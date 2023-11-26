// Copyright (c) 2023, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Entry', {
	 refresh: function(frm) {
		if (frm.doc.salary_slips_submitted || (frm.doc.__onload && frm.doc.__onload.submitted_ss)) {
			frm.add_custom_button(__("SIF Download"), function () {
				
				//let url='/api/method/custom_reports.custom_reports.page.sif_file.sif_file.down_report';
				//open_url_post(url, {company:frm.doc.company,payroll: frm.doc.name}); 

				var base_url = window.location.origin;
                var url=base_url+'/app/sif-file/'+frm.doc.company+'/'+frm.doc.name
				window.open(url, '_blank');

			}).addClass("btn-primary");
		} 
	 }
});
