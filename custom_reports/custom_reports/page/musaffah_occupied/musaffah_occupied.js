frappe.pages['musaffah-occupied'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Property Unit Report',
		single_column: true
	});
}

frappe.pages['musaffah-occupied'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Property Unit Report',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				
				this.page.add_inner_button('Print', () => print_rep());
				var wrp=this.page.main
				frappe.call({
					method: 'custom_reports.custom_reports.page.musaffah_occupied.musaffah_occupied.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',					
					callback: function (r) {
					  if (r.message) {							
							$(frappe.render_template("musaffah_plot",r.message)).appendTo(wrp);	
					  }
					},
				  });
				
			}
		
		
		})
		
		function print_rep()
				{
					
					var divToPrint=document.getElementById('unit_report');
		
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}