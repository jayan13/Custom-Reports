// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material And Pro Req  Settlement Dashboard Settings', {
	 refresh: function(frm) {
		frm.set_query("casier_account", function() {
			return {
				filters: {"company": frm.doc.company}
				
			}
		});
		frm.set_query("casier_account_pro", function() {
			return {
				filters: {"company": frm.doc.company}
				
			}
		});
		frm.set_query("iou_cash_account", function() {
			return {
				filters: {"company": frm.doc.company}
				
			}
		});
	 }
});
