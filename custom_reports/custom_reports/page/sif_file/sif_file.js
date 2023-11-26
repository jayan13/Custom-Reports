
frappe.pages['sif-file'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
	
}

		MyPage =Class.extend({
	
			init: function(wrapper){
				this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Salary Information',
					single_column: true
				});
					this.make(wrapper);
			},
			make: function(wrapper)
			{
				
				var company=frappe.defaults.get_user_default("Company");
				if(frappe.get_route()[1])
				{
					company=frappe.get_route()[1];
				}

				var payroll_entry=''
				if(frappe.get_route()[2])
				{
					payroll_entry=frappe.get_route()[2];
				}
				

				let field = this.page.add_field({
					label: 'Company',
					fieldtype: 'Link',
					fieldname: 'company',
					options: 'Company',
					reqd: 1,
					change() {
						load_tab(wrapper);
						
						//frappe.set_route("sif-file/"+field.get_value());
						//frappe.ui.toolbar.clear_cache();
						//location.reload(true);
					},
					default:company
				});

				let field1 = this.page.add_field({
					label: 'Payroll Entry',
					fieldtype: 'Link',
					fieldname: 'payroll_entry',
					options: 'Payroll Entry',
					change() {
						load_tab(wrapper);
					},
					get_query: function(){ return {'filters': [['Payroll Entry', 'company','=',field.get_value()]]}},
					default:payroll_entry
				});
				
				let field2 = this.page.add_field({
					label: 'Month',
					fieldtype: 'Date',
					fieldname: 'start_date',
					change() {
						load_tab(wrapper);
					},
					
				});
		
				/*let field3 = this.page.add_field({
					label: 'Date To',
					fieldtype: 'Date',
					fieldname: 'to_date',
					change() {
						load_tab(wrapper);
					},
					
				}); */
				let field4 = this.page.add_field({
					label: 'Employer ID',
					fieldtype: 'Link',
					fieldname: 'mol',
					options: 'Ministry of Labor Employer ID',
					reqd: 1,
					change() {
						load_tab(wrapper);
					},
					get_query: function(){ return {'filters': [['Ministry of Labor Employer ID', 'parent','=',field.get_value()]]}}
				});
				let field5 = this.page.add_field({
					label: 'Employee',
					fieldtype: 'Link',
					fieldname: 'employee',
					options: 'Employee',
					change() {
						load_tab(wrapper);
					},
					get_query: function(){ return {'filters': [['Employee', 'company','=',field.get_value()]]}}
				});
		
				//field2.set_value(frappe.datetime.month_start());
				//field3.set_value(frappe.datetime.get_today());
				var date_to=field2.get_value()
				
				if((date_to=='' || typeof(date_to)=='undefined') && payroll_entry)
				{
					frappe.db.get_value('Payroll Entry', payroll_entry, 'start_date')
					.then(r => {
						console.log(r.message.start_date) // Open
						field2.set_value(r.message.start_date);
					})
					
				}
				
				this.page.add_inner_button('Download', () => download_rep());
				let data={'company':field.get_value()};
				var pg=this.page.main;
				
				function load_tab(wrapper){
					
					frappe.call({
						method: 'custom_reports.custom_reports.page.sif_file.sif_file.get_report',
						args: {
							company: field.get_value(),
							payroll_entry: field1.get_value(),
							start_date: field2.get_value(),
							mol: field4.get_value(),
							employee: field5.get_value(),
						},
						callback: function (r) {
						if (r.message) {
							$(wrapper).find(".sif").remove();
							//data={'company':field.get_value(),'slip':r.message};
							$(frappe.render_template("sif_file",r.message)).appendTo(pg);
							
						}
						},
					}); 
		
				}
				//load_tab();
				
				function download_rep()
				{
					if(field4.get_value()=='' || typeof(field4.get_value())=='undefined') 
					{
						frappe.throw(__('Please select Employer id provided by Ministry of Labor'));
					}	

					frappe.call({
						method: "custom_reports.custom_reports.page.sif_file.sif_file.down_report",
						args: {
							company: field.get_value(),
							payroll_entry: field1.get_value(),
							start_date: field2.get_value(),
							mol: field4.get_value(),
							employee: field5.get_value(),	
						},
						callback: function(response) {
						  var files = response.message;
						  //window.open("/api/method/livestock.poultry.page.poultry_dashbord.poultry_dashbord.down_file");
						  let url='/api/method/custom_reports.custom_reports.page.sif_file.sif_file.down_file';
						  open_url_post(url, {file: files}); 
						}
					  }); 
		
					  
				}
				
				
				
			}
		
		
		})