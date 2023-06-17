
frappe.pages['material-request-set'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}


var script = document.createElement("script");
script.src = '/assets/js/bootstrap-4-web.min.js';  // set its src to the provided URL
document.head.appendChild(script);

MyPage =Class.extend({
	
	init: function(wrapper){
			this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Material And Pro Request - Settlement Dashboard',
			single_column: true
		});
			this.make();
	},
	make: function()
	{
		const comarry=[];
		var company=frappe.defaults.get_user_default("Company");
		if(frappe.get_route()[1])
		{
			company=frappe.get_route()[1];
		}
		
			let field = this.page.add_field({
			label: 'Company',
			fieldtype: 'Link',
			fieldname: 'company',
			options: 'Company',
			default:company,
			change() {
				get_report();
			}
		});
		
		
		this.page.add_inner_button('Print', () => print_rep());
		
		let data='';
		$(frappe.render_template("material_request_set",data)).appendTo(this.page.main);

		
		
		function get_report()
		{
			
			if(field.get_value())
			{ 
				//reqsnd=1;
				frappe.call({
					method: 'custom_reports.custom_reports.page.material_request_set.material_request_set.get_report',
					freeze: 1,
					freeze_message: 'Data loading ...please waite',
					args: {
					  company: field.get_value()				  					  
					},
					callback: function (r) {
					  if (r.message) {
						
						 $('#dash').html(r.message);
						 
					  }
					},
				  }); 
			}
			
		}
		
		get_report();

		
	}
})

function print_rep()
				{
					
					var dash=document.getElementById('dash');
					
					  var newWin=window.open('','Print-Window');
					  newWin.document.open();
					  newWin.document.write('<html><style>table, th, td {border: 1px solid;border-collapse: collapse; } table{ width:100%;} table td{ text-align:right;} #rear-chart{display:none;}#layer-chart{display:none;} .table-secondary td,.table-secondary th {background-color: #d5d7d9;font-weight: bold;}  @media print { #prod{overflow-x:unset !important;} #rer{overflow-x:unset !important;} } </style><body onload="window.print()">'+dash.innerHTML+'</body></html>');
					  newWin.document.close();
					  setTimeout(function(){newWin.close();},10);
		  
				}