import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_report():
    data = {}    
    
    frappe.db.sql(""" set @rownum := 0 """)
    data['items']=frappe.db.sql("""select @rownum := @rownum + 1 as row_number,name,customer_name,DATE_FORMAT(contract_start_date,'%d/%m/%Y') as contract_start_date,DATE_FORMAT(contract_end_date,'%d/%m/%Y') as contract_end_date,unit_status from `tabProperty Unit` where MONTH(contract_end_date)=MONTH(CURRENT_DATE()) AND YEAR(contract_end_date)=YEAR(CURRENT_DATE()) and property_name='Villas'""",as_dict=1,debug=0)
    return data

       
    

    
    