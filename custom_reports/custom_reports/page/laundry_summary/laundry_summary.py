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
   
    data['items']=frappe.db.sql("""select ad.address_title,sum(si.total_qty) as total_qty,sum(si.total) as total,sum(si.total_taxes_and_charges) as total_taxes,sum(si.grand_total) as  grand_total from `tabSales Invoice` si left join `tabAddress` ad on ad.name=si.customer_address where si.company='Quick Laundry – Sole Proprietorship LLC' and ad.address_title in ('F & B LINEN','F&B LINEN', 'GUEST LAUNDRY', 'ROOM LINEN', 'RECREATION LINEN', 'STAFF UNIFORM', 'MANAGEMENT LAUNDRY','ADMINISTRATION STAFF') and si.docstatus=1 and si.customer='{0}' and (si.posting_date between '{1}' and '{2}') group by ad.address_title """.format(customer,from_date,to_date),as_dict=1,debug=1)

    data['items_total']=frappe.db.sql("""select sum(si.total_qty) as total_qty,sum(si.total) as total,sum(si.total_taxes_and_charges) as total_taxes,sum(si.grand_total) as  grand_total from `tabSales Invoice` si left join `tabAddress` ad on ad.name=si.customer_address where si.company='Quick Laundry – Sole Proprietorship LLC' and ad.address_title in ('F & B LINEN','F&B LINEN', 'GUEST LAUNDRY', 'ROOM LINEN', 'RECREATION LINEN', 'STAFF UNIFORM', 'MANAGEMENT LAUNDRY','ADMINISTRATION STAFF') and si.docstatus=1 and si.customer='{0}' and (si.posting_date between '{1}' and '{2}') group by si.customer """.format(customer,from_date,to_date),as_dict=1,debug=0)
    

    return data

       
    

    
    