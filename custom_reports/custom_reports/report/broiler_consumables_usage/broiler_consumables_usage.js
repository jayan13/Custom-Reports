// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Broiler Consumables Usage"] = {
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
