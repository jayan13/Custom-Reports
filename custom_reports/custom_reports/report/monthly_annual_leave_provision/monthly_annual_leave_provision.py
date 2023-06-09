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
	return get_columns(filters), get_data(conditions,filters)

def get_columns(filters):
	
	columns = [
		{
		"fieldname": "employee",
		"fieldtype": "Link",
		"label": "Employee No",
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
		"fieldname": "leave_provision_date",
		"fieldtype": "Data",
		"label": "Provision Date ",	
		"width": 80
		},		
		{
		"fieldname": "total_days",
		"fieldtype": "Currency",
		"label": "Total Days ",	
		"width": 80
		},
		{
		"fieldname": "absent",
		"fieldtype": "Currency",
		"label": "Absent ",	
		"width": 80
		},
		{
		"fieldname": "used",
		"fieldtype": "Currency",
		"label": "Used ",	
		"width": 80
		},
		{
		"fieldname": "actual_worked",
		"fieldtype": "Currency",
		"label": "Actual Worked ",	
		"width": 80
		},		
		{
		"fieldname": "accrued",
		"fieldtype": "Currency",
		"label": "Accrued ",	
		"width": 80
		},		
		{
		"fieldname": "amount_accrued",
		"fieldtype": "Currency",
		"label": "Amount Accrued",	
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
	date_from=filters.get("date_from")
	date_to=processing_month
	alrules=get_provision_rule(company,date_from,0)
	applicable_earnings_component=get_applicable_components(alrules.name)
	

	departmentname=''
	for emp in conc:
		processing_month=filters.get("processing_month") #update relaving history
		if emp.relieving_date and emp.relieving_date < getdate(processing_month):
			processing_month=emp.relieving_date
		date_to=processing_month
		
		if emp.parent_department=='All Departments':
			emp.parent_department=emp.department_name.split('-')[0]

		departmentname=emp.department_name.split('-')[0]
		if emp.parent_department != parent_department:
			parent_department=emp.parent_department
			parent_department_tot=0
			parent_department_emp_tot=0
			
		if emp.department_name != department_name:
			department_name=emp.department_name
			department_name_tot=0
			department_name_emp_tot=0				
		#leave_provision_date
		totleave=emp.leaves_per_year
		tot_leave=get_leave_no(emp.name,processing_month)
		if tot_leave:
			totleave=tot_leave.new_leaves_allocated
			
		gross_salary=get_total_applicable_component_amount(emp.name, applicable_earnings_component, date_to)
		total_days=date_diff(date_to,date_from)+1
		absents=getabsents(emp.name,0,date_from,date_to)			
		usedleaves=getused(emp.name,0,date_from,date_to)
		actual_worked=float(total_days)-float(absents)-float(usedleaves)
		accrued=round(round(float(totleave)/365,4)*actual_worked,4)
		amount_accrued=round(((gross_salary*12)/365)*accrued,2)
		leave_code=str(totleave)+'D'
		
		accrued=round(accrued,3)		
		amount_accrued=round(amount_accrued,2)
		
		parent_department_tot+=amount_accrued
		department_name_tot+=amount_accrued
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})
		emp.update({'department_name':departmentname})
		emp.update({'total_days':total_days})		
		emp.update({'gross_salary':gross_salary})
		emp.update({'absent':absents})
		emp.update({'leave_code':leave_code})
		emp.update({'actual_worked':actual_worked})
		emp.update({'accrued':accrued})
		emp.update({'used':usedleaves})
		emp.update({'amount_accrued':amount_accrued})
		
		data.append(emp)
	return data


def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and e.company= '{0}' ".format(company)
		conditions += " and d.company= '{0}' ".format(company)
	if filters.get("processing_month"):
		processing_month=filters.get("processing_month")
		conditions += " and (e.status='Active' OR (e.status='Left' and (e.relieving_date >= '{0}' OR (MONTH(e.relieving_date)=MONTH('{0}') and YEAR(e.relieving_date)=YEAR('{0}') ) ))) and e.date_of_joining <= '{0}' ".format(processing_month)
	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += "  and e.employee = '{0}'".format(employee)

	return conditions

