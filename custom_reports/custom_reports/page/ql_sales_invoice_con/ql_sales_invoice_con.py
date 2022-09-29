import frappe
from frappe.utils import formatdate, getdate, flt

@frappe.whitelist()
def get_customer_list():
    data = {}
    data["customers"] = frappe.get_list("Customer", filters={ 'customer_group': 'Quick Laundry'},fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data

@frappe.whitelist()
def get_invoice_list(customer):
    data = {}
    data["invoices"] = frappe.get_list("Sales Invoice", filters={ 'customer': customer,'company':'Quick Laundry – Sole Proprietorship LLC'},fields=['name'],limit_page_length=0, order_by="posting_date desc",debug=0)
    return data
    
@frappe.whitelist()
def get_report(customer=None,sales_invoice=None):
    data = {}
        
    data['customer']=customer
    data['sales_invoice']=sales_invoice    
    data['trn']=frappe.db.get_value("Customer", customer,"tax_id") or ""
    data['head']=frappe.db.get_value('Letter Head', 'Quick Laundry Letter Head', 'content')
    inv=frappe.get_doc("Sales Invoice",sales_invoice)
    inv.posting_date=inv.posting_date.strftime('%d-%m-%Y')
    inv.in_words=frappe.utils.money_in_words(inv.base_grand_total)
   
    data['total']=frappe.utils.fmt_money(inv.total)
    data['total_taxes_and_charges']=frappe.utils.fmt_money(inv.total_taxes_and_charges)
    data['grand_total']=frappe.utils.fmt_money(inv.grand_total)
   
    data['invoice']=inv
    frappe.db.sql(""" SET @idx=0 """)
    item=frappe.db.sql(""" select @idx:=@idx+1 AS idxs,ad.address_title,sum(si.qty) as qty,sum(ROUND(si.amount, 2)) as amount,si.tax_rate as tax_rate,sum(si.tax_amount) as tax_amount,sum(si.total_amount) as total_amount from `tabSales Invoice Item` si left join `tabDelivery Note` dn on dn.name=si.delivery_note left join `tabAddress` ad on ad.name=dn.customer_address where ad.address_title in ('F & B LINEN','F&B LINEN', 'GUEST LAUNDRY', 'ROOM LINEN', 'RECREATION LINEN', 'STAFF UNIFORM', 'MANAGEMENT LAUNDRY','ADMINISTRATION STAFF') and si.parent='{0}' group by ad.address_title order by idxs""".format(sales_invoice),as_dict=1,debug=0)   
    it=[]
    for itm in item:
        amount=flt(itm.amount,2)
        itm.amount=frappe.utils.fmt_money(amount)
        tax_amount=flt(amount*(itm.tax_rate/100))
        itm.tax_amount=frappe.utils.fmt_money(tax_amount)
        itm.total_amount=frappe.utils.fmt_money(amount+tax_amount)
        it.append(itm)

    data['items']=it

    return data

       
    

    
    