// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Orders to Invoice"] = {
	"filters": [
		{
			"fieldname": "date_from",
			"label": __("From"),
			"fieldtype": "Date",
			"reqd": 1 ,
		},
		{
			"fieldname": "date_to",
			"label": __("To"),
			"fieldtype": "Date",
			"reqd": 1 ,
		}
	]
};