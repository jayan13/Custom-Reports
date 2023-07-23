// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Credit Approval', {
	// refresh: function(frm) {

	// }
	
});

cur_frm.fields_dict.address.get_query = function(doc) {
	return {
		filters: {
			customer: doc.client
		}
	}
}