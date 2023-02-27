// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Broiler Consumables Usages"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
		"default": frappe.defaults.get_user_default("Company"),
	},{
		"fieldname": "date_from",
		"label": __("From"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.month_start()
	},
	{
		"fieldname": "date_to",
		"label": __("To"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.get_today()
	}
	]
};