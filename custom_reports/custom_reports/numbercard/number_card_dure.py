# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from distutils.log import debug
from operator import itemgetter

import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate
from six import iteritems

import erpnext
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition
#from erpnext.stock.utils import is_reposting_item_valuation_in_progress 

@frappe.whitelist()
def last_wo_purchase():
	carddata = {}
	rate=frappe.db.sql(
		"""
		select incoming_rate from `tabStock Ledger Entry` where docstatus < 2 and is_cancelled = 0 and item_code='wo001' and company='Dure Oil Middle East Factory - Sole Proprietorship LLC' and voucher_type='Purchase Receipt'
		order by posting_date desc limit 0,1 """,
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['incoming_rate'] or 0
	carddata['fieldtype']='Float'
	return carddata

@frappe.whitelist()
def last_PLO_sold():
	carddata = {}
	rate=frappe.db.sql(
		"""
		select rate from `tabSales Invoice Item` 
		where docstatus = 1  and item_code='LLB001' 
		order by creation desc limit 0,1 """,
		as_dict=1,debug=0
	)
	carddata['value']=0
	if rate:
		carddata['value']=rate[0]['rate'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def hbo_vhbo_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('VHBO101','HBO101') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_month,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def ytd_hbo_vhbo_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('VHBO101','HBO101') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_year,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def ytd_asphault_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('AS0001') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_year,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def mtd_asphault_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('AS0001') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_month,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def ytd_asphault_1_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('AS0002') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_year,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def mtd_asphault_1_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('AS0002') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No'  """%(first_day_month,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def lpo_m_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('LLB001') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No' """%(first_day_month,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def lpo_y_sales():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(itm.amount) as sales from `tabSales Invoice Item` itm left join `tabSales Invoice` inv on inv.name = itm.parent where itm.item_code in ('LLB001') 
		and inv.posting_date>= '%s' and inv.posting_date<='%s' and inv.docstatus=1 and inv.is_opening='No' """%(first_day_year,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['sales'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def other_income():
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	rate=frappe.db.sql(
		"""	select sum(credit-debit) as amt from `tabGL Entry` where account='420100 - Other Income - DURE' and voucher_type='Journal Entry' and posting_date>='%s' and posting_date<='%s' """%(first_day_year,to_date),
		as_dict=1,debug=0
	)[0]
	carddata['value']=0
	if rate:
		carddata['value']=rate['amt'] or 0
	carddata['fieldtype']='Float'
	
	return carddata

@frappe.whitelist()
def total_sales(filters=None):
	import json
	card = json.loads(filters)
	card_name=card.get('card_name')
	carddata={}
	card = json.loads(filters)
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	if card_name=='YTD Sales Revenue':
		rate=frappe.db.sql(
			"""select sum(total) as val from `tabSales Invoice` where 
			company='Dure Oil Middle East Factory - Sole Proprietorship LLC' 
			and posting_date >= '%s' and posting_date <= '%s' and is_opening='No' and docstatus=1 """%(first_day_year,to_date),
			as_dict=1,debug=0
		)[0]

	if card_name=='MTD Sales Revenue':
		rate=frappe.db.sql(
			"""select sum(total) as val from `tabSales Invoice` where 
			company='Dure Oil Middle East Factory - Sole Proprietorship LLC' 
			and posting_date >= '%s' and posting_date <= '%s' and is_opening='No' and docstatus=1 """%(first_day_month,to_date),
			as_dict=1,debug=0
		)[0]

	if card_name=='YTD Sales In Tons':
		rate=frappe.db.sql(
			"""select sum(total_qty)/1000 as val from `tabSales Invoice` where 
			company='Dure Oil Middle East Factory - Sole Proprietorship LLC' 
			and posting_date >= '%s' and posting_date <= '%s' and is_opening='No' and docstatus=1"""%(first_day_year,to_date),
			as_dict=1,debug=0
		)[0]

	if card_name=='MTD Sales In Tons':
		rate=frappe.db.sql(
			"""select sum(total_qty)/1000 as val from `tabSales Invoice` where 
			company='Dure Oil Middle East Factory - Sole Proprietorship LLC' 
			and posting_date >= '%s' and posting_date <= '%s' and is_opening='No' and docstatus=1 """%(first_day_month,to_date),
			as_dict=1,debug=0
		)[0]

	carddata['fieldtype']='Float'
	carddata['value']=0
	if rate:
		carddata['value']=rate['val'] or 0
	return carddata

@frappe.whitelist()
def last_wo_purchase_trade():
	carddata = {}
	rate=frappe.db.sql(
		"""
		select	incoming_rate from 	`tabStock Ledger Entry` 
		where docstatus < 2 and is_cancelled = 0 and item_code='wo005' and company='Dure Oil Middle East Factory - Sole Proprietorship LLC' and voucher_type='Purchase Receipt'
		order by posting_date desc limit 0,1 """,
		as_dict=1,debug=0
	)

	carddata['fieldtype']='Float'
	carddata['value']=rate[0]['incoming_rate']
	return carddata

@frappe.whitelist()
def get_card(filters=None):
	import json
	carddata={}
	card = json.loads(filters)
	card_name=card.get('card_name')
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	field=''

	if 'Opening' in card_name:
		field='opening_qty'
	elif 'Collection' in card_name:
		field='in_qty'
	elif 'Issued' in card_name:
		field='out_qty'
	elif 'Balance' in card_name:
		field='bal_qty'

	avgitem='Wo001'
	if 'Trade' in card_name:
		avgitem='Wo005'

	if card_name in ['MTD Waste Oil Opening Stock','MTD Waste Oil Collection','MTD Waste Oil Issued','MTD Waste Oil Balance']:
		from_date=first_day_month
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO001'],'warehouse':['FT-1/FT-2 (WASTE OIL) - DURE','RT (WASTE OIL) - DURE']}
		carddata=get_card_data(field,filters)

	elif card_name in ['MTD Waste Oil Opening Stock Trade','MTD Waste Oil Collection Trade','MTD Waste Oil Issued Trade','MTD Waste Oil Balance Trade']:
		from_date=first_day_month
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO005'],'warehouse':['WASTE OIL(EXTERNAL TANK) - DURE']}
		carddata=get_card_data(field,filters)

	elif card_name in ['YTD Waste Oil Opening Stock','YTD Waste Oil Collection','YTD Waste Oil Issued','YTD Waste Oil Balance']:
		from_date=first_day_year
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO001'],'warehouse':['FT-1/FT-2 (WASTE OIL) - DURE','RT (WASTE OIL) - DURE']}
		carddata=get_card_data(field,filters)

	elif card_name in ['YTD Waste Oil Opening Stock Trade','YTD Waste Oil Collection Trade','YTD Waste Oil Issued Trade','YTD Waste Oil Balance Trade']:
		from_date=first_day_year
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO005'],'warehouse':['WASTE OIL(EXTERNAL TANK) - DURE']}
		carddata=get_card_data(field,filters)
#--------------------------------------------------------------
	elif card_name in ['YTD AVG Waste Oil Price','YTD AVG Waste Oil Price Trade']:
		from_date=first_day_year
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':[avgitem],'voucher_type':'Purchase Receipt'}
		carddata=avg_waste_oil_price(filters)

	elif card_name in ['MTD AVG Waste Oil Price','MTD AVG Waste Oil Price Trade']:
		from_date=first_day_month
		filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':[avgitem],'voucher_type':'Purchase Receipt'}
		carddata=avg_waste_oil_price(filters)
#--------------------------------------------------------------------
	if not carddata:
		carddata['fieldtype']='Float'
		carddata['value']=0
	return carddata

def get_card_data(field,filters):
	carddata = {}
	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	include_uom = filters.get("include_uom")
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	iwb_map = get_item_warehouse_map(filters, sle)
	item_map = get_item_details(items, sle, filters)
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())

	data = []
	conversion_factors = {}

	_func = itemgetter(1)

	for (company, item, warehouse) in sorted(iwb_map):
		if item_map.get(item):
			qty_dict = iwb_map[(company, item, warehouse)]
			item_reorder_level = 0
			item_reorder_qty = 0
			if item + warehouse in item_reorder_detail_map:
				item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
				item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

			report_data = {
				"currency": company_currency,
				"item_code": item,
				"warehouse": warehouse,
				"company": company,
				"reorder_level": item_reorder_level,
				"reorder_qty": item_reorder_qty,
			}
			report_data.update(item_map[item])
			report_data.update(qty_dict)

			if include_uom:
				conversion_factors.setdefault(item, item_map[item].conversion_factor)

			data.append(report_data)
	open_bal=0
	for dt in data:
		open_bal+=dt[field]
		#print(str(dt['opening_qty'])+'\n')
	carddata['fieldtype']='Float'
	carddata['value']=open_bal
	return carddata

def avg_waste_oil_price(filters):
	carddata = {}
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items,1)
	
	open_bal=0
	rtcnt=0
	for dt in sle:
		open_bal+=dt['incoming_rate']        
		rtcnt+=1

	carddata['fieldtype']='Float'
	carddata['value']=0
	if open_bal:
		carddata['value']=open_bal/rtcnt
	return carddata
	

def get_conditions(filters,to=''):
	conditions = ""
	if filters.get("from_date") and to:
		conditions += " and sle.posting_date >= %s" % frappe.db.escape(filters.get("from_date"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))

	if filters.get("company"):
		conditions += " and sle.company = %s" % frappe.db.escape(filters.get("company"))

	if filters.get("voucher_type"):
		conditions += " and sle.voucher_type = %s" % frappe.db.escape(filters.get("voucher_type"))

	if filters.get("warehouse"):
		warehouse_details = filters.get("warehouse")
		if warehouse_details:
			conditions += """ and sle.warehouse in ('{}')""".format( "' ,'".join([str(elem) for elem in warehouse_details]))

	return conditions


def get_stock_ledger_entries(filters, items,to=''):
	item_conditions_sql = ""
	if items:
		item_conditions_sql = " and sle.item_code in ({})".format(
			", ".join(frappe.db.escape(i, percent=False) for i in items)
		)

	conditions = get_conditions(filters,to)

	return frappe.db.sql(
		"""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
			sle.item_code as name, sle.voucher_no, sle.stock_value, sle.batch_no, sle.incoming_rate
		from
			`tabStock Ledger Entry` sle
		where sle.docstatus < 2 %s %s
		and is_cancelled = 0
		order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty"""
		% (item_conditions_sql, conditions),  # nosec
		as_dict=1,debug=0
	)


def get_item_warehouse_map(filters, sle):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict(
				{
					"opening_qty": 0.0,
					"opening_val": 0.0,
					"in_qty": 0.0,
					"in_val": 0.0,
					"out_qty": 0.0,
					"out_val": 0.0,
					"bal_qty": 0.0,
					"bal_val": 0.0,
					"val_rate": 0.0,
				}
			)

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

		if d.voucher_type == "Stock Reconciliation" and not d.batch_no:
			qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date or (
			d.posting_date == from_date
			and d.voucher_type == "Stock Reconciliation"
			and frappe.db.get_value("Stock Reconciliation", d.voucher_no, "purpose") == "Opening Stock"
		):
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if flt(qty_diff, float_precision) >= 0:
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff

	iwb_map = filter_items_with_no_transactions(iwb_map, float_precision)

	return iwb_map


def filter_items_with_no_transactions(iwb_map, float_precision):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]

		no_transactions = True
		for key, val in iteritems(qty_dict):
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False

		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map


def get_items(filters):
	
	if filters.get("item_code"):
		items=filters.get("item_code")
	return items


def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set(d.item_code for d in sle))

	if not items:
		return item_details

	cf_field = cf_join = ""
	if filters.get("include_uom"):
		cf_field = ", ucd.conversion_factor"
		cf_join = (
			"left join `tabUOM Conversion Detail` ucd on ucd.parent=item.name and ucd.uom=%s"
			% frappe.db.escape(filters.get("include_uom"))
		)

	res = frappe.db.sql(
		"""
		select
			item.name, item.item_name, item.description, item.item_group, item.brand, item.stock_uom %s
		from
			`tabItem` item
			%s
		where
			item.name in (%s)
	"""
		% (cf_field, cf_join, ",".join(["%s"] * len(items))),
		items,
		as_dict=1,
	)

	for item in res:
		item_details.setdefault(item.name, item)

	if filters.get("show_variant_attributes", 0) == 1:
		variant_values = get_variant_values_for(list(item_details))
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in iteritems(item_details)}

	return item_details


def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql(
			"""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(
				", ".join(frappe.db.escape(i, percent=False) for i in items)
			),
			as_dict=1,
		)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)


def get_variants_attributes():
	"""Return all item variant attributes."""
	return [i.name for i in frappe.get_all("Item Attribute")]


def get_variant_values_for(items):
	"""Returns variant values for items."""
	attribute_map = {}
	for attr in frappe.db.sql(
		"""select parent, attribute, attribute_value
		from `tabItem Variant Attribute` where parent in (%s)
		"""
		% ", ".join(["%s"] * len(items)),
		tuple(items),
		as_dict=1,
	):
		attribute_map.setdefault(attr["parent"], {})
		attribute_map[attr["parent"]].update({attr["attribute"]: attr["attribute_value"]})

	return attribute_map
