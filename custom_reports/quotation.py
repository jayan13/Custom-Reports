# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import cint, flt

from erpnext.setup.utils import get_exchange_rate

@frappe.whitelist()
def quotation_comparison(purchase_order):

	tems=frappe.db.get_all('Purchase Order Item',filters={'parent': purchase_order},fields=['item_code','material_request'],debug=0)
	itemar=[]
	matreq=''
	for pitem in tems:
		itemar.append(pitem.item_code)
		matreq=pitem.material_request
	
	supplier_quotation_data = get_data(matreq,itemar)
	data= prepare_data(supplier_quotation_data)
	return data

def get_data(matreq,itemar):
	itemssql="','".join(itemar)
	supplier_quotation_data = frappe.db.sql(
		"""
		SELECT
			sqi.parent, sqi.item_code,
			sqi.qty, sqi.stock_qty, sqi.amount,
			sqi.uom, sqi.stock_uom,
			sqi.request_for_quotation,
			sqi.lead_time_days, sq.supplier as supplier_name, DATE_FORMAT(sq.valid_till, "%d-%m-%Y") as valid_till
		FROM
			`tabSupplier Quotation Item` sqi,
			`tabSupplier Quotation` sq
		WHERE
			sqi.parent = sq.name
			AND sqi.docstatus < 2
			AND sqi.item_code in ('{0}')
			AND sqi.material_request='{1}'
			order by sq.transaction_date, sqi.item_code""".format(
			itemssql,matreq
		),
		as_dict=1,
	)

	return supplier_quotation_data


def prepare_data(supplier_quotation_data):
	out, groups, qty_list, suppliers=  [], [], [], []
	group_wise_map = defaultdict(list)
	supplier_qty_price_map = {}

	group_by_field = (
		"item_code"
	)
	company_currency = frappe.db.get_default("currency")
	float_precision = cint(frappe.db.get_default("float_precision")) or 2

	for data in supplier_quotation_data:
		group = data.get(group_by_field)  # get item or supplier value for this row

		supplier_currency = frappe.db.get_value(
			"Supplier", data.get("supplier_name"), "default_currency"
		)

		if supplier_currency:
			exchange_rate = get_exchange_rate(supplier_currency, company_currency)
		else:
			exchange_rate = 1

		row = {
			"item_code": data.get("item_code"),
			"supplier_name": data.get("supplier_name"),
			"quotation": data.get("parent"),
			"qty": data.get("qty"),
			"price": flt(data.get("amount") * exchange_rate, float_precision),
			"uom": data.get("uom"),
			"stock_uom": data.get("stock_uom"),
			"request_for_quotation": data.get("request_for_quotation"),
			"valid_till": data.get("valid_till"),
			"lead_time_days": data.get("lead_time_days"),
		}
		row["price_per_unit"] = flt(row["price"]) / (flt(data.get("stock_qty")) or 1)

		# map for report view of form {'supplier1'/'item1':[{},{},...]}
		group_wise_map[group].append(row)

		# map for chart preparation of the form {'supplier1': {'qty': 'price'}}
		supplier = data.get("supplier_name")
		
		groups.append(group)
		suppliers.append(supplier)
		qty_list.append(data.get("qty"))

	groups = list(set(groups))
	suppliers = list(set(suppliers))
	qty_list = list(set(qty_list))

	highlight_min_price = group_by_field = "item_code"

	# final data format for report view
	for group in groups:
		group_entries = group_wise_map[group]  # all entries pertaining to item/supplier
		group_entries[0].update({group_by_field: group})  # Add item/supplier name in first group row

		if highlight_min_price:
			prices = [group_entry["price_per_unit"] for group_entry in group_entries]
			min_price = min(prices)

		for entry in group_entries:
			if highlight_min_price and entry["price_per_unit"] == min_price:
				entry["min"] = 1
			out.append(entry)



	return out