def get_gross_salary(emp,company,processing_month):
	gsal=0
	rule=get_provision_rule(company,processing_month,0)
	#frappe.msgprint(str(rule))
	applicable_earnings_component=[]
	if rule:
		applicable_earnings_component=get_applicable_components(rule.name)

	gsal=get_total_applicable_component_amount(emp, applicable_earnings_component, processing_month)
	#salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':emp,'from_date':['<=',processing_month]},'salary_structure',debug=0)
	#sal=frappe.db.sql(""" select sum(amount) as gross_salary from `tabSalary Detail` where parent='%s' and parentfield='earnings'  group by parent"""% (salary_structure),as_dict=1,debug=0)
	#if sal:
	#	gsal=sal[0].gross_salary
	return gsal

def getabsents(emp,opn,start_date,end_date):
	absent=float(opn)
	sal3=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and a.attendance_date between '{1}' and  '{2}' and l.is_ppl='1' """.format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal3:
		absent+=float(sal3[0].absent)/2
	
	sal4=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and a.attendance_date between '{1}' and  '{2}' and l.is_lwp='1' """.format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal4:
		absent+=sal4[0].absent
	
	sal5=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where docstatus=1 and status='Absent' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}'""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal5:
		absent+=sal5[0].absent
	
	sal6=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='Half Day' and a.employee='{0}' and a.attendance_date between '{1}' and  '{2}' and (l.is_lwp='1' or l.is_ppl='1' ) """.format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal6:
		absent+=float(sal6[0].absent)/2
	
	return absent

def getused(emp,opn,start_date,end_date):
	used=float(opn)

	sal=frappe.db.sql(""" select count(*) as used FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and a.attendance_date between '{1}' and  '{2}' and a.leave_type='Annual Leave' """.format(emp,start_date,end_date),as_dict=1,debug=0)
	
	if sal:
		used+=sal[0].used
		
	return used

#========================================================
def get_total_applicable_component_amount(employee, applicable_earnings_component, processing_month):
	#sal_slip = get_last_salary_slip(employee,processing_month)
	sal_slip=''
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
	#if employee in ['5076','5078','5077']:
	#	frappe.msgprint(employee+' - '+str(total_applicable_components_amount))
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

def get_provision_rule(company,processing_month='',all=1):
	if processing_month=='':
		set = frappe.db.sql(""" select name,date_from,date_to from `tabProvision Annual Leave Setting` where company='{0}'  order by creation """.format(company,processing_month),as_dict=1,debug=0)
		if not set:
			set = frappe.db.sql(""" select name,date_from,date_to from `tabProvision Annual Leave Setting` where company=''  order by creation """.format(processing_month),as_dict=1,debug=0)
	else:
		set = frappe.db.sql(""" select name,date_from,date_to from `tabProvision Annual Leave Setting` where company='{0}' and 
	((date_to is null and date_from is not null and date_from <= '{1}') 
	or (date_from is null and date_to is not null and date_to >= '{1}')
	or (date_from is not null and date_to is not null and '{1}' between date_from and date_to)) order by creation """.format(company,processing_month),as_dict=1,debug=0)
		if not set:
			set = frappe.db.sql(""" select name,date_from,date_to from `tabProvision Annual Leave Setting` where company='' and 
	((date_to is null and date_from is not null and date_from <= '{0}') 
	or (date_from is null and date_to is not null and date_to >= '{0}') 	or (date_from is not null and date_to is not null and '{0}' between date_from and date_to) ) order by creation """.format(processing_month),as_dict=1,debug=0)
	
	if not set:
		return
	if all:
		val=set
	else:
		val=set[0]

	return val

def get_leave_no(emp,processing_month):
	
	set = frappe.db.sql(""" select new_leaves_allocated,unused_leaves from `tabLeave Allocation` where employee='{0}' 
	and '{1}' between from_date and to_date and leave_type='Annual Leave' """.format(emp,processing_month),as_dict=1,debug=0)
	if not set:
		return
	return set[0]