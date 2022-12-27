// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gratuity Provisions"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
	},{
		"fieldname": "processing_month",
		"label": __("Processing Month"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.get_today()		
	},{
		"fieldname": "gratuity_rule",
		"label": __("Gratuity Rule"),
		"fieldtype": "Link",
		"options":"Gratuity Rule",
		"reqd": 1 ,
	},
	{
		"fieldname": "employee",
		"label": __("Employee"),
		"fieldtype": "Link",
		"options":"Employee",
	}
	]
};
