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
		"fieldname": "posting_date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},		
		{
		"fieldname": "waste_oil_consumed",
		"fieldtype": "Data",
		"label": "Waste oil consumed",	
		"width": 100
		},
		{
		"fieldname": "lightend_qty",
		"fieldtype": "Data",
		"label": "Lightend Qty",	
		"width": 100
		},
		{
		"fieldname": "lightend_cost",
		"fieldtype": "Currency",
		"label": "Lightend Cost",	
		"width": 100
		},
		{
		"fieldname": "lightlube_qty",
		"fieldtype": "Data",
		"label": "Lightlube Qty",	
		"width": 100
		},
		{
		"fieldname": "lightlube_cost",
		"fieldtype": "Currency",
		"label": "Lightlube Cost",	
		"width": 100
		},
		{
		"fieldname": "asphalt_qty",
		"fieldtype": "Data",
		"label": "Asphalt Qty",	
		"width": 100
		},
		{
		"fieldname": "asphalt_cost",
		"fieldtype": "Currency",
		"label": "Asphalt Cost",	
		"width": 100
		},
		{
		"fieldname": "waste_water_qty",
		"fieldtype": "Data",
		"label": "Waste water Qty",	
		"width": 100
		},
		{
		"fieldname": "waste_water_cost",
		"fieldtype": "Currency",
		"label": "Waste water Cost",	
		"width": 100
		},		
		{
		"fieldname": "total_recovery",
		"fieldtype": "Data",
		"label": "Total Recovery %",	
		"width": 100
		}
 	 ]	
	
	return columns

def get_data(conditions):

	data=[]	
	stkentry=frappe.db.sql(""" select p.name as process_order,s.name,s.posting_date as posting_date from `tabStock Entry` s 
		left join `tabProcess Order` p on s.process_order=p.name 
		where s.process_order!='' and s.docstatus<2 and p.process_type='Waste Oil Re-refining' and s.stock_entry_type='Manufacture'
		and %s order by s.posting_date"""% (conditions),as_dict=1,debug=0)
	for stk in stkentry:
		manu={}
		manu.update({'posting_date':stk.posting_date})
		itm=frappe.db.sql(""" select item_code,qty,uom,amount from `tabStock Entry Detail` 
        where parent='{0}' ORDER BY FIELD(item_code, 'WO001', 'LLB001','LI0001','AS0001','WT1-WATER') """.format(stk.name),as_dict=1,debug=0)
		wt=0
		prd=0
		recovery=0
		for it in itm:
			if it.item_code=='WO001':
				wt=it.qty
				manu.update({'waste_oil_consumed':it.qty})
			if it.item_code=='LLB001':
				prd+=it.qty				
				manu.update({'lightlube_qty':it.qty,'lightlube_cost':it.amount})
			if it.item_code=='LI0001':
				prd+=it.qty
				manu.update({'lightend_qty':it.qty,'lightend_cost':it.amount})
			if it.item_code=='AS0001':
				prd+=it.qty
				manu.update({'asphalt_qty':it.qty,'asphalt_cost':it.amount})
			if it.item_code=='WT1-WATER':
				prd+=it.qty
				manu.update({'waste_water_qty':it.qty,'waste_water_cost':it.amount})

		recovery=round((prd/wt)*100)
		manu.update({'total_recovery':recovery})
		data.append(manu)

	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(s.posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(s.posting_date) <= '{0}'".format(date_to)

	return conditions
