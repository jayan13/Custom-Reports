# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data(conditions,filters)

def get_columns():
	
	columns = [
		{
		"fieldname": "department",
		"fieldtype": "Link",
		"label": "Department",
		"options": "Department",			
		"width": 200
		},
		{
		"fieldname": "particular",
		"fieldtype": "Link",
		"label": "Particulars",	
		"width": 200
		},
		{
		"fieldname": "dr",
		"fieldtype": "Data",
		"label": "Dr.",	
		"width": 150
		},
		{
		"fieldname": "cr",
		"fieldtype": "Data",
		"label": "Cr.",	
		"width": 150
		},
		{
		"fieldname": "balance",
		"fieldtype": "Currency",
		"label": "Balance",	
		"width": 150
		},
		
		
 	 ]	
	    
		
	return columns

def get_data(conditions,filters):
	data=[]
	date_from=filters.get("date_from")
	date_to=filters.get("date_to")
	company=filters.get("company")
	conc=frappe.db.sql(""" select * from `tabDepartment` where %s  order by name"""% (conditions),as_dict=1,debug=0)
	for dept in conc:
		
		earnings=[]
		deductions=[]
		gross_pay=0
		total_deduction=0
		tot_ern=0
		slip=frappe.db.sql(""" select name,gross_pay from `tabSalary Slip` where company='{0}' and department='{1}' and posting_date between '{2}' and '{3}' """.format(company,dept.name,date_from,date_to),as_dict=1,debug=0)
		if slip:
			slipname=[]
			for slp in slip:
				slipname.append(slp.name)
				gross_pay+=float(slp.gross_pay or 0)
				total_deduction+=float(slp.total_deduction or 0)
				tot_ern+=float(slp.gross_pay or 0)+float(slp.total_deduction or 0)
			if len(slipname):
				slips="','".join([str(elem) for elem in slipname])

			earnings=frappe.db.sql(""" select salary_component,sum(amount) as amount from `tabSalary Detail` where parentfield='earnings' and parent in '{0}'  group by salary_component""".format(slips),as_dict=1,debug=0)
			deductions=frappe.db.sql(""" select salary_component,sum(amount) as amount from `tabSalary Detail` where parentfield='deductions' and parent in '{0}' group by salary_component""".format(slips),as_dict=1,debug=0)
		
		if len(earnings):
			for er in earnings:
				dt={}
				dt.update({'particular':er.salary_component})
				dt.update({'dr':er.amount})
				dt.update({'cr':'0'})
				dt.update({'department':dept.name})
				dt.update({'parent':dept.parent_department})
				dt.update({'gross_pay':gross_pay})
				dt.update({'tot_ern':tot_ern})
				dt.update({'balance':gross_pay})
				data.append(dt)
		if len(deductions):	
			for de in deductions:
				dt={}
				dt.update({'particular':de.salary_component})
				dt.update({'dr':'0'})
				dt.update({'cr':de.amount})
				dt.update({'department':dept.name})
				dt.update({'parent':dept.parent_department})
				dt.update({'gross_pay':gross_pay})
				dt.update({'tot_ern':tot_ern})
				dt.update({'balance':gross_pay})
				data.append(dt)		
			
		

	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)		
	
	if filters.get("department"):
		department=filters.get("department")
		conditions += "  and name = '{0}'".format(department)

	return conditions