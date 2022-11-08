// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Broiler Consumables Details"] = {
	"filters": [{
		"fieldname": "project",
		"label": __("Project"),
		"fieldtype": "Link",
		"options":"Project",
		"get_query": function(){ return {'filters': [['Project', 'project_type','=','Broiler']]}}
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
