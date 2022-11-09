// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Own Packing Material Report"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
		"default": "ABU DHABI MODERNE POULTRY FARM L.L.C."
	},{
		"fieldname": "date_from",
		"label": __("From"),
		"fieldtype": "Date",
		"default": frappe.datetime.month_start()
	},
	{
		"fieldname": "date_to",
		"label": __("To"),
		"fieldtype": "Date",
		"default": frappe.datetime.get_today()
	}
	]
};
