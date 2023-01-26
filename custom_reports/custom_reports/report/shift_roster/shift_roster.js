// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Shift Roster"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options":"Company",
		"reqd": 1 ,
		"default": frappe.defaults.get_user_default("Company"),
	},{
		"fieldname": "date_from",
		"label": __("From"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.month_start()		
	},{
		"fieldname": "date_to",
		"label": __("To"),
		"fieldtype": "Date",
		"reqd": 1 ,
		"default": frappe.datetime.get_today()		
	},{
		"fieldname": "department",
		"label": __("Department"),
		"fieldtype": "Link",
		"options":"Department",
	}
	,{
		"fieldname": "employee",
		"label": __("Employee"),
		"fieldtype": "Link",
		"options":"Employee",
	}
	]
};

