// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Provision Gratuity"] = {
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
		on_change: function() {
			if (frappe.query_report.get_filter_value("date_from")<'2022-12-31')
			{
				
				frappe.query_report.set_filter_value('date_from', "");
				frappe.throw('From date must be grater than 31-12-2022');
				return;
			}			
		}					
	},
	{
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
