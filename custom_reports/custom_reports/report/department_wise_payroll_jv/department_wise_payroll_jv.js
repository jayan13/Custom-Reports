// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();
frappe.query_reports["Department Wise Payroll Jv"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options":"Company",
			"reqd": 1 ,			
		},
		{
			"fieldname": "date_from",
			"label": __("From"),
			"fieldtype": "Date",
			"reqd": 1 ,
			"default": new Date(d.getFullYear(),d.getMonth(),1)		
		}
		,{
			"fieldname": "date_to",
			"label": __("To"),
			"fieldtype": "Date",
			"reqd": 1 ,
			"default": frappe.datetime.get_today()		
		}
	]
};
