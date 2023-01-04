# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_link_to_form,
	get_datetime,
	get_first_day,
	getdate,
	money_in_words,
	rounded,
)
from erpnext.hr.utils import get_holiday_dates_for_employee

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
		"fieldname": "parent_department",
		"fieldtype": "Data",
		"label": "Main Department",	
		"width": 150
		},
		{
		"fieldname": "department_name",
		"fieldtype": "Data",
		"label": "Department",	
		"width": 150
		},
		{
		"fieldname": "perodical",
		"fieldtype": "Data",
		"label": "Perodical",	
		"width": 150
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
		"fieldname": "amount_accrued",
		"fieldtype": "Data",
		"label": "Amount Accrued",	
		"width": 100
		},
		{
		"fieldname": "amount_used",
		"fieldtype": "Data",
		"label": "Amount Used",	
		"width": 100
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
	conc=frappe.db.sql(""" select e.*,d.parent_department,d.department_name from `tabEmployee` e left join `tabDepartment` d on e.department=d.name where  %s  order by d.parent_department,d.name"""% (conditions),as_dict=1,debug=0)

	data=[]
	parent_department=''
	department_name=''
	parent_department_tot=0
	department_name_tot=0
	parent_department_emp_tot=0
	department_name_emp_tot=0
	for emp in conc:
		
		if emp.parent_department != parent_department:
			parent_department=emp.parent_department
			parent_department_tot=0
			parent_department_emp_tot=0
		if emp.department_name != department_name:
			department_name=emp.department_name
			department_name_tot=0
			department_name_emp_tot=0

		perodical=''
		ticket_per_month=0
		amount_balance=0
		usedno=0
		usedpri=0
		amount_used=0
		amount_accrued=0
		balance=0
		accrued=0
		eligible=0
		years=0
		actual_worked=0
		total_days=0
		absents=0
		perodical=str(emp.no_of_tickets_eligible)+"'s in a "+emp.ticket_period+' Years'

		if emp.openning_entry_date:
			openabs=0
			if getdate(processing_month)>emp.openning_entry_date:
				total_days=frappe.utils.date_diff(processing_month,emp.openning_entry_date)
			
			if total_days > 0 and float(emp.ticket_period) > 0:
				day = getdate(emp.openning_entry_date)
				start_date = add_days(day, 1)
				absents=getabsents(emp.name,openabs,start_date,processing_month)
				actual_worked=total_days-absents
				years=round(actual_worked/365,3)
				accrued=round(years/float(emp.ticket_period),3)*emp.no_of_tickets_eligible
				used=get_ticket_issued(emp.name,start_date)
				if used:
					usedno=used.ticket_no or 0
					usedpri=used.total_air_fare or 0
			
			opn_acc=round(float(emp.opening_ticket_balance)+float(emp.used_tickets),2)			
			balance=round((accrued+float(emp.opening_ticket_balance))-float(usedno),3)	
			amount_accrued=round(accrued*emp.ticket_price,2)
			accrued+=round(opn_acc,3)			
			amount_accrued+=round(emp.opening_ticket_amount_used+emp.opening_ticket_balance_amount,2)
			amount_used=usedpri
			amount_used+=float(emp.opening_ticket_amount_used)
			if total_days > 0:
				amount_balance=round(emp.ticket_price*balance,2)
			else:
				amount_balance=float(emp.opening_ticket_balance_amount)
			
			absents+=float(emp.opening_absent)
			working_before_opn=frappe.utils.date_diff(emp.openning_entry_date,emp.date_of_joining)+1
			total_days+=working_before_opn
			actual_worked+=working_before_opn-float(emp.opening_absent)
			years+=round(actual_worked/365,3)
			if float(emp.ticket_period) > 0:
				eligible=(years//float(emp.ticket_period))*emp.no_of_tickets_eligible

		
		parent_department_tot+=amount_balance
		department_name_tot+=amount_balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})		
		emp.update({'perodical':perodical})		
		emp.update({'total_days':total_days})
		emp.update({'absent':absents})
		emp.update({'actual_worked':actual_worked})
		emp.update({'years':years})
		emp.update({'eligible':eligible})
		emp.update({'accrued':accrued})		
		emp.update({'balance':balance})
		emp.update({'amount_accrued':amount_accrued})
		emp.update({'amount_used':amount_used})
		emp.update({'amount_balance':amount_balance})
		data.append(emp)
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and e.company= '{0}' ".format(company)
	if filters.get("processing_month"):
		processing_month=filters.get("processing_month")
		#conditions += " and DATE(s.posting_date) >= '{0}' ".format(date_from)
	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += "  and e.employee = '{0}'".format(employee)

	return conditions

def get_gross_salary(emp,processing_month):
	salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':emp,'from_date':['<=',processing_month]},'salary_structure',debug=0)
	gsal=0
	sal=frappe.db.sql(""" select sum(amount) as gross_salary from `tabSalary Detail` where parent='%s' and parentfield='earnings'  group by parent"""% (salary_structure),as_dict=1,debug=0)
	if sal:
		gsal=sal[0].gross_salary
	return gsal

def getabsents(emp,opn,start_date,end_date):
	absent=float(opn)
	sal=frappe.db.sql(""" select sum(l.total_leave_days) as absent from `tabLeave Application` l 
	left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{0}' and p.is_lwp='1' 
	and l.status='Approved' and l.from_date >= '{1}' and l.to_date <= '{2}' group by l.employee""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal:
		absent+=sal[0].absent
	
	sal2=frappe.db.sql(""" select sum(l.total_leave_days) as absent from `tabLeave Application` l 
	left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{0}' and p.is_ppl='1' 
	and l.status='Approved' and l.from_date >= '{1}' and l.to_date <= '{2}' group by l.employee""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal2:
		absent+=sal2[0].absent

	sal3=frappe.db.sql(""" select l.to_date as absent from `tabLeave Application` l 
	left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{0}' and p.is_lwp='1' 
	and l.status='Approved' and  '{1}' between l.from_date and l.to_date """.format(emp,start_date),as_dict=1,debug=0)
	if sal3:
		for s in sal3:
			dc=date_diff(s.absent,start_date)
			absent+=dc

	sal4=frappe.db.sql(""" select l.from_date as absent from `tabLeave Application` l 
	left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{0}' and p.is_lwp='1' 
	and l.status='Approved' and '{1}' between l.from_date and l.to_date """.format(emp,end_date),as_dict=1,debug=0)
	if sal4:
		for s in sal4:
			dc=date_diff(end_date,s.absent)
			absent+=dc

	sal5=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where status='Absent' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}'""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal5:
		absent+=sal5[0].absent
	
	sal6=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where status='Half Day' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}' and leave_type=''""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal6:
		absent+=sal6[0].absent
	
	return absent

def get_ticket_issued(emp,from_date):
	ticket_no=0
	sal7=frappe.db.sql(""" select sum(no_of_ticket_given) as ticket_no,sum(total_air_fare) as total_air_fare FROM `tabAdvance Air Ticket Request` where  employee='{0}' 
	and request_date >='{1}' and  docstatus=1 and ticket_type='Company' group by employee""".format(emp,from_date),as_dict=1,debug=0)
	if sal7:
		return sal7
	return
	

