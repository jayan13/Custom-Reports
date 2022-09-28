import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_customer_list():
    data = {}
    data["customers"] = frappe.get_list("Customer", filters={ 'customer_group': 'Quick Laundry'},fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data
    
@frappe.whitelist()
def get_report(customer=None,from_date=None,to_date=None):
    data = {}
        
    data['customer']=customer
    data['from_date']=getdate(from_date).strftime('%d/%m/%Y')
    data['to_date']=getdate(to_date).strftime('%d/%m/%Y')
    data['trn']=frappe.db.get_value("Customer", customer,"tax_id") or ""
    data['head']=frappe.db.get_value('Letter Head', 'Quick Laundry Letter Head', 'content')
   
    data['items']=frappe.db.sql("""select si.po_no,si.name,DATE_FORMAT(si.posting_date,'%d/%m/%Y') AS posting_date,si.total_qty,si.total,si.total_taxes_and_charges,si.grand_total,(select parent from `tabSales Invoice Item` sitm where si.name=sitm.delivery_note limit 0,1) as salinv from `tabDelivery Note` si left join `tabAddress` ad on ad.name=si.customer_address where si.company='Quick Laundry – Sole Proprietorship LLC' and si.docstatus=1 and si.customer='{0}' and (si.posting_date between '{1}' and '{2}')  order by si.posting_date""".format(customer,from_date,to_date),as_dict=1,debug=0)

    data['items_total']=frappe.db.sql("""select sum(si.total_qty) as total_qty,sum(si.total) as total,sum(si.total_taxes_and_charges) as total_taxes,sum(si.grand_total) as  grand_total from `tabDelivery Note` si left join `tabAddress` ad on ad.name=si.customer_address where si.company='Quick Laundry – Sole Proprietorship LLC' and si.docstatus=1 and si.customer='{0}' and (si.posting_date between '{1}' and '{2}') group by si.customer """.format(customer,from_date,to_date),as_dict=1,debug=0)
    

    return data

       
    

    
    