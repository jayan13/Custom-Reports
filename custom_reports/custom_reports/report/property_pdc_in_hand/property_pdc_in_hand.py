# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	#columns, data = [], []
	return get_columns(), get_data(filters)

def get_columns():
	return [{
		"fieldname": "cheque_date",
		"fieldtype": "Date",
		"label": "Cheque Date",
		"width": 100
		},
		{
		"fieldname": "cheque_no",
		"fieldtype": "Data",
		"label": "Cheque no",
		"width": 100
		},
		{
		"fieldname": "amount",
		"fieldtype": "Currency",
		"label": "Amount",
		"width": 100
		},
		{
		"fieldname": "deposit_bank",
		"fieldtype": "Link",
		"label": "Bank",
		"options": "Account",
		"width": 400
		},
		{
		"fieldname": "payment_entry",
		"fieldtype": "Data",
		"label": "Payment Entry",
		"width": 200
		},
		{
		"fieldname": "journal_entry",
		"fieldtype": "Data",
		"label": "Journal Entry",
		"width": 150
		},
		{
		"fieldname": "cheque_status",
		"fieldtype": "Data",
		"label": "Status",
		"width": 150
		}

	]

def get_data(filters=None):	
	return frappe.db.sql(""" select cheque_date,cheque_no,amount,deposit_bank,payment_entry,journal_entry,cheque_status from `tabReceivable Cheques` where company='Bin Butti International Real Estate Management – Unincorporated' and cheque_status='Cheque Received' order by cheque_date""",as_dict=1)