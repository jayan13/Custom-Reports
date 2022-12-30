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
		"fieldname": "leave_code",
		"fieldtype": "Data",
		"label": "Leave Code",	
		"width": 100
		},		
		{
		"fieldname": "gross_salary",
		"fieldtype": "Data",
		"label": "Gross Salary ",	
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
		"fieldname": "accrued",
		"fieldtype": "Data",
		"label": "Accrued ",	
		"width": 80
		},
		{
		"fieldname": "used",
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
	company=filters.get("company")
	conc=frappe.db.sql(""" select e.*,d.parent_department,d.department_name from `tabEmployee` e left join `tabDepartment` d on e.department=d.name where  %s  order by d.parent_department,d.name"""% (conditions),as_dict=1,debug=0)
	
	data=[]
	parent_department=''
	department_name=''
	parent_department_tot=0
	department_name_tot=0
	parent_department_emp_tot=0
	department_name_emp_tot=0
	#Provision Annual Leave Setting
	for emp in conc:
		if emp.parent_department != parent_department:
			parent_department=emp.parent_department
			parent_department_tot=0
			parent_department_emp_tot=0
		if emp.department_name != department_name:
			department_name=emp.department_name
			department_name_tot=0
			department_name_emp_tot=0		
		
		start_date=emp.date_of_joining
		openabs=0
		opnused=0
		cf_leave=0
		if emp.openning_entry_date:
			day = getdate(emp.openning_entry_date)
			start_date = add_days(day, 1)
			openabs=emp.opening_absent
			opnused=emp.opening_used_leaves
		totleave=get_leave_no(emp.name,processing_month)
		leaves_per_year=emp.leaves_per_year
		if totleave:
			leaves_per_year=totleave
		
		total_days=date_diff(processing_month,emp.date_of_joining)+1
		gross_salary=get_gross_salary(emp.name,company,processing_month)
		absents=getabsents(emp.name,openabs,start_date,processing_month)
		usedleave=getused(emp.name,opnused,start_date,processing_month)
		leave_code=str(leaves_per_year)+'D'
		actual_worked=total_days-absents
		accrued=round((actual_worked/365)*leaves_per_year,4)
		balance=accrued-usedleave
		amount_balance=round(((gross_salary*12)/365)*balance,2)
		parent_department_tot+=amount_balance
		department_name_tot+=amount_balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})
		emp.update({'total_days':total_days})
		emp.update({'gross_salary':gross_salary})
		emp.update({'absent':absents})
		emp.update({'leave_code':leave_code})
		emp.update({'actual_worked':actual_worked})
		emp.update({'accrued':accrued})
		emp.update({'used':usedleave})
		emp.update({'balance':balance})
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

def get_gross_salary(emp,company,processing_month):
	gsal=0
	rule=get_provision_rule(company,processing_month)
	applicable_earnings_component=[]
	if rule:
		applicable_earnings_component=get_applicable_components(rule)

	gsal=get_total_applicable_component_amount(emp, applicable_earnings_component, processing_month)
	#salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':emp,'from_date':['<=',processing_month]},'salary_structure',debug=0)
	#sal=frappe.db.sql(""" select sum(amount) as gross_salary from `tabSalary Detail` where parent='%s' and parentfield='earnings'  group by parent"""% (salary_structure),as_dict=1,debug=0)
	#if sal:
	#	gsal=sal[0].gross_salary
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

def getused(emp,opn,start_date,end_date):
	used=float(opn)
	sal=frappe.db.sql(""" select sum(total_leave_days) as used from `tabLeave Application` where employee='{0}' 
	and status='Approved' and leave_type='Annual Leave' and from_date >= '{1}' and to_date <= '{2}' group by employee""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal:
		used+=sal[0].used

	sal3=frappe.db.sql(""" select to_date as used from `tabLeave Application` where employee='{0}' 
	and status='Approved' and leave_type='Annual Leave' and '{1}' between from_date and to_date """.format(emp,start_date),as_dict=1,debug=0)
	if sal3:
		for s in sal3:
			dc=date_diff(s.used,start_date)
			used+=dc

	sal4=frappe.db.sql(""" select from_date as used from `tabLeave Application` where employee='{0}' 
	and status='Approved' and leave_type='Annual Leave' and '{1}' between from_date and to_date """.format(emp,end_date),as_dict=1,debug=0)
	if sal4:
		for s in sal4:
			dc=date_diff(end_date,s.used)
			used+=dc
			
	return used

#========================================================
def get_total_applicable_component_amount(employee, applicable_earnings_component, processing_month):
	sal_slip = get_last_salary_slip(employee,processing_month)
	sal_stru = get_last_salary_structure(employee,processing_month)
	pare= sal_slip or sal_stru
	component_and_amounts=''
	if pare:
		if len(applicable_earnings_component):
			component_and_amounts = frappe.get_all(
			"Salary Detail",
			filters={
				"docstatus": 1,
				"parent": pare,
				"parentfield": "earnings",
				"salary_component": ("in", applicable_earnings_component),
			},
			fields=["amount"],debug=0
			)
		else:
			component_and_amounts = frappe.get_all(
			"Salary Detail",
			filters={
				"docstatus": 1,
				"parent": pare,
				"parentfield": "earnings",
			},
			fields=["amount"],
			)

	total_applicable_components_amount = 0

	for data in component_and_amounts:
		total_applicable_components_amount += data.amount
	return total_applicable_components_amount

def get_last_salary_slip(employee,processing_month):
	salary_slips = frappe.get_list(
		"Salary Slip", filters={"employee": employee, "docstatus": 1,'start_date':['<=',processing_month]}, order_by="start_date desc"
	)
	if not salary_slips:
		return
	return salary_slips[0].name

def get_last_salary_structure(employee,processing_month):

	salary_structure = frappe.get_list(
		"Salary Structure Assignment", filters={"employee": employee, "docstatus": 1,'from_date':['<=',processing_month]},fields=['salary_structure'], order_by="from_date desc"
	)
	if not salary_structure:
		return
	return salary_structure[0].salary_structure

def get_applicable_components(rule):
	applicable_earnings_components = frappe.get_all(
		"Provision Applicable Component", filters={"parent": rule}, fields=["salary_component"],debug=0)
	applicable_earnings_component = []
	if len(applicable_earnings_components):		
		applicable_earnings_component = [
		component.salary_component for component in applicable_earnings_components
		]

	return applicable_earnings_component

def get_provision_rule(company,processing_month):
	set = frappe.db.sql(""" select name from `tabProvision Annual Leave Setting` where company='{0}' and 
	((date_to = '' and date_from != '' and date_from <= '{1}') 
	or (date_from = '' and date_to != '' and date_to >= '{1}')
	or (date_from != '' and date_to != '' and '{1}' between date_from and date_to)) """.format(company,processing_month),as_dict=1,debug=0)
	if not set:
		set = frappe.db.sql(""" select name from `tabProvision Annual Leave Setting` where company='' and 
	((date_to = '' and date_from != '' and date_from <= '{1}') 
	or (date_from = '' and date_to != '' and date_to >= '{1}') 
	or (date_from != '' and date_to != '' and '{1}' between date_from and date_to) ) """.format(processing_month),as_dict=1,debug=0)
	if not set:
		return
	return set[0].name

def get_leave_no(emp,processing_month):
	
	set = frappe.db.sql(""" select new_leaves_allocated,unused_leaves from `tabLeave Allocation` where employee='{0}' 
	and '{1}' between from_date and to_date """.format(emp,processing_month),as_dict=1,debug=0)
	if not set:
		return
	return set[0].new_leaves_allocated