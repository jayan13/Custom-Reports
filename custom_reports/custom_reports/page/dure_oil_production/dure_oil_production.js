

frappe.pages['dure-oil-production'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Dure Oil Production',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				const comarry=[];
				
				
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
				$(frappe.render_template("dure_oil_production",data)).appendTo(this.page.main);
				
				function get_report()
				{
					//console.log(field.get_value());
					//console.log(field2.get_value());
					if(field2.get_value() && field3.get_value())
					{		
							frappe.call({
							method: 'custom_reports.custom_reports.page.dure_oil_production.dure_oil_production.get_report',
							freeze: 1,
							freeze_message: 'Data loading ...please waite',
							args: {							  
							  from_date: field2.get_value(),
							  to_date: field3.get_value(),
							},
							callback: function (r) {
							  if (r.message) {
								  $('#report_egg').html('');
									
									let data2=r.message;									
									$(frappe.render_template("dure_oil_production_data",data2)).appendTo("#report_egg");
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