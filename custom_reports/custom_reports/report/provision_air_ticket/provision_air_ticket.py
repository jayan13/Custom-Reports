# Copyright (c) 2022, alantech and contributors
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
		"fieldname": "employee",
		"fieldtype": "Link",
		"label": "Employee",
		"options": "Employee",	
		"width": 200
		},
		{
		"fieldname": "employee_name",
		"fieldtype": "Data",
		"label": "Employee Name",	
		"width": 200
		},
		{
		"fieldname": "perodical",
		"fieldtype": "Data",
		"label": "Perodical",	
		"width": 80
		},
		{
		"fieldname": "ticket_per_month",
		"fieldtype": "Data",
		"label": "Ticket Per Month",	
		"width": 80
		},
		{
		"fieldname": "ticket_price",
		"fieldtype": "Data",
		"label": "Ticket Fare ",	
		"width": 100
		},
		{
		"fieldname": "date_of_joining",
		"fieldtype": "Date",
		"label": "Date of Joining",	
		"width":100
		},
		{
		"fieldname": "total_days",
		"fieldtype": "Data",
		"label": "Total Days ",	
		"width": 80
		},
		{
		"fieldname": "absent",
		"fieldtype": "Data",
		"label": "Absent ",	
		"width": 80
		},
		{
		"fieldname": "actual_worked",
		"fieldtype": "Data",
		"label": "Actual Worked ",	
		"width": 80
		},
		{
		"fieldname": "years",
		"fieldtype": "Data",
		"label": "Years ",	
		"width": 80
		},
		{
		"fieldname": "eligible",
		"fieldtype": "Data",
		"label": "Eligible ",	
		"width": 80
		},
		{
		"fieldname": "accrued",
		"fieldtype": "Data",
		"label": "Accrued ",	
		"width": 80
		},
		{
		"fieldname": "used_tickets",
		"fieldtype": "Data",
		"label": "Used ",	
		"width": 80
		},
		{
		"fieldname": "balance",
		"fieldtype": "Data",
		"label": "Balance ",	
		"width": 80
		},
		{
		"fieldname": "amount_balance",
		"fieldtype": "Data",
		"label": "Amount Balance",	
		"width": 100
		},
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	processing_month=filters.get("processing_month")
	conc=frappe.db.sql(""" select * from `tabEmployee` where  %s  """% (conditions),as_dict=1,debug=1)
	for emp in conc:
		total_days=frappe.utils.date_diff(processing_month,emp.date_of_joining)
		absents=getabsents(emp.name,emp.opening_absent)		
		actual_worked=total_days-absents
		years=total_days/365
		perodical='Once in a '+emp.ticket_period+' Years'
		ticket_per_month=0
		eligible=0
		accrued=0
		amount_balance=0
		balance=0
		
		if float(emp.ticket_period) > 0:
			ticket_per_month=1/(float(emp.ticket_period)*12)
			eligible=years//float(emp.ticket_period)
			accrued=years/float(emp.ticket_period)
		
		balance=accrued-emp.used_tickets
		
		if float(emp.ticket_period) > 0:
			amount_balance=(emp.ticket_price/float(emp.ticket_period))*balance

		emp.update({'perodical':perodical})
		emp.update({'ticket_per_month':ticket_per_month})
		emp.update({'total_days':total_days})
		emp.update({'absent':absents})
		emp.update({'actual_worked':actual_worked})
		emp.update({'years':years})
		emp.update({'eligible':eligible})
		emp.update({'accrued':accrued})
		emp.update({'balance':balance})
		emp.update({'amount_balance':amount_balance})
	return conc

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)
	if filters.get("processing_month"):
		processing_month=filters.get("processing_month")
		#conditions += " and DATE(s.posting_date) >= '{0}' ".format(date_from)
	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += "  and employee = '{0}'".format(employee)

	return conditions

def get_gross_salary(emp,processing_month):
	salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':emp,'from_date':['<=',processing_month]},'salary_structure',debug=0)
	gsal=0
	sal=frappe.db.sql(""" select sum(amount) as gross_salary from `tabSalary Detail` where parent='%s' and parentfield='earnings'  group by parent"""% (salary_structure),as_dict=1,debug=0)
	if sal:
		gsal=sal[0].gross_salary
	return gsal

def getabsents(emp,opn):
	absent=0
	sal=frappe.db.sql(""" select sum(l.total_leave_days)+{0} as absent from `tabLeave Application` l left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{1}' and p.is_lwp='1' and l.status='Approved' group by l.employee""".format(opn,emp),as_dict=1,debug=0)
	if sal:
		absent=sal[0].absent
	return absent

