# -*- coding: utf-8 -*-
# Copyright (c) 2017, Direction and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate
from frappe import throw, msgprint, _


@frappe.whitelist()
def validate_expense(exp_year,exp_date,employee):

	emprv=frappe.db.sql(""" select * from `tabExpense Request Item` where docstatus=1 and employee='{0}' and date between DATE_SUB('{2}', INTERVAL {1} YEAR) and '{2}' """.format(employee,exp_year,exp_date),as_dict=1,debug=0)

	if emprv:
		return 1
	else:
		return 0
	
@frappe.whitelist()
def maintanse_items(sub_gp):
	return frappe.db.sql(""" select sub_group_items from `tabAsset Sub Group Items` where parent='{0}' """.format(sub_gp),as_dict=1,debug=0)
