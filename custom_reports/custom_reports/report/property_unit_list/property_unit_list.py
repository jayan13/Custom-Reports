# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe


#def execute(filters=None):
#	columns, data = [], []
#	return columns, data

import frappe


def execute(filters=None):
	columns, data = [], []
	return get_columns(), get_data(filters)

def get_columns():
	return [
		{
   "fieldname": "property_name",
   "fieldtype": "Link",
   "label": "Property",
   "options": "Property Master",
   "width": 250
  },
  {
   "fieldname": "name",
   "fieldtype": "Data",
   "label": "Unit",
   "width": 250
  },
  {
   "fieldname": "customer_name",
   "fieldtype": "Link",
   "label": "Customer",
   "options": "Customer",
   "width": 350
  },
  {
   "fieldname": "contract_start_date",
   "fieldtype": "Date",
   "label": "Start Date",
   "width": 100
  },
  {
   "fieldname": "contract_end_date",
   "fieldtype": "Date",
   "label": "End Date",
   "width": 100
  },
  {
   "fieldname": "unit_status",
   "fieldtype": "Select",
   "label": "Status",
   "options": "Occupied,Vacant",
   "width": 100
  }
		]

def get_data(filters=None):	
	return frappe.db.sql(""" select property_name,name,customer_name,contract_start_date,contract_end_date,unit_status,unit_no from `tabProperty Unit`  """,as_dict=1)
