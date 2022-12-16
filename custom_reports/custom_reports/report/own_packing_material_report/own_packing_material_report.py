# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data(conditions,filters)

def get_columns():
	
	columns = [
		{
		"fieldname": "posting_date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},
		{
		"fieldname": "item",
		"fieldtype": "Data",
		"label": "Item",	
		"width": 400
		},
		{
		"fieldname": "transfer_qty",
		"fieldtype": "Float",
		"label": "Qty",	
		"width": 100
		},
		{
		"fieldname": "stock_uom",
		"fieldtype": "Data",
		"label": "Uom",	
		"width": 100
		},
		{
		"fieldname": "basic_rate",
		"fieldtype": "Currency",
		"label": "Rate",	
		"width": 100
		},
		{
		"fieldname": "basic_amount",
		"fieldtype": "Currency",
		"label": "Amount",	
		"width": 100
		}
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	
	conc=frappe.db.sql(""" select s.posting_date,CONCAT(d.item_code,' - ',d.item_name) as item,sum(d.transfer_qty) as transfer_qty,d.stock_uom,d.basic_rate,sum(d.basic_amount) as basic_amount from `tabStock Entry Detail` d left join `tabStock Entry` s on s.name=d.parent 
where d.item_code in(select DISTINCT item from `tabPacking Items`) and s.stock_entry_type ='Manufacture' 
and s.manufacturing_type='Chicken Slaughtering' and s.docstatus=1 and %s group by d.item_code order by d.item_name """% (conditions),as_dict=1,debug=1)
	
	return conc

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and s.company= '{0}' ".format(company)
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(s.posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(s.posting_date) <= '{0}'".format(date_to)

	return conditions


