# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AnnualLeavePayslip(Document):
	def on_submit(self):
		doc = frappe.get_doc('Leave Application', self.leave_application)
		doc.salary_paid_in_advance = '1'
		doc.save()

	def on_cancel(self):
		doc = frappe.get_doc('Leave Application', self.leave_application)
		doc.salary_paid_in_advance = '0'
		doc.save()	