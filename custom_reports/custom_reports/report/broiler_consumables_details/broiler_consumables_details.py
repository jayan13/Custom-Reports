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
		"fieldname": "project",
		"fieldtype": "Link",
		"label": "Project",
		"options": "Project",		
		"width": 200
		},
		{
		"fieldname": "item",
		"fieldtype": "Data",
		"label": "Item",	
		"width": 200
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
	
	data=[]
	conc=frappe.db.sql(""" select GROUP_CONCAT(name) as name,project,posting_date from `tabStock Entry` where stock_entry_type ='Manufacture' 
		and manufacturing_type='Broiler Chicken' and docstatus<2 and %s group by project order by project"""% (conditions),as_dict=1,debug=0)
	for cosu in conc:
		names=cosu.name.replace(",", "','")

		vaccine=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabVaccine` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in vaccine:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		medicine=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabMedicine` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in medicine:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		starter_item=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT starter_item from `tabFeed` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in starter_item:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		finisher_item=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT finisher_item from `tabFeed` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in finisher_item:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)
	
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)
	if filters.get("project"):
		project=filters.get("project")
		conditions += " and project= '{0}' ".format(project)
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(posting_date) <= '{0}'".format(date_to)

	return conditions

