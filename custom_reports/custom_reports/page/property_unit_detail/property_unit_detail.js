
frappe.pages['property-unit-detail'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
	//frappe.ui.toolbar.clear_cache();
	
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Property Unit Details',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				
				//this.page.add_inner_button('Print', () => print_rep());
				var wrp=this.page.main
				frappe.call({
					method: 'custom_reports.custom_reports.page.property_unit_detail.property_unit_detail.get_report',
					freeze: 1,
					args: {'unit_name':frappe.get_route()[1]},
					freeze_message: 'Data loading ...please waite',					
					callback: function (r) {
					  if (r.message) {							
							$(frappe.render_template("property_unit_detail",r.message)).appendTo(wrp);	
					  }
					},
				  });
				
			}
		
		
		})