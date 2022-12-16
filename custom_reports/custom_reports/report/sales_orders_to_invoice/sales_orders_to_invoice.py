# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data(conditions)

def get_columns():
	
	columns = [
		{
		"fieldname": "name",
		"fieldtype": "Link",
		"label": "Sales Order",
		"options": "Sales Order",
		"width": 200
		},
		{
		"fieldname": "transaction_date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},		
		{
		"fieldname": "property",
		"fieldtype": "Link",
		"label": "Property",
		"options": "Property Master",	
		"width": 100
		},
		{
		"fieldname": "property_unit",
		"fieldtype": "Link",
		"label": "Property Unit",
		"options": "Property Unit",	
		"width": 200
		},
		{
		"fieldname": "contract_start_date",
		"fieldtype": "Date",
		"label": "Start Date",
		"width": 100
		},
		{
		"fieldname": "contract_end_date",
		"fieldtype": "End Date",
		"label": "Date",
		"width": 100
		},
		{
		"fieldname": "number_of_days",
		"fieldtype": "Data",
		"label": "Days",
		"width": 100
		},
		{
		"fieldname": "invoice_status",
		"fieldtype": "Data",
		"label": "Invoice Status",
		"width": 100
		},
		{
		"fieldname": "auto_repeat",
		"fieldtype": "Link",
		"label": "Auto Repeat",
		"options": "Auto Repeat",
		"width": 200
		}
		
 	 ]	
	
	return columns

def get_data(conditions):

	data=[]	
	stkentry=frappe.db.sql(""" select name,transaction_date,property,property_unit,contract_start_date,contract_end_date,'' as invoice_status,'' as auto_repeat,DATEDIFF(contract_end_date, contract_start_date)+1 as number_of_days from `tabSales Order` where  docstatus=1 and company='AL NOKHBA BUILDING' 
		and %s order by transaction_date"""% (conditions),as_dict=1,debug=0)
	for stk in stkentry:
		itm=frappe.db.sql("""select count(s.name) as cnt,s.auto_repeat from `tabSales Invoice Item` it left join `tabSales Invoice` s on s.name=it.parent where  s.docstatus=1 and it.sales_order='{0}' """.format(stk.name),as_dict=1,debug=0)
		stk.update({'invoice_status':itm[0].cnt})
		stk.update({'auto_repeat':itm[0].auto_repeat})
		#s.auto_repeat='' and
	return stkentry

def get_conditions(filters):
	
	conditions =" DATEDIFF(contract_end_date, contract_start_date)>0 "
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(transaction_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(transaction_date) <= '{0}'".format(date_to)

	return conditions
