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
		"fieldtype": "MultiSelectList",
		"options":"Department",
		get_data: function(txt) {
			return frappe.db.get_link_options('Department', txt, {
				company: frappe.query_report.get_filter_value("company")
			});
		}
	}
	,{
		"fieldname": "employee",
		"label": __("Employee"),
		"fieldtype": "Link",
		"options":"Employee",
	}
	]
};

