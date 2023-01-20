// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Final Settlement Request', {
	before_save: function(frm) {
		var tot=0;
		frm.doc.settlement_details.forEach(function(d) { 
			if(d.applied=='Yes')
			{
				tot+=Math.round(d.paid_amt,2);
				
			}
		});
		frm.doc.allowance_and_deducts.forEach(function(d) { 
			
				tot+=Math.round(d.currency_amt,2);
			
		});
		frm.doc.total_amount=tot;
	}, 
	employee:function(frm)
	{
		cur_frm.clear_table("settlement_details");
		frm.trigger("get_settlement_details"); 
		frm.trigger("get_annual_leave");
		frm.trigger("get_day_off_compensatory");
		frm.trigger("annual_leave");
		frm.trigger("day_off_compensatory");
		frm.trigger("get_period_worked");	
		frm.trigger("gratuity_rule");
	},
	relieving_date:function(frm)
	{
		cur_frm.clear_table("settlement_details");
		frm.trigger("get_settlement_details"); 
		frm.trigger("get_annual_leave");
		frm.trigger("get_day_off_compensatory");
		frm.trigger("annual_leave");
		frm.trigger("day_off_compensatory");
		frm.trigger("get_period_worked");	
		frm.trigger("gratuity_rule");
		if (frm.doc.docstatus === 0 && frm.doc.employee  && frm.doc.date_of_joining && frm.doc.relieving_date) {
			frappe.call({
				method: "custom_reports.api.get_ticket_given",
				args: {					
					emp: frm.doc.employee,
					from_date: frm.doc.date_of_joining,
					to_date: frm.doc.relieving_date,		
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
	date_of_joining:function(frm)
	{
		cur_frm.clear_table("settlement_details");
		frm.trigger("get_settlement_details"); 
		frm.trigger("get_annual_leave");
		frm.trigger("get_day_off_compensatory");
		frm.trigger("annual_leave");
		frm.trigger("day_off_compensatory");
		frm.trigger("get_period_worked");	
		frm.trigger("gratuity_rule");
	},
	annual_leave: function(frm) {
		
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.annual_leave && frm.doc.relieving_date) {

			return frappe.call({
				method: "custom_reports.api.get_annual_leaveamount",
				args: {
					emp:frm.doc.employee,					
					reval_date: frm.doc.relieving_date,				
				},
				callback: function (r) {
					if (r.message) {
						var itemin=0;
						frm.doc.settlement_details.forEach(function(d) { 
							if(d.settlement=='Annual Leave')
							{
								d.paid_amt=((r.message.sal*12)/365)*frm.doc.annual_leave;
								itemin=1;
							}
						});
						if(itemin==0)
						{						
						var c = frm.add_child("settlement_details");
							c.settlement='Annual Leave';
							c.paid_amt=((r.message.sal*12)/365)*frm.doc.annual_leave;
							c.gen_amt=c.paid_amt;
							c.days=frm.doc.annual_leave;
							c.narration='Annual Leave';
						}
						frm.doc.gross_salary=r.message.gross_salary;
						frm.doc.ticket_period=r.message.ticket_period
						frm.doc.used_leaves=r.message.used_leaves
						frm.doc.base_salary=r.message.base_salary 
						frm.doc.leave_entitled=r.message.leave_entitled
						frm.doc.salary_structure=r.message.salary_structure						
						frm.doc.ticket_eligible=r.message.ticket_eligible
							frm.refresh_fields();
					} 
				}
			});
			
		}
	},
	get_annual_leave: function(frm) {

		if (frm.doc.docstatus === 0 && frm.doc.employee  && frm.doc.date_of_joining && frm.doc.relieving_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.relieving_date,
					to_date: frm.doc.relieving_date,
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
	},
	day_off_compensatory: function(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.day_off_compensatory && frm.doc.relieving_date) {

			return frappe.call({
				method: "custom_reports.api.get_compen_amount",
				args: {
					emp:frm.doc.employee,					
					reval_date: frm.doc.relieving_date,				
				},
				callback: function (r) {
					if (r.message) {						
						
							var itemin=0;
							frm.doc.settlement_details.forEach(function(d) { 
								if(d.settlement=='Compensatory')
								{
									d.paid_amt=((r.message*12)/365)*frm.doc.day_off_compensatory;
									itemin=1;
								}
							});
							if(itemin==0)
							{
								var c = frm.add_child("settlement_details");
								c.settlement='Compensatory';
								c.paid_amt=((r.message*12)/365)*frm.doc.day_off_compensatory;
								c.gen_amt=c.paid_amt;
								c.days=frm.doc.day_off_compensatory;
								c.narration='Compensatory';
							}

							frm.refresh_fields();
					} 
				}
			});
			
		}
	},
	get_day_off_compensatory: function(frm) {
		if (frm.doc.docstatus === 0 && frm.doc.employee  && frm.doc.date_of_joining && frm.doc.relieving_date) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
				args: {
					employee: frm.doc.employee,
					date: frm.doc.relieving_date,
					to_date: frm.doc.relieving_date,
					leave_type: 'Compassionate leave',
					consider_all_leaves_in_the_allocation_period: 1
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value('day_off_compensatory', flt(r.message,3));
					} else {
						frm.set_value('day_off_compensatory', "0");
					}
				}
			});
		}
	},
	period_worked:function(frm)
	{
		
	},
	get_period_worked:function(frm)
	{
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.date_of_joining && frm.doc.relieving_date) {

			return frappe.call({
				method: "custom_reports.api.get_year_month_day",
				args: {
					emp:frm.doc.employee,					
					date_from: frm.doc.relieving_date,
					date_to: frm.doc.date_of_joining,					
				},
				callback: function (r) {
					if (r.message) {						
						frm.set_value('period_worked',r.message);
					} else {
						frm.set_value('period_worked', "0");
					}
				}
			});
			
		}
	},
	gratuity_rule:function(frm)
	{
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.gratuity_rule && frm.doc.relieving_date) {
			
			return frappe.call({
				method: "custom_reports.api.calculate_work_experience_and_amount",
				args: {
					employee:frm.doc.employee,					
					gratuity_rule: frm.doc.gratuity_rule,
					processing_month:frm.doc.relieving_date,

				},
				callback: function (r) {
					if (r.message) {						
						frm.set_value('gratuity_amount',r.message.amount);
						frm.set_value('accured_days', r.message.accured_days);

						var itemin=0;
						frm.doc.settlement_details.forEach(function(d) { 
							if(d.settlement=='Gratuity')
							{
								d.paid_amt=r.message.amount;
								d.days=r.message.accured_days;
								itemin=1;
							}
						});
						if(itemin==0)
						{

						var c = frm.add_child("settlement_details");
							c.settlement='Gratuity';
							c.paid_amt=r.message.amount;
							c.gen_amt=c.paid_amt;
							c.days=r.message.accured_days;
							c.narration='Gratuity';
						}	
							frm.refresh_fields();
					} else {
						frm.set_value('gratuity_amount', "0");
						frm.set_value('accured_days', "0");
						
					}
				}
			});
			
		}

	},
	settlement_details:function(frm)
	{ 
		
	},
	get_settlement_details:function(frm)
	{ 
		if (frm.doc.docstatus === 0 && frm.doc.employee && frm.doc.date_of_joining && frm.doc.relieving_date) {
			return frappe.call({
				method: "custom_reports.api.get_employee_salary",
				args: {
					emp:frm.doc.employee,					
					date_from: frm.doc.date_of_joining,
					date_to:frm.doc.relieving_date,

				},
				callback: function (r) {
					if (!r.exc && r.message) {						
						$.each(r.message, function(i, jvd) {
							
							var c = frm.add_child("settlement_details");
							c.settlement=jvd.salary_component;
							c.paid_amt=jvd.amount;
							c.gen_amt=c.paid_amt;
							c.narration=jvd.salary_component;
						});
						frm.refresh_fields();
					} 
				}
			});
		}
	}
});
