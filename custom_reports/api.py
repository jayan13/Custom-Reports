# -*- coding: utf-8 -*-
# Copyright (c) 2017, Direction and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate
from frappe import throw, msgprint, _


@frappe.whitelist()
def validate_expense(exp_year,exp_date,employee):

	emprv=frappe.db.sql(""" select * from `tabExpense Request Item` where docstatus=1 and employee='{0}' and date between DATE_SUB('{2}', INTERVAL {1} YEAR) and '{2}' """.format(employee,exp_year,exp_date),as_dict=1,debug=0)

	if emprv:
		return 1
	else:
		return 0
	
@frappe.whitelist()
def maintanse_items(sub_gp):
	return frappe.db.sql(""" select sub_group_items from `tabAsset Sub Group Items` where parent='{0}' """.format(sub_gp),as_dict=1,debug=0)

@frappe.whitelist()
def customer_outstanding(company,customer):
	outsta=0
	out=frappe.db.sql(""" select sum(outstanding_amount) as outstanding_amount 
from `tabSales Invoice` where docstatus = 1 and company='{0}' and customer='{1}'
and outstanding_amount <> 0 group by customer""".format(company,customer),as_dict=1,debug=0)
	if out:
		outsta=out[0].outstanding_amount
	return outsta

@frappe.whitelist()
def customer_overdue(company,customer):
	overdue=0
	payment_terms = frappe.db.get_value('Customer', {'name':customer}, ['payment_terms'])
	if payment_terms:
		payment_terms=payment_terms.upper()
		payment_terms=payment_terms.rstrip('S')	
		sql=""" select DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL {2})) as overdu
	from `tabSales Invoice` where docstatus = 1 and company='{0}' and customer='{1}'
	and outstanding_amount <> 0 and DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL {2})) >0 
	order by posting_date limit 0,1 """.format(company,customer,payment_terms)
		
		over=frappe.db.sql(sql,as_dict=1,debug=0)
		if over:
			overdue=over[0].overdu
	return overdue

@frappe.whitelist()
def customer_credit(company,customer):
	overdue=0   
	over=frappe.db.sql(""" select credit_limit 
	from `tabCustomer Credit Limit` where company='{0}' and parent='{1}' """.format(company,customer),as_dict=1,debug=0)
	if over:
		overdue=over[0].credit_limit
	return overdue



