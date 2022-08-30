// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Property Unit List"] = {
	"filters": [
		{
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": 'Bin Butti International Real Estate Management – Unincorporated'
        },
		{
			"fieldname": "property_name",
			"fieldtype": "Link",
			"label": "Property",
			"options": "Property Master",
		},

	]
};
