// Copyright (c) 2022, alantech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Request', {
	 refresh: function(frm) {
		frm.fields_dict['expense'].grid.get_field("employee").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Employee', 'company', '=', frm.doc.company],			
				]
			}
		}
	 }
});

frappe.ui.form.on('Expense Request Item', {
    
    employee(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
		let yeardu=0;
		let typarry=['Visa Expenses','EID','Medical','Labour Permit','Resident Permit'];
		if(row.date && row.expense_claim_type && row.employee){
			if(row.expense_claim_type=='Medical Insurance')
			{
				yeardu=1;
			}
			else if(typarry.includes(row.expense_claim_type))
			{
				yeardu=2;
			}
			if(yeardu)
			{
				frappe.call({
					method: 'custom_reports.api.validate_expense',
						args: {
							'exp_year': yeardu,
							'exp_date': row.date,
							'employee': row.employee,
					},
					callback: function(data) {
						if(data.message)
						{
							frappe.throw('Select employee expense canot be added with this date');

						}
					}
				});
			}
		}
		
    },
	expense_claim_type(frm, cdt, cdn)
	{
		let row = frappe.get_doc(cdt, cdn);
		let yeardu=0;
		let typarry=['Visa Expenses','EID','Medical','Labour Permit','Resident Permit'];
		if(row.date && row.expense_claim_type && row.employee){
			if(row.expense_claim_type=='Medical Insurance')
			{
				yeardu=1;
			}
			else if(typarry.includes(row.expense_claim_type))
			{
				yeardu=2;
			}
			if(yeardu)
			{

				frappe.call({
					method: 'custom_reports.api.validate_expense',
						args: {
							'exp_year': yeardu,
							'exp_date': row.date,
							'employee': row.employee,
					},
					callback: function(data) {
						if(data.message)
						{
							frappe.throw('Select employee expense canot be added with this date');

						}
					}
				});
			}
		}

	},
	date(frm, cdt, cdn)
	{
		let row = frappe.get_doc(cdt, cdn);
		let yeardu=0;
		let typarry=['Visa Expenses','EID','Medical','Labour Permit','Resident Permit'];
		if(row.date && row.expense_claim_type && row.employee){
			if(row.expense_claim_type=='Medical Insurance')
			{
				yeardu=1;
			}
			else if(typarry.includes(row.expense_claim_type))
			{
				yeardu=2;
			}
			if(yeardu)
			{
				frappe.call({
					method: 'custom_reports.api.validate_expense',
						args: {
							'exp_year': yeardu,
							'exp_date': row.date,
							'employee': row.employee,
					},
					callback: function(data) {
						if(data.message)
						{
							frappe.throw('Select employee expense canot be added with this date');

						}
					}
				});
			}
		}

	}
});






