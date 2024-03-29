// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Head Count"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options":"Company",
			"reqd": 1 ,
			"default": frappe.defaults.get_user_default("Company"),			
		},
		{
			"fieldname": "date_to",
			"label": __("Month"),
			"fieldtype": "Date",
			"reqd": 1 ,
			"default": frappe.datetime.get_today()		
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "MultiSelectList",
			"options":"Department",
			get_data: function(txt) {
				return frappe.db.get_link_options('Department', txt, {
					company: frappe.query_report.get_filter_value("company")
				});
			}
		}

	]
};