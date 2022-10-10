import frappe
from frappe.utils import formatdate, getdate

@frappe.whitelist()
def get_report():
    data = {}    
    
    frappe.db.sql(""" set @rownum := 0 """)
    data['comments']=frappe.db.sql("""select @rownum := @rownum + 1 as row_number,name,subject,for_user,from_user,REPLACE(LOWER(document_type), ' ', '-') as document_type,document_name,email_content,type,`read`,DATE_FORMAT(creation,'%d/%m/%Y') as creation from `tabNotification Log` where `read`=0 and for_user='{0}' order by creation desc""".format(frappe.session.user),as_dict=1,debug=0)
    return data

 
    

    
    