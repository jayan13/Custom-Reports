// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Ticket Provision"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
		"reqd": 1 ,
		"default": frappe.defaults.get_user_default("Company"),
	},{
		"fieldname": "date_from",
		"label": __("Date From"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),			
	},{
		"fieldname": "processing_month",
		"label": __("Processing Month"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.get_today()		
	},{
		"fieldname": "employee",
		"label": __("Employee"),
		"fieldtype": "Link",
		"options":"Employee",
	}
	]
};
