import frappe
from frappe.utils import formatdate, getdate, date_diff

@frappe.whitelist()
def get_report(from_date=None,to_date=None):
    data = {}
    punit=frappe.db.sql(""" select name,contract_start_date,contract_end_date from `tabProperty Unit` where company='AL NOKHBA BUILDING' 
        and property_name='AL NOKHBA BUILDING' order by cast(unit_no as unsigned)""",as_dict=1,debug=0)
    data['from_date']=getdate(from_date).strftime('%d/%m/%Y')
    data['to_date']=getdate(to_date).strftime('%d/%m/%Y')
    endday=frappe.utils.getdate(to_date)
    dfrm=frappe.utils.getdate(from_date)
    data['cnt']=date_diff(endday,dfrm)+1
    datelist=frappe.utils.add_days(dfrm, -1)
    html='<tr style="position: sticky; top: 0px; background-color: #ccc;"><td style="width:190px;"></td>'
    while datelist < endday:
        datelist=frappe.utils.add_days(datelist,1)
        html+='<td >'+datelist.strftime('%d/%m')+'</td>'
    html+='</tr>'
    for unit in punit:
        html+='<tr><td style="width:190px;">'+unit.name+'</td>'
        booking=[]
        order=frappe.db.sql(""" select contract_start_date,contract_end_date from `tabSales Order` where company='AL NOKHBA BUILDING' 
        and property='AL NOKHBA BUILDING' and property_unit='{0}' and docstatus=1 
        and ((contract_start_date between '{1}' and '{2}') or (contract_end_date between '{1}' and '{2}')) """.format(unit.name,from_date,to_date),as_dict=1,debug=0)
        for ord in order:
            cdate=frappe.utils.add_days(getdate(ord.contract_start_date), -1)            
            while cdate < ord.contract_end_date:
                cdate=frappe.utils.add_days(cdate,1)
                booking.append(cdate)

        invoice=frappe.db.sql(""" select contract_start_date,contract_end_date from `tabSales Invoice` where company='AL NOKHBA BUILDING' 
        and property='AL NOKHBA BUILDING' and property_unit='{0}' and docstatus=1 
        and ((contract_start_date between '{1}' and '{2}') or (contract_end_date between '{1}' and '{2}')) """.format(unit.name,from_date,to_date),as_dict=1,debug=0)
        for ord in invoice:
            cdate=frappe.utils.add_days(getdate(ord.contract_start_date), -1)            
            while cdate < ord.contract_end_date:
                cdate=frappe.utils.add_days(getdate(cdate),1)
                booking.append(cdate)

        datelist=frappe.utils.add_days(dfrm, -1)
        while datelist < endday:
            datelist=frappe.utils.add_days(datelist,1)
            if datelist in booking:
                html+='<td class="occu">x</td>'
            else:
                html+='<td></td>'    
        html+='</tr>'

    data['items']=html
    return data

       
    

    
    