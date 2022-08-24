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
def opening_waste_oil_month():
	#is_reposting_item_valuation_in_progress()
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	from_date=first_day_month
	filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO001','WO005']}
	
	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	include_uom = filters.get("include_uom")
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	if filters.get("show_stock_ageing_data"):
		filters["show_warehouse_wise_stock"] = True
		item_wise_fifo_queue = FIFOSlots(filters, sle).generate()

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
		open_bal+=dt['opening_qty']
		#print(str(dt['opening_qty'])+'\n')
	carddata['fieldtype']='Float'
	carddata['value']=open_bal
	return carddata

@frappe.whitelist()
def opening_waste_oil_year():
	#is_reposting_item_valuation_in_progress()
	carddata = {}
	to_date = frappe.utils.today()
	fromdate=getdate(to_date)
	first_day_month=fromdate.replace(day=1)
	first_day_year=fromdate.replace(month=1, day=1)
	from_date=first_day_year
	filters = {'from_date':from_date,'to_date':to_date,'company':'Dure Oil Middle East Factory - Sole Proprietorship LLC','item_code':['WO001','WO005']}
	
	if filters.get("company"):
		company_currency = erpnext.get_company_currency(filters.get("company"))
	else:
		company_currency = frappe.db.get_single_value("Global Defaults", "default_currency")

	include_uom = filters.get("include_uom")
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)

	if filters.get("show_stock_ageing_data"):
		filters["show_warehouse_wise_stock"] = True
		item_wise_fifo_queue = FIFOSlots(filters, sle).generate()

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
		open_bal+=dt['opening_qty']
		#print(str(dt['opening_qty'])+'\n')
	carddata['fieldtype']='Float'
	carddata['value']=open_bal
	return carddata

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("company"):
		conditions += " and sle.company = %s" % frappe.db.escape(filters.get("company"))

	if filters.get("warehouse"):
		warehouse_details = filters.get("warehouse")
		if warehouse_details:
			conditions += """ and sle.warehouse in ('{}')""".format( "' ,'".join([str(elem) for elem in warehouse_details]))

	return conditions


def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ""
	if items:
		item_conditions_sql = " and sle.item_code in ({})".format(
			", ".join(frappe.db.escape(i, percent=False) for i in items)
		)

	conditions = get_conditions(filters)

	return frappe.db.sql(
		"""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
			sle.item_code as name, sle.voucher_no, sle.stock_value, sle.batch_no
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
