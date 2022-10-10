

frappe.pages['comments'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}

		MyPage =Class.extend({
	
			init: function(wrapper){
					this.page = frappe.ui.make_app_page({
					parent: wrapper,
					title: 'Comments',
					single_column: true
				});
					this.make();
			},
			make: function()
			{
				this.page.add_inner_button('Mark All As Read', () => mark_all());
				var wrp=this.page.main
				frappe.call({
					method: 'custom_reports.custom_reports.page.comments.comments.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',					
					callback: function (r) {
					  if (r.message) {							
							$(frappe.render_template("comments",r.message)).appendTo(wrp);	
					  }
					},
				  });
				
			}
		
		
		})
function set_read(com)
{
	
	frappe.call({
		method: "frappe.desk.doctype.notification_log.notification_log.mark_as_read",
		args: {docname:com},
	});
	
}

function mark_all()
{
	frappe.call({
		method: "frappe.desk.doctype.notification_log.notification_log.mark_all_as_read",
	});
	
	setTimeout(window.location.reload(), 3000);
}