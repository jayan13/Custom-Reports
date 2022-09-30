frappe.pages['ql-sales-invoice-con'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Invoice',
		single_column: true
	});
}

frappe.pages['ql-sales-invoice-con'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Sales Invoice',
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
					change() {
						get_invoice();
					}
				});
				
				frappe.call({
				  method: 'custom_reports.custom_reports.page.ql_sales_invoice_con.ql_sales_invoice_con.get_customer_list',
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
					change() {
						get_invoice();
					}
					
				});
		
				let field3 = this.page.add_field({
					label: 'Date To',
					fieldtype: 'Date',
					fieldname: 'to_date',
					change() {
						get_invoice();
					}
					
				});

				let field1 = this.page.add_field({
					label: 'Sales Invoice',
					fieldtype: 'Select',
					fieldname: 'sales_invoice',
					options: [],
					
				});
				
				fdate=frappe.datetime.add_months(frappe.datetime.get_today(), -1);
				field2.set_value(fdate);
				field3.set_value(frappe.datetime.get_today());	
				function get_invoice()
				{
					frappe.call({
						method: 'custom_reports.custom_reports.page.ql_sales_invoice_con.ql_sales_invoice_con.get_invoice_list',
						args: {
							'customer':field.get_value(),
							'from_date':field2.get_value(),
							'to_date':field3.get_value(),
					},
						callback: function (r) {
						  if (r.message) {

							let data=r.message;
							if(field2.get_value()==''){
								field2.set_value(data.from_date);
							}
							if(field3.get_value()==''){
								field3.set_value(data.to_date);
							}

							$('[data-fieldname="sales_invoice"][type="text"]').find('option').remove();
							  $('[data-fieldname="sales_invoice"][type="text"]').append($("<option></option>").attr("value", "").text("")); 
							  $.each( r.message.invoices, function( key, value ) {					
								  
								  $('[data-fieldname="sales_invoice"][type="text"]').append($("<option></option>").attr("value", value.name).text(value.name)); 
							  }); 
							  
						  }
						},
					  });
				}
				

				let field4 = this.page.add_field({
					label: 'View Invoice',
					fieldtype: 'Button',
					fieldname: 'create_report',
					click() {
						
						get_report();
						
					}
				});
				
				this.page.add_inner_button('Print', () => print_rep());
				let data='';
				$(frappe.render_template("laundry_summary",data)).appendTo(this.page.main);
				
				function get_report()
				{
					//console.log(field.get_value());
					//console.log(field2.get_value());
					if(field.get_value() && field1.get_value())
					{		
							frappe.call({
							method: 'custom_reports.custom_reports.page.ql_sales_invoice_con.ql_sales_invoice_con.get_report',
							freeze: 1,
							freeze_message: 'Data loading ...please waite',
							args: {
							  customer: field.get_value(),
							  sales_invoice: field1.get_value(),
							},
							callback: function (r) {
							  if (r.message) {
								  $('#report_egg').html('');
									
									let data2=r.message;
									if(field.get_value()==''){
										field.set_value(data2.customer);
									}
									if(field1.get_value()==''){
										field1.set_value(data2.sales_invoice);
									}
									$(frappe.render_template("laundry_summary_data",data2)).appendTo("#report_egg");
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