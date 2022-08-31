# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	return get_columns(), get_data(filters=None)

def get_columns():
	return [{
   "fieldname": "name",
   "fieldtype": "Data",
   "label": "Invoice",
   "width": 150
  },
  {
   "fieldname": "customer",
   "fieldtype": "Link",
   "label": "Customer",
   "options": "Customer",
   "width": 300
  },
  {
   "fieldname": "property",
   "fieldtype": "Link",
   "label": "Property",
   "options": "Property Master",
   "width": 200
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
   "label": "Contract Start Date",
   "width": 100
  },
  {
   "fieldname": "contract_end_date",
   "fieldtype": "Date",
   "label": "Contract End Date",
   "width": 100
  },
  {
   "fieldname": "base_net_total",
   "fieldtype": "Currency",
   "label": "Amount",
   "width": 100
  }

	]

def get_data(filters=None):
	return frappe.db.sql(""" select name,customer,property,property_unit,contract_start_date,contract_end_date,base_net_total from `tabSales Invoice` where company='Bin Butti International Real Estate Management – Unincorporated' and docstatus=1  and posting_date >= MAKEDATE(year(now()), 1) """,as_dict=1)