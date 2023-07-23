import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_report():
    data = {}    
    
    frappe.db.sql(""" set @rownum := 0 """)
    data['items']=frappe.db.sql("""select @rownum := @rownum + 1 as row_number,name,customer_name,DATE_FORMAT(contract_start_date,'%d/%m/%Y') as contract_start_date,DATE_FORMAT(contract_end_date,'%d/%m/%Y') as contract_end_date,unit_status from `tabProperty Unit` where MONTH(DATE_SUB(contract_end_date,INTERVAL 1 MONTH))=MONTH(CURRENT_DATE()) AND YEAR(DATE_SUB(contract_end_date,INTERVAL 1 MONTH))=YEAR(CURRENT_DATE()) and property_name='Musaffah Plot - MZE19-144'""",as_dict=1,debug=0)
    for itm in data['items']:
        itm.name='<a href="'+frappe.utils.get_url()+'/app/property-unit-detail/'+itm.name+'" onclick="frappe.ui.toolbar.clear_cache()" target="_blank">'+itm.name+'</a>'
    
    return data

       
    

    
    