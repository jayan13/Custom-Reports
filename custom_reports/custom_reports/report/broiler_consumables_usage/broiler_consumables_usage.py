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
		"width": 300
		},
		{
		"fieldname": "vaccine",
		"fieldtype": "Currency",
		"label": "Vaccine",	
		"width": 100
		},
		{
		"fieldname": "medicine",
		"fieldtype": "Currency",
		"label": "Medicine",	
		"width": 100
		},
		{
		"fieldname": "feed",
		"fieldtype": "Currency",
		"label": "Feed",	
		"width": 100
		},
		{
		"fieldname": "total",
		"fieldtype": "Currency",
		"label": "Total",	
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
		manu={}
		manu.update({'posting_date':cosu.posting_date})
		manu.update({'project':cosu.project})

		vaccine=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabVaccine` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if vaccine:
			vac=vaccine[0].basic_amount
		else:
			vac=0
		manu.update({'vaccine':vac})

		medicine=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabMedicine` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if medicine:
			med=medicine[0].basic_amount
		else:
			med=0

		manu.update({'medicine':med})	
		feed=0
		starter_item=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT starter_item from `tabFeed` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if starter_item:
			starter=starter_item[0].basic_amount
		else:
			starter=0

		finisher_item=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT finisher_item from `tabFeed` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if finisher_item:
			finisher=finisher_item[0].basic_amount
		else:
			finisher=0

		feed=starter+finisher
		manu.update({'feed':feed})
		total=vac+med+feed
		manu.update({'total':total})
		#...................................................................	
		data.append(manu)
	
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(posting_date) <= '{0}'".format(date_to)

	return conditions
