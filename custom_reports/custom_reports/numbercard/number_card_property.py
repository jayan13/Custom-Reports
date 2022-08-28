# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate

import erpnext

@frappe.whitelist()
def vacant_units():
	carddata = {}
	to_date = frappe.utils.today()
	rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where unit_status='Vacant' or unit_status='Vacant - Legal'
		""",
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	return carddata

@frappe.whitelist()
def occupied_units():
	carddata = {}
	to_date = frappe.utils.today()
	rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where unit_status='Occupied' or unit_status='Occupied - Legal' """,
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def this_month_renewal():
	carddata = {}
	to_date = frappe.utils.today()
	#fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	#first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select count(*) as cnt from `tabProperty Unit` where MONTH('%s')= MONTH(contract_end_date) """%(to_date),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def sales_revenue_tyd():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(base_net_total) as amt
                        from `tabSales Invoice` where company in ('Bin Butti International Real Estate Management – Unincorporated','AL NOKHBA BUILDING') and docstatus=1 and posting_date>= '%s' """%(first_day_year),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata
