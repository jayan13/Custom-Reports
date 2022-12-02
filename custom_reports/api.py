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

	out=frappe.db.get_list('Sales Invoice',
    fields=['sum(outstanding_amount) as outstanding_amount'],
	filters={'docstatus':1,'company':company,'customer':customer,'outstanding_amount':['>',0]},
    group_by='customer')
	if out:
		outsta=out[0].outstanding_amount
	return outsta


@frappe.whitelist()
def customer_overdue(company,customer):
	overdue=0
	
	payment_terms = frappe.db.get_value('Customer', {'name':customer}, ['payment_terms'])
	if payment_terms:
		import re		
		
		payment_terms=re.findall('\d+', payment_terms)
		
		values = {'company': company,'customer':customer,'payment_terms':payment_terms}
		over = frappe.db.sql("""
			SELECT DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL %(payment_terms)s DAY)) as overdu from `tabSales Invoice` where docstatus = 1 and company=%(company)s and customer=%(customer)s and outstanding_amount <> 0 and DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL %(payment_terms)s DAY)) >0 order by posting_date limit 0,1
		""", values=values, as_dict=1,debug=0)
		if over:
			overdue=over[0].overdu
	return overdue

@frappe.whitelist()
def customer_credit(company,customer):
	overdue=0   	
	overdue=frappe.db.get_value('Customer Credit Limit', {'company':company,'parent':customer}, ['credit_limit'])
	return overdue or 0

@frappe.whitelist()
def update_cost_acc(doc,event):
	
	item=['TELWA-330ML - 12 PACK','TELWA-330ML - 16 PACK','TELWA-600ML - 12 PACK','TELWA-600ML - 20 PACK','TELWA-600ML - 20 PCS - CTN','TELWA-1.5 L - 6 PACK','TELWA-1.5 L - 6 PCS - CTN','TELWA-NEW GALLON','TELWA-RE-FILLING GALLON']
	acc=['513101 - COGS .330 Ltrs - TELWA','513101 - COGS .330 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513103 - COGS 1.5 Ltrs - TELWA','513103 - COGS 1.5 Ltrs - TELWA','513201 - COGS 20 Ltrs Bottle - TELWA','513202 - COGS 20 Ltrs Refill - TELWA']
	if doc.company=='Nigerienne De Reffraichissement Telwa – Socite a Resposabilite Limitee.':
		for itm in doc.items:
			if itm.item_code in item and itm.expense_account=='':
				index = item.index(itm.item_code)
				itm.expense_account=acc[index]


