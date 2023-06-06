
frappe.pages['salary-comparison'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
	
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Salary Comparison',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				frappe.get_route()[1]
				let field = this.page.add_field({
					label: 'Payroll Entry',
					fieldtype: 'Link',
					fieldname: 'payroll_entry',
					options: 'Payroll Entry',
					change() {
						get_report();
					}
				});
			this.page.add_inner_button('Print', () => print_rep());
			var wrp=this.page.main

			if(frappe.get_route()[1]){
				field.set_value(frappe.get_route()[1]);
				get_report();
			}

			function get_report()
			{
				$('#report_eggs').remove();
				if(field.get_value())
				{
					
					frappe.call({
						method: 'custom_reports.custom_reports.page.salary_comparison.salary_comparison.get_report',
						freeze: 1,
						freeze_message: 'Data loading ...please waite',
						args: {							  
							payroll_entry: field.get_value(),
						},					
						callback: function (r) {
						if (r.message) {							
								$(frappe.render_template("salary_comparison",r.message)).appendTo(wrp);	
						}
						},
					}); 
				}
			}
				
				
				
			}
		
		
		})
		
		function print_rep()
				{
					
					var divToPrint=document.getElementById('report_eggs');
		
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>	.table-bordered{ display: table; text-indent: initial; border-spacing: 0; border-collapse: collapse; width: 100%; max-width: 100%; font-size: inherit; } .table-bordered tr td{ border-color: black !important; border-left:none !important; border-right:none !important; } .table-bordered{ border:none !important; } </style><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}