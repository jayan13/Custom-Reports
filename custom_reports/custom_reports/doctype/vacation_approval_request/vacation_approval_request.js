// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vacation Approval Request', {
	 refresh: function(frm) {
		frm.set_query("leave_application", function() {
			return {
				filters: {"employee": frm.doc.employee,'leave_type':'Annual Leave'}
				
			}
		});
	 },
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

				//leave_entitled
			}
		if(frm.doc.application_date && frm.doc.employee)
		{

		} 
	},
	leave_application:function(frm) {
		
	}
});
