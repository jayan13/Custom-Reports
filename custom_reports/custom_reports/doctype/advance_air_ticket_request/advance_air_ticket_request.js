// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Advance Air Ticket Request', {
	// refresh: function(frm) {

	// }
	employee:function(frm) {
		if(frm.doc.employee)
			{
				frappe.call({
				method: 'custom_reports.leave.get_ticket_blance',
						args: {
							'emp':frm.doc.employee,
					},
					callback: function(data) {
						if(data.message)
						{
							frm.doc.ticket_available=data.message;
							frm.refresh_field('ticket_available');
						}
					}
				});
			} 
	}
});
