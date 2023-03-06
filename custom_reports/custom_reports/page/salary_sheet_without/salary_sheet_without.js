

frappe.pages['salary-sheet-without'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
	
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Salary Sheet Without Over Time',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				
				this.page.add_inner_button('Print', () => print_rep());
				var wrp=this.page.main
				frappe.call({
					method: 'custom_reports.custom_reports.page.salary_sheet_without.salary_sheet_without.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {							  
						payroll_entry: frappe.get_route()[1],
					  },					
					callback: function (r) {
					  if (r.message) {							
							$(frappe.render_template("salary_sheet_without",r.message)).appendTo(wrp);	
					  }
					},
				  });
				
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