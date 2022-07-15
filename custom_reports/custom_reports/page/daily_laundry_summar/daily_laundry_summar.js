
frappe.pages['daily-laundry-summar'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Daily Laundry Summary',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				const comarry=[];
				
				
				
					let field = this.page.add_field({
					label: 'Customer',
					fieldtype: 'Select',
					fieldname: 'customer',
					options: [],
					
				});
				
				frappe.call({
				  method: 'custom_reports.custom_reports.page.daily_laundry_summar.daily_laundry_summar.get_customer_list',
				  args: {},
				  callback: function (r) {
					if (r.message) {
						$('[data-fieldname="customer"][type="text"]').append($("<option></option>").attr("value", "").text("")); 
						$.each( r.message.customers, function( key, value ) {					
							
							$('[data-fieldname="customer"][type="text"]').append($("<option></option>").attr("value", value.name).text(value.name)); 
						}); 
						
					}
				  },
				});
				
		
				let field2 = this.page.add_field({
					label: 'Date From',
					fieldtype: 'Date',
					fieldname: 'from_date',
					
				});
		
				let field3 = this.page.add_field({
					label: 'Date To',
					fieldtype: 'Date',
					fieldname: 'to_date',
					
				});
				let field4 = this.page.add_field({
					label: 'Create report',
					fieldtype: 'Button',
					fieldname: 'create_report',
					click() {
						
						get_report();
						
					}
				});
				field2.set_value(frappe.datetime.get_today());
				field3.set_value(frappe.datetime.get_today());		
				//this.page.add_inner_button('Get  Report', () => get_report());
				this.page.add_inner_button('Print', () => print_rep());
				let data='';
				$(frappe.render_template("daily_laundry_summar",data)).appendTo(this.page.main);
				
				function get_report()
				{
					//console.log(field.get_value());
					//console.log(field2.get_value());
					if(field.get_value())
					{		
							frappe.call({
							method: 'custom_reports.custom_reports.page.daily_laundry_summar.daily_laundry_summar.get_report',
							freeze: 1,
							freeze_message: 'Data loading ...please waite',
							args: {
							  customer: field.get_value(),
							  from_date: field2.get_value(),
							  to_date: field3.get_value(),
							},
							callback: function (r) {
							  if (r.message) {
								  $('#report_egg').html('');
									
									let data2=r.message;
									if(field.get_value()==''){
										field.set_value(data2.customer);
									}
									$(frappe.render_template("daily_laundry_summar_data",data2)).appendTo("#report_egg");
							  }
							},
						  });
			  
					}
				}
				
				
				
			}
		
		
		})
		
		function print_rep()
				{
					
					var divToPrint=document.getElementById('report_egg');
		
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}