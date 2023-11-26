// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee', {
	refresh(frm) {
		frm.set_query("ministry_of_labor_employer_id", function() {
			return {
				filters: {"parent": frm.doc.company}
				
			}
		});
	}
})
