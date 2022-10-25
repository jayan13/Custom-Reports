import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_customer_list():
    data = {}
    data["customers"] = frappe.get_list("Customer", filters={ 'customer_group': 'Quick Laundry'},fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data
    
@frappe.whitelist()
def get_report(from_date=None,to_date=None):
    data = {}
        
    
    data['from_date']=getdate(from_date).strftime('%d/%m/%Y')
    data['to_date']=getdate(to_date).strftime('%d/%m/%Y')
    
    data['head']=frappe.db.get_value('Letter Head', 'Dure Oil Letter Head', 'content')
    manu=[]
    stkentry=frappe.db.sql(""" select p.name as process_order,s.name,s.posting_date from `tabStock Entry` s 
left join `tabProcess Order` p on s.process_order=p.name 
where s.process_order!='' and s.docstatus<2 and p.process_type='Waste Oil Re-refining' and s.stock_entry_type='Manufacture'
and s.posting_date between '{0}' and '{1}' order by s.posting_date""".format(from_date,to_date),as_dict=1,debug=0)
    for stk in stkentry:
        itm=frappe.db.sql(""" select item_code,qty,uom,amount from `tabStock Entry Detail` 
        where parent='{0}' ORDER BY FIELD(item_code, 'WO001', 'LLB001','LI0001','AS0001','WT1-WATER') """.format(stk.name),as_dict=1,debug=0)
        wt=0
        prd=0
        recovery=0
        for it in itm:
            if it.item_code=='WO001':
                wt=it.qty
            if it.item_code not in ['WO001']:
                prd+=it.qty

        
        recovery=round((prd/wt)*100)
        manu.append({'date':stk.posting_date,'items':itm,'recovery':recovery})
    
    data['items']=manu
    
    data['items_total']=frappe.db.sql(""" select sd.item_code,sum(qty) as qty,sum(amount) as amount from `tabStock Entry` s left join `tabStock Entry Detail` sd on s.name=sd.parent 
left join `tabProcess Order` p on s.process_order=p.name 
where s.process_order!='' and s.docstatus<2 and p.process_type='Waste Oil Re-refining' and s.stock_entry_type='Manufacture'
AND s.posting_date between '{0}' and '{1}' group by sd.item_code ORDER BY FIELD(sd.item_code, 'WO001', 'LLB001','LI0001','AS0001','WT1-WATER') """.format(from_date,to_date),as_dict=1,debug=0)
    

    return data

       
    

    
    