# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, get_datetime, get_link_to_form, add_days, getdate, date_diff, get_first_day, get_last_day
from frappe.model.document import Document

class FinalSettlementRequest(Document):
	pass

