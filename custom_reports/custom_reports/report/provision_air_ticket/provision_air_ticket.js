// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Provision Air Ticket"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
		"reqd": 1 ,
		"default": frappe.defaults.get_user_default("Company"),
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
