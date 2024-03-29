import frappe
from frappe.utils import getdate,add_days,get_first_day,get_last_day,nowdate,flt,date_diff
@frappe.whitelist()
def get_company_list():
    data = {}
    data["companys"] = frappe.get_list("Company", fields=['name'],limit_page_length=0, order_by="name",debug=0)
    return data


@frappe.whitelist()
def get_report(company):
    html=''
    sett=frappe.db.get_value('Material And Pro Req  Settlement Dashboard Settings',{'company':company},['iou_cash_account','casier_account','casier_account_no','casier_account_pro','casier_account_no_pro','iou_cash_account_no','approved_status','bill_settled_status','approved_status_pro','bill_settled_status_pro'],as_dict=1)
    if sett:
        cash_acc=sett.casier_account
        iou_cash_acc=sett.iou_cash_account
        cash_acc_pro=sett.casier_account_pro
    else:
        sett=frappe.db.get_value('Material And Pro Req  Settlement Dashboard Settings',{'company':''},['iou_cash_account','casier_account','casier_account_no','casier_account_pro','casier_account_no_pro','iou_cash_account_no','approved_status','bill_settled_status','approved_status_pro','bill_settled_status_pro'],as_dict=1)
        if sett:
            cash_acc=frappe.db.get_value('Account',{'company':company,'account_number':sett.casier_account_no},['name'])
            cash_acc_pro=frappe.db.get_value('Account',{'company':company,'account_number':sett.casier_account_no_pro},['name'])
            iou_cash_acc=frappe.db.get_value('Account',{'company':company,'account_number':sett.iou_cash_account_no},['name'])
        else:
            frappe.throw("Please add settings in - Material And Pro Req  Settlement Dashboard Settings ")
        

    approved=sett.approved_status
    billed=sett.bill_settled_status
    approvedpro=sett.approved_status_pro
    billedpro=sett.bill_settled_status_pro
    tot_cash=0
    html+='<table class="table table-bordered" >'
    html+='<tr class="table-secondary"><th colspan="2">UNSETTLED CASH BALANCE</th><th>BALANCE AMOUNT</th></tr>'

    cash_amt=0
    cash_sql=frappe.db.sql(""" select IFNULL(sum(debit)-sum(credit), 0) as amt from `tabGL Entry` where docstatus=1 and account='{0}' and company='{1}' """.format(cash_acc,company),as_dict=1)
    if cash_sql:
        cash_amt=cash_sql[0].amt
        tot_cash+=float(cash_amt)
        cash_amt=frappe.utils.fmt_money(cash_amt)
    html+='<tr><td colspan="2">CASH BALANCE WITH CASHIER - Material Req</td> <td class="text-right">'+str(cash_amt)+'</td></tr>'
    cash_amt_pro=0
    cash_pro_sql=frappe.db.sql(""" select IFNULL(sum(debit)-sum(credit), 0) as amt from `tabGL Entry` where docstatus=1 and account='{0}' and company='{1}' """.format(cash_acc_pro,company),as_dict=1)
    if cash_pro_sql:
        cash_amt_pro=cash_pro_sql[0].amt
        tot_cash+=float(cash_amt_pro)
    cash_amt_pro=frappe.utils.fmt_money(cash_amt_pro)    
    html+='<tr><td colspan="2">CASH BALANCE WITH CASHIER - PRO Req</td> <td class="text-right">'+str(cash_amt_pro)+'</td></tr>'

    iou_employee=frappe.db.sql(""" select IFNULL(sum(debit)-sum(credit), 0) as amt,party from `tabGL Entry` where docstatus=1 and party_type='Employee' and account='{0}' and company='{1}' group by party""".format(iou_cash_acc,company),as_dict=1)
    
    if iou_employee:
        
        for emp in iou_employee:
            tot_cash+=float(emp.amt)
            amt=frappe.utils.fmt_money(emp.amt)
            empname=frappe.db.get_value('Employee',emp.party,'employee_name')
            html+='<tr><td colspan="2">IOU Balance - '+str(empname)+'</td> <td class="text-right">'+str(amt)+'</td></tr>'
    
    tot_cash=frappe.utils.fmt_money(tot_cash)
    html+='<tr class="table-secondary"><td colspan="2"><b>TOTAL CASH BALANCE</b></td> <td class="text-right">'+str(tot_cash)+'</td></tr>'
    html+='<tr ><td><b>&nbsp;</b></td> <td class="text-right"></td><td></td></tr>'
    html+='<tr class="table-secondary"><th>MATERIAL REQUEST</th> <th>Count</th> <th>Total Amount</th> </tr>'
    totsettle=0
    settled_amt=0
    settled_cnt=0
    settled=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabMaterial Request` where docstatus=1 and workflow_state!='Cash Issued' and workflow_state!='{0}' and workflow_state!='{1}' and company='{2}' """.format(billed,approved,company),as_dict=1)
    if settled:
        settled_amt=settled[0].amount
        settled_cnt=settled[0].cnt
        totsettle+=float(settled[0].amount)

    issued_amt=0
    issued_cnt=0
    issued=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabMaterial Request` where docstatus=1 and workflow_state='Cash Issued' and company='{0}' """.format(company),as_dict=1)
    if issued:
        issued_amt=issued[0].amount
        issued_cnt=issued[0].cnt
        totsettle+=float(issued[0].amount)

    unsettled_amt=0
    unsettled_cnt=0
    unsettled=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabMaterial Request` where docstatus=1 and  workflow_state='{0}' and company='{1}' """.format(approved,company),as_dict=1)
    if unsettled:
        unsettled_amt=unsettled[0].amount
        unsettled_cnt=unsettled[0].cnt
        totsettle+=float(unsettled[0].amount)

    settled_amt=frappe.utils.fmt_money(settled_amt)
    issued_amt=frappe.utils.fmt_money(issued_amt)
    unsettled_amt=frappe.utils.fmt_money(unsettled_amt)
    
    html+='<tr><td>Material Requests in Settlemet Process</td> <td class="text-right">'+str(settled_cnt)+'</td><td class="text-right">'+str(settled_amt)+'</td></tr>'
    html+='<tr><td>Unsettled Cash Issued Material Requests</td> <td class="text-right">'+str(issued_cnt)+'</td><td class="text-right">'+str(issued_amt)+'</td></tr>'
    html+='<tr><td>Unsettled Material Requests</td> <td class="text-right">'+str(unsettled_cnt)+'</td><td class="text-right">'+str(unsettled_amt)+'</td></tr>'

    html+='<tr class="table-secondary"><th>PRO EXPENSE REQUEST</th> <th>Count</th> <th>Total Amount</th> </tr>'
    settled_amt=0
    settled_cnt=0
    settled=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabPRO Expense Request` where docstatus=1 and workflow_state!='Paid' and workflow_state!='Cash Issued' and workflow_state!='{0}' and workflow_state!='{1}' and company='{2}' """.format(billedpro,approvedpro,company),as_dict=1)
    if settled:
        settled_amt=settled[0].amount
        settled_cnt=settled[0].cnt
        totsettle+=float(settled[0].amount)
    
    issued_amt=0
    issued_cnt=0
    issued=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabPRO Expense Request` where docstatus=1 and workflow_state='Cash Issued' and company='{0}' """.format(company),as_dict=1)
    if issued:
        issued_amt=issued[0].amount
        issued_cnt=issued[0].cnt
        totsettle+=float(issued[0].amount)

    unsettled_amt=0
    unsettled_cnt=0
    unsettled=frappe.db.sql(""" select count(total) as cnt,IFNULL(sum(total), 0) as amount from `tabPRO Expense Request` where docstatus=1 and workflow_state='{0}' and company='{1}' """.format(approvedpro,company),as_dict=1)
    if unsettled:
        unsettled_amt=unsettled[0].amount
        unsettled_cnt=unsettled[0].cnt
        totsettle+=float(unsettled[0].amount)

    settled_amt=frappe.utils.fmt_money(settled_amt)
    issued_amt=frappe.utils.fmt_money(issued_amt)
    unsettled_amt=frappe.utils.fmt_money(unsettled_amt)
    totsettle=frappe.utils.fmt_money(totsettle)
    html+='<tr><td>PRO Requests in Settlemet Process</td> <td class="text-right">'+str(settled_cnt)+'</td><td class="text-right">'+str(settled_amt)+'</td></tr>'
    html+='<tr><td>Unsettled Cash Issued PRO Requests</td> <td class="text-right">'+str(issued_cnt)+'</td><td class="text-right">'+str(issued_amt)+'</td></tr>'
    html+='<tr><td>Unsettled PRO Requests</td> <td class="text-right">'+str(unsettled_cnt)+'</td><td class="text-right">'+str(unsettled_amt)+'</td></tr>'

    html+='<tr class="table-secondary"><td><b>Total (PRO + MATERIAL REQ)</b></td> <td class="text-right"></td><td class="text-right"><b>'+str(totsettle)+'</b></td></tr>'
    
    
    html+='</table>'
    return html


    
    