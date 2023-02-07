// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Annual Leave Payslip', {
	 refresh: function(frm) {
		frm.set_query("leave_application", function() {
			return {
				filters: {"employee": frm.doc.employee,'leave_type':'Annual Leave'}
				
			}
		});
		
	 },
	 ending_date: function(frm) {
		frm.trigger("get_annual_leave");
		frm.trigger("get_emp_detail");
		frm.trigger("get_tickets_given");
		frm.trigger("get_settlement_details");
		
	 },
	 get_annual_leave: function(frm) {

		if (frm.doc.docstatus === 0 && frm.doc.employee  && frm.doc.date_of_joining && frm.doc.ending_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.starting_date,
					to_date: frm.doc.ending_date,
					leave_type: 'Annual Leave',
					consider_all_leaves_in_the_allocation_period: 1
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value('annual_leave', flt(r.message,3));
					} else {
						frm.set_value('annual_leave', "0");
					}
				}
			});
		}
	},get_emp_detail: function(frm) {

		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.starting_date && frm.doc.ending_date) {

			return frappe.call({
				method: "custom_reports.api.get_emp_details",
				args: {
					emp:frm.doc.employee,					
					start_date: frm.doc.starting_date,
					end_date:frm.doc.ending_date,					
				},
				callback: function (r) {
					if (r.message) {						
						frm.set_value('leaves_taken_during_this_year',r.message.leave_in_year);						
						frm.set_value('ticket_given',r.message.ticket_issued);
						frm.set_value('ticket_period',r.message.ticket_period);
						frm.set_value('used_leaves',r.message.used_leaves);
						frm.set_value('leave_entitled',r.message.leave_entitled);
						frm.set_value('salary_structure',r.message.salary_structure);
						frm.set_value('ticket_used',r.message.ticket_issued);
						frm.set_value('ticket_eligible',r.message.ticket_eligible);
						frm.set_value('gross_salary',r.message.gross_salary);
						frm.set_value('base_salary',r.message.base_salary);
					} else {
						frm.set_value('leaves_taken_during_this_year',"0");
						frm.set_value('ticket_balance',"0");						
						frm.set_value('ticket_period',"0");
						frm.set_value('used_leaves',"0");
						frm.set_value('leave_entitled',"0");
						frm.set_value('salary_structure',"0");
						frm.set_value('ticket_used',"0");
						frm.set_value('ticket_eligible',"0");
						frm.set_value('gross_salary',"0");
						frm.set_value('base_salary',"0");
					}
				}
			});
			
		}
	},get_tickets_given: function(frm) 
	{
		if (frm.doc.docstatus === 0 && frm.doc.employee  && frm.doc.date_of_joining && frm.doc.ending_date) {
			frappe.call({
				method: "custom_reports.api.get_ticket_given",
				args: {					
					emp: frm.doc.employee,
					from_date: frm.doc.date_of_joining,
					to_date: frm.doc.ending_date,		
				},
				callback: function(p) {
					if(p.message) {					
					frm.doc.ticket_balance=p.message.balance;
					frm.refresh_field('ticket_balance');
					
					frm.doc.ticket_used=p.message.used;
					frm.refresh_field('ticket_used');
						
					}
				}
			});
		}
	},
	get_settlement_details:function(frm)
	{ 
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.starting_date && frm.doc.ending_date) {
			return frappe.call({
				method: "custom_reports.api.get_employee_salarys",
				args: {
					emp:frm.doc.employee,					
					date_from: frm.doc.starting_date,
					date_to:frm.doc.ending_date,

				},
				callback: function (r) {
					if (r.message) {						
						$.each(r.message, function(i, jvd) {
							
							var c = frm.add_child("settlement_details");
							c.settlement=jvd.salary_component;
							c.paid_amt=jvd.amount;
							c.gen_amt=jvd.amount;
							c.narration=jvd.narration;
							c.slip=jvd.slip;
						});
						frm.refresh_field("settlement_details");
						frm.trigger("calc_tot");
					} 
				}
			});
		}
	},
	calc_tot: function(frm)
	{
		var tot=0;
		frm.doc.settlement_details.forEach(function(d) { 
			if(d.applied=='Yes')
			{
				tot+=Math.round(d.paid_amt,2);
				
			}
		});
		if(frm.doc.allowance_and_deducts){
			frm.doc.allowance_and_deducts.forEach(function(d) { 
				
					tot+=Math.round(d.currency_amt,2);
				
			});
		}
		frm.doc.total_amount=tot;
		frm.refresh_field('total_amount');
	}
});

frappe.ui.form.on('Allowance And Deducts', {
    
    currency_amt(frm, cdt, cdn) {
       
		var tot=0;
		frm.doc.settlement_details.forEach(function(d) { 
			if(d.applied=='Yes')
			{
				tot+=Math.round(d.paid_amt,2);
				
			}
		});
		if(frm.doc.allowance_and_deducts){
			frm.doc.allowance_and_deducts.forEach(function(d) { 
				
					tot+=Math.round(d.currency_amt,2);
				
			});
		}
		frm.doc.total_amount=tot;
		frm.refresh_field('total_amount');
    }
})

frappe.ui.form.on('Settlement Details', {
   
    paid_amt(frm, cdt, cdn) {
      
		var tot=0;
		frm.doc.settlement_details.forEach(function(d) { 
			if(d.applied=='Yes')
			{
				tot+=Math.round(d.paid_amt,2);
				
			}
		});
		if(frm.doc.allowance_and_deducts){
			frm.doc.allowance_and_deducts.forEach(function(d) { 
				
					tot+=Math.round(d.currency_amt,2);
				
			});
		}
		frm.doc.total_amount=tot;
		frm.refresh_field('total_amount');
    }
})