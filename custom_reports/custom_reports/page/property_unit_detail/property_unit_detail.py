import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_report(unit_name):
    data = {'unit_name':unit_name}    
    unit_details=frappe.db.get_value('Property Unit',unit_name,['name','property_name','company','unit_status','customer_name','contract_start_date','contract_end_date','security_deposit','annual_rent'],as_dict=1)
    unit_details.contract_start_date=formatdate(unit_details.contract_start_date, "dd-MM-yyyy")
    unit_details.contract_end_date=formatdate(unit_details.contract_end_date, "dd-MM-yyyy")
    data.update({'unit_details':unit_details})
    start=unit_details.contract_start_date
    prevord=frappe.db.sql("select * from `tabSales Invoice` where property_unit='{0}' and docstatus=1 and contract_end_date<='{1}' order by contract_end_date desc limit 0,1".format(unit_name,start),as_dict=1,debug=0)
    
    if prevord:
        data.update({'prebook':prevord[0]})
    else:
        data.update({'prebook':''})

    maintance=[]
    tot=0
    maint=frappe.db.sql("select * from `tabProperty Maintenance` where docstatus=1 and ((propperty_unit='{0}' and  property='{1}') or (propperty_unit='' and  property='{1}')) and YEAR(start_date)=YEAR(CURDATE()) order by start_date desc limit 0,1".format(unit_details.name,unit_details.property_name),as_dict=1,debug=0)
    for mt in maint:
        mtd={}
        mname='<a href="'+frappe.utils.get_url()+'/app/property-maintenance/'+mt.name+'" target="_blank">'+mt.name+'</a>'
        mtd.update({'name':mname})
        mtd.update({'desc':mt.note})
        mtd.update({'start_date':mt.start_date})
        mtd.update({'end_date':mt.end_date})
        mtd.update({'estimated_costing':mt.estimated_costing})
        actual_costing=0

        actp=frappe.db.sql(""" select sum(total) as total from `tabPurchase Invoice` where property_maintenance='{0}' group by property_maintenance """.format(mt.name),as_dict=1)
        if actp:
            actual_costing+=actp[0].total

        actj=frappe.db.sql(""" select sum(total_credit) as total from `tabJournal Entry` where property_maintenance='{0}' group by property_maintenance """.format(mt.name),as_dict=1)
        if actj:
            actual_costing+=actj[0].total

        #actj=frappe.db.sql(""" select sum(total_credit) as total from `tabJournal Entry` j jeft join `Journal Entry Account` a on j.name=a.parent where j.property_maintenance='{0}'  """.format(mt.cost_center),as_dict=1)
        
        mtd.update({'actual_costing':actual_costing})
        maintance.append(mtd)
        tot+=actual_costing

    data.update({'maintance':maintance})
    data.update({'totmain':tot})
    return data

       
    

    
    