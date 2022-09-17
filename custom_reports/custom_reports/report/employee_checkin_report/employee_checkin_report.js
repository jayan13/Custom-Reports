// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Checkin Report"] = {
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
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				};
			}
		},
		
	]
};
