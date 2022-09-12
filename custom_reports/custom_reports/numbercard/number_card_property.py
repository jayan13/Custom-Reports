# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate

import erpnext

@frappe.whitelist()
def total_units(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where  property_name like '%Musaffah Plot%'
		""",
		as_dict=1,debug=0
	)
	else:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where  property_name='{0}'
		""".format(card_name),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	return carddata

@frappe.whitelist()
def vacant_units(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()	
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where (unit_status='Vacant' or unit_status='Vacant - Legal')
		 and property_name like '%Musaffah Plot%'
		""",
		as_dict=1,debug=0
	)
	else:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where (unit_status='Vacant' or unit_status='Vacant - Legal') 
		and property_name='{0}'
		""".format(card_name),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	return carddata

@frappe.whitelist()
def occupied_units(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()
	
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where (unit_status='Occupied' or unit_status='Occupied - Legal')
		 and property_name like '%Musaffah Plot%'
		""",
		as_dict=1,debug=0
	)
	else:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where (unit_status='Occupied' or unit_status='Occupied - Legal')
		and property_name='{0}'
		""".format(card_name),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def this_month_renewal(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()
	#fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	#first_day_year=fromdate.replace(month=1, day=1)
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where MONTH('{0}')= MONTH(contract_end_date) and YEAR('{0}')= YEAR(contract_end_date) and property_name like '%Musaffah Plot%'
		""".format(to_date),as_dict=1,debug=0)
	
	else:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where  property_name='{0}' YEAR('{0}')= YEAR(contract_end_date) and and MONTH('{1}')= MONTH(contract_end_date)
		""".format(card_name,to_date),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def next_month_renewal(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()
	#fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	#first_day_year=fromdate.replace(month=1, day=1)
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where MONTH(DATE_ADD('{0}', INTERVAL 1 MONTH))= MONTH(contract_end_date) and YEAR(DATE_ADD('{0}', INTERVAL 1 MONTH))= YEAR(contract_end_date) and property_name like '%Musaffah Plot%'
		""".format(to_date),as_dict=1,debug=0)
	
	else:
		rate=frappe.db.sql(
		"""
		select count(*) as cnt from `tabProperty Unit` where  property_name='{0}' and MONTH(DATE_ADD('{1}', INTERVAL 1 MONTH))= MONTH(contract_end_date) and YEAR(DATE_ADD('{1}', INTERVAL 1 MONTH))= YEAR(contract_end_date)
		""".format(card_name,to_date),
		as_dict=1,debug=0
	)
	
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['cnt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def sales_revenue_tyd(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	first_day_year=fromdate.replace(month=1, day=1)
	if 'Musaffah Plot' in card_name:
		rate=frappe.db.sql(
		"""	select sum(base_net_total) as amt
                        from `tabSales Invoice` where property_unit in (select name from `tabProperty Unit` where  property_name like '%Musaffah Plot%') and docstatus=1 and is_return=0 and is_opening='No' and posting_date>= '%s' """%(first_day_year),
		as_dict=1,debug=0
	)
	else:
		rate=frappe.db.sql(
		"""	select sum(base_net_total) as amt
                        from `tabSales Invoice` where property_unit in (select name from `tabProperty Unit` where  property_name='%s') and docstatus=1 and is_return=0 and is_opening='No' and posting_date>= '%s' """%(card_name,first_day_year),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def total_sales_revenue_tyd():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(base_net_total) as amt
                        from `tabSales Invoice` where company ='Bin Butti International Real Estate Management – Unincorporated' and docstatus=1 and is_return=0 and is_opening='No' and posting_date>= '%s' """%(first_day_year),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def total_pdc_tyd():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(amount) as amt from `tabReceivable Cheques` where cheque_status='Cheque Received' and company ='Bin Butti International Real Estate Management – Unincorporated'  """,
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def total_pdcreal_tyd():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	#first_day_month=fromdate.replace(day=1)	
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(amount) as amt from `tabReceivable Cheques` where cheque_status='Cheque Realized' and company ='Bin Butti International Real Estate Management – Unincorporated' and DATE(cheque_date)>= '%s' """%(first_day_year),
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata