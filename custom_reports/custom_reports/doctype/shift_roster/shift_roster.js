// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Roster', {
	refresh: function(frm) {
		if(frm.doc.employee_list_html)
		{
			frm.fields_dict.employee_list.$wrapper.html(frm.doc.employee_list_html);
		}
		if(frm.doc.__islocal)
		{
			frm.fields_dict.employee_list.$wrapper.html('');
		}
		cur_frm.fields_dict.employee_list.$wrapper.find('.chkcng').on('change',function() {
			cur_frm.doc.__unsaved=1;
			//var index=this.selectedIndex;
			var val=$(this).val();	
			$(this).find('option').each(function(index,element){
							
				if (val==$(element).attr('value'))
				{
					$(element).attr('selected','selected');
				}else{
					$(element).removeAttr('selected');
				}
			});
		});
		//cur_frm.doc.__unsaved=1;
		
	},
	date_from:function(frm)
	{
		if(frm.doc.date_to)
		{
			if (frm.doc.date_to<frm.doc.date_from)
			{
				frappe.throw("From date Must be Less than or equal to To date")
			}
		}
		if(frm.doc.department && frm.doc.date_from && frm.doc.date_to)
		{
			frm.trigger('get_employees');
		}
	},
	date_to:function(frm)
	{
		if (frm.doc.date_to && frm.doc.date_from)
			{
				if (frm.doc.date_to<frm.doc.date_from)
				{
					frappe.throw("To date Must be grater than or equal to From date")
				}
			}

		if(frm.doc.department && frm.doc.date_from && frm.doc.date_to)
		{
			frm.trigger('get_employees');
		} 
	},
	get_employees:function(frm)
	{
		
		if(frm.doc.department=='')
		{
			frappe.throw(" Please select department")
		}
		if(frm.doc.date_from=='')
		{
			frappe.throw(" Please select date from")
		}
		if(frm.doc.date_to=='')
		{
			frappe.throw(" Please select date to")
		}
		frappe.call({
			method: "custom_reports.custom_reports.doctype.shift_roster.shift_roster.employee_list",
			args: {					
				department: frm.doc.department,				
				date_from: frm.doc.date_from,
				date_to: frm.doc.date_to,				
			},
			callback: function(p) {
				if(p.message) {					

					frm.fields_dict.employee_list.$wrapper.html(p.message);
					frm.doc.employee_list_html=p.message;

					cur_frm.fields_dict.employee_list.$wrapper.find('.chkcng').on('change',function() {
						cur_frm.doc.__unsaved=1;
						var val=$(this).val();						
						//var index=this.selectedIndex;	
						$(this).find('option').each(function(index,element){
							
							if (val==$(element).attr('value'))
							{
								$(element).attr('selected','selected');
							}else{
								$(element).removeAttr('selected');
							}
						});
						
					});
					
					
				}
			}
		})
	},
	before_save:function(frm)
	{

		//var html=$('div[data-fieldname="employee_list"]').html();
		var html=frm.fields_dict.employee_list.$wrapper.html();
		frm.doc.employee_list_html=html;
		frm.refresh_field('employee_list_html');
		var em=[]
		var d=[]
		cur_frm.fields_dict.employee_list.$wrapper.find('.emp').each(function(){
			em.push($(this).val());
			
		});

		cur_frm.fields_dict.employee_list.$wrapper.find('.dat').each(function(){
			d.push($(this).val());
			
		});
		
		var emparry=[];
		for(var i=0;i< em.length;i++)
		{
			
			for(var j=0;j< d.length;j++)
			{
				var ids="#"+em[i]+"_"+d[j]+"_s";
				var idd="#"+em[i]+"_"+d[j]+"_d";
				var idsdata=$(ids).val();
				var idddata=$(idd).val();
				emparry.push({shift_roster:'',employee:em[i],shift_type:idsdata,day:d[j],day_type:idddata});
			}
		}
		//console.log(emparry);
		//frappe.throw("test");
		var myJsonString = JSON.stringify(emparry);
		frm.doc.employee_list_data=myJsonString;
	},
	mark_attendance:function(frm)
	{

		frappe.confirm('Are you sure you want to mark Attendance?',
			() => {
				frappe.call({
					method: "custom_reports.custom_reports.doctype.shift_roster.shift_roster.mark_attendance",
					args: {					
						shift_roster: frm.doc.name		
					},
					callback: function(p) {
						if(p.message) {					
						frm.doc.attendance_marked='1';
						frm.refresh_field('attendance_marked');
						frappe.msgprint("Attendance marked");
							
						}
					}
				})
			}, () => {
				// action to perform if No is selected
			})
		
	},
	
});

cur_frm.fields_dict['department'].get_query = function(doc) {
	return {
		filters: {
			"company": doc.company
		}
	}
}
