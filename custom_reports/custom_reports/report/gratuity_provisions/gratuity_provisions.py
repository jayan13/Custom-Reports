# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe
#from erpnext.payroll.doctype.gratuity.gratuity import calculate_work_experience_and_amount
#employee gratuity_rule  return current_work_experience amount
from math import floor
from frappe import _, bold
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
		"fieldname": "gross_salary",
		"fieldtype": "Currency",
		"label": "Base Amount",	
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
		"fieldname": "actual_worked",
		"fieldtype": "Currency",
		"label": "Actual Worked ",	
		"width": 80
		},
		{
		"fieldname": "accr_d",
		"fieldtype": "Data",
		"label": "Accrued Days ",	
		"width": 80
		},
		{
		"fieldname": "accrued",
		"fieldtype": "Currency",
		"label": "Accrued ",	
		"width": 80
		},
		{
		"fieldname": "paid",
		"fieldtype": "Currency",
		"label": "Paid ",	
		"width": 80
		},
		{
		"fieldname": "balance",
		"fieldtype": "Currency",
		"label": "Balance",	
		"width": 100
		},
		{
		"fieldname": "in_limit",
		"fieldtype": "data",
		"label": "Days Accrued Within Limit",	
		"width": 100
		},
		{
		"fieldname": "after_limit",
		"fieldtype": "data",
		"label": "Days Accrued After Limit",	
		"width": 100
		},
 	 ]	
	    
	return columns
accured_days=0  #global variable
def get_data(conditions,filters):
	processing_month=filters.get("processing_month")
	gratuity_rule=filters.get("gratuity_rule")
	#nationality
	conc=frappe.db.sql(""" select e.*,d.parent_department,d.department_name from `tabEmployee` e left join `tabDepartment` d on e.department=d.name where  %s  order by d.parent_department,d.name"""% (conditions),as_dict=1,debug=0)
	global accured_days
	data=[]
	parent_department=''
	department_name=''
	parent_department_tot=0
	department_name_tot=0
	parent_department_emp_tot=0
	department_name_emp_tot=0
	departmentname=''
	for emp in conc:
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
		total_days=date_diff(processing_month,emp.date_of_joining)+1
		#gross_salary=get_gross_salary(emp.name,processing_month)
		applicable_earnings_component = get_applicable_components(gratuity_rule)
		total_applicable_components_amount = get_total_applicable_component_amount(
		emp.name, applicable_earnings_component, gratuity_rule,processing_month
		)
		gross_salary=total_applicable_components_amount
		start_date=emp.date_of_joining
		openabs=0
		if emp.openning_entry_date:
			day = getdate(emp.openning_entry_date)
			start_date = add_days(day, 1)
			openabs=emp.opening_absent
		absents=get_nonworking_days(emp.name,openabs,start_date,processing_month)
		actual_worked=total_days-absents
		accrued=calculate_work_experience_and_amount(emp.name,gratuity_rule,processing_month,openabs)['amount']
		paid=0
		accrued=round(accrued,2)		
		balance=accrued-paid
		balance=round(balance,2)
		accr_d=round(accured_days,4)
		parent_department_tot+=balance
		department_name_tot+=balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		in_limit=accr_d
		after_limit=0
		if float(in_limit) > 105:
			in_limit=105
			after_limit=float(accr_d)-105
			after_limit=round(after_limit,4)

		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})			
		emp.update({'department_name':departmentname})
		emp.update({'total_days':total_days})
		emp.update({'gross_salary':gross_salary})
		emp.update({'absent':absents})
		emp.update({'actual_worked':actual_worked})
		emp.update({'accr_d':accr_d})
		emp.update({'accrued':accrued})		
		emp.update({'paid':paid})
		emp.update({'balance':balance})
		emp.update({'in_limit':in_limit})
		emp.update({'after_limit':after_limit})
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


@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule,processing_month,openabs):
	global accured_days
	accured_days=0
	current_work_experience = calculate_work_experience(employee, gratuity_rule,processing_month,openabs) or 0
	
	gratuity_amount = calculate_gratuity_amount(employee, gratuity_rule, current_work_experience,processing_month) or 0
	#frappe.msgprint('days='+str(accured_days))
	return {"current_work_experience": current_work_experience, "amount": gratuity_amount}


def calculate_work_experience(employee, gratuity_rule,processing_month,openabs):

	total_working_days_per_year, minimum_year_for_gratuity = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, ["total_working_days_per_year", "minimum_year_for_gratuity"]
	)

	date_of_joining, relieving_date = frappe.db.get_value(
		"Employee", employee, ["date_of_joining", "relieving_date"]
	)
	if not relieving_date:
		relieving_date=processing_month

	method = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, "work_experience_calculation_function"
	)
	#employee_total_workings_days = calculate_employee_total_workings_days(
	#	employee, date_of_joining, relieving_date
	#)
	total_workings_days = (get_datetime(relieving_date) - get_datetime(date_of_joining)).days+1
	employee_total_workings_days = get_nonworking_days(
		employee,openabs,date_of_joining, relieving_date
	)
	employee_total_workings_days=total_workings_days-employee_total_workings_days
	#frappe.msgprint(str(employee_total_workings_days))
	
	current_work_experience = employee_total_workings_days / total_working_days_per_year or 1
	current_work_experience = get_work_experience_using_method(
		method, current_work_experience, minimum_year_for_gratuity, employee
	)
	return current_work_experience


def calculate_employee_total_workings_days(employee, date_of_joining, relieving_date):
	employee_total_workings_days = (get_datetime(relieving_date) - get_datetime(date_of_joining)).days

	payroll_based_on = frappe.db.get_value("Payroll Settings", None, "payroll_based_on") or "Leave"
	if payroll_based_on == "Leave":
		total_lwp = get_non_working_days(employee, relieving_date, "On Leave")
		employee_total_workings_days -= total_lwp
	elif payroll_based_on == "Attendance":
		total_absents = get_non_working_days(employee, relieving_date, "Absent")
		employee_total_workings_days -= total_absents
	
	return employee_total_workings_days


def get_work_experience_using_method(
	method, current_work_experience, minimum_year_for_gratuity, employee
):
	if method == "Round off Work Experience":
		current_work_experience = round(current_work_experience)
	else:
		#current_work_experience = floor(current_work_experience)
		current_work_experience = current_work_experience

	if current_work_experience < minimum_year_for_gratuity:
		current_work_experience=0
		
	return current_work_experience


def get_non_working_days(employee, relieving_date, status):

	filters = {
		"docstatus": 1,
		"status": status,
		"employee": employee,
		"attendance_date": ("<=", get_datetime(relieving_date)),
	}

	if status == "On Leave":
		lwp_leave_types = frappe.get_list("Leave Type", filters={"is_lwp": 1})
		lwp_leave_types = [leave_type.name for leave_type in lwp_leave_types]
		filters["leave_type"] = ("IN", lwp_leave_types)

	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"])
	return record[0].total_lwp if len(record) else 0


def calculate_gratuity_amount(employee, gratuity_rule, experience,processing_month):
	global accured_days
	applicable_earnings_component = get_applicable_components(gratuity_rule)
	total_applicable_components_amount = get_total_applicable_component_amount(
		employee, applicable_earnings_component, gratuity_rule,processing_month
	)
	
	if experience > 5:
		gratuity_rule = 'Rule Under Limited Contract (UAE)'

	calculate_gratuity_amount_based_on = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, "calculate_gratuity_amount_based_on"
	)
	#frappe.msgprint(str(total_applicable_components_amount))
	#frappe.msgprint(str(calculate_gratuity_amount_based_on))
	gratuity_amount = 0
	slabs = get_gratuity_rule_slabs(gratuity_rule)
	slab_found = False
	year_left = experience
	
	
	
	
	for slab in slabs:
		if calculate_gratuity_amount_based_on == "Current Slab":
			slab_found, gratuity_amount = calculate_amount_based_on_current_slab(
				slab.from_year,
				slab.to_year,
				experience,
				total_applicable_components_amount,
				slab.fraction_of_applicable_earnings,
			)
			if slab_found:
				break

		elif calculate_gratuity_amount_based_on == "Sum of all previous slabs":
			if slab.to_year == 0 and slab.from_year == 0:
				#gratuity_amount += (
				#	year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
				#)
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)									
				gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)
				accured_days+=(year_left*day)
				slab_found = True
				break

			if experience > slab.to_year and experience > slab.from_year and slab.to_year != 0:
				#gratuity_amount += (
				#	(slab.to_year - slab.from_year)
				#	* total_applicable_components_amount
				#	* slab.fraction_of_applicable_earnings
				#)
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				yer=slab.to_year - slab.from_year		
				gratuity_amount += (yer*day)*((total_applicable_components_amount*12)/365)
				accured_days+=(yer*day)
				year_left -= slab.to_year - slab.from_year
				slab_found = True
				#frappe.msgprint(str(experience)+'-('+str(slab.from_year)+'-'+str(slab.to_year)+')-'+str(slab.fraction_of_applicable_earnings)+'*'+str(slab.to_year - slab.from_year)+'*'+str(total_applicable_components_amount))
			elif slab.from_year <= experience and (experience < slab.to_year or slab.to_year == 0):
				#gratuity_amount += (
				#	year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
				#)
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				accured_days+=(year_left*day)		
				gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)
				slab_found = True
				#frappe.msgprint(str(experience)+'-('+str(slab.from_year)+'-'+str(slab.to_year)+')-'+str(slab.fraction_of_applicable_earnings)+'*'+str(year_left)+'*'+str(total_applicable_components_amount))

	#if not slab_found:
	#	frappe.throw(
	#		_("No Suitable Slab found for Calculation of gratuity amount in Gratuity Rule: {0}").format(
	#			bold(gratuity_rule)
	#		)
#		)
	return gratuity_amount


def get_applicable_components(gratuity_rule):
	applicable_earnings_component = frappe.get_all(
		"Gratuity Applicable Component", filters={"parent": gratuity_rule}, fields=["salary_component"]
	)
	if len(applicable_earnings_component) == 0:
		frappe.throw(
			_("No Applicable Earnings Component found for Gratuity Rule: {0}").format(
				bold(get_link_to_form("Gratuity Rule", gratuity_rule))
			)
		)
	applicable_earnings_component = [
		component.salary_component for component in applicable_earnings_component
	]

	return applicable_earnings_component


def get_total_applicable_component_amount(employee, applicable_earnings_component, gratuity_rule,processing_month):
	sal_slip = get_last_salary_slip(employee)
	if not sal_slip:
		salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':employee,'from_date':['<=',processing_month]},'salary_structure',debug=0)
		component_and_amounts = frappe.get_all(
		"Salary Detail",
		filters={
			"docstatus": 1,
			"parent": salary_structure,
			"parentfield": "earnings",
			"salary_component": ("in", applicable_earnings_component),
		},
		fields=["amount"],
		)
	else:
		component_and_amounts = frappe.get_all(
		"Salary Detail",
		filters={
			"docstatus": 1,
			"parent": sal_slip,
			"parentfield": "earnings",
			"salary_component": ("in", applicable_earnings_component),
		},
		fields=["amount"],
		)
	total_applicable_components_amount = 0
	if not len(component_and_amounts):
		frappe.throw(_("No Applicable Component is present in last month salary slip"))
	for data in component_and_amounts:
		total_applicable_components_amount += data.amount
	return total_applicable_components_amount


def calculate_amount_based_on_current_slab(
	from_year,
	to_year,
	experience,
	total_applicable_components_amount,
	fraction_of_applicable_earnings,
):
	slab_found = False
	global accured_days
	gratuity_amount = 0
	if experience >= from_year and (to_year == 0 or experience < to_year):
		#gratuity_amount = (
		#	total_applicable_components_amount * experience * fraction_of_applicable_earnings
		#)
		day=fraction_of_applicable_earnings*30
		day=round(day)
		accured_days+=(experience*day)		
		gratuity_amount =(experience*day)*((total_applicable_components_amount*12)/365)
		#frappe.msgprint()
		#frappe.msgprint(str(day)+'*'+str(experience)+'*(('+str(total_applicable_components_amount)+'*12)/365)'+str(gratuity_amount)+')')
		if fraction_of_applicable_earnings:
			slab_found = True

	return slab_found, gratuity_amount


def get_gratuity_rule_slabs(gratuity_rule):
	return frappe.get_all(
		"Gratuity Rule Slab", filters={"parent": gratuity_rule}, fields=["*"], order_by="idx"
	)


def get_salary_structure(employee):
	return frappe.get_list(
		"Salary Structure Assignment",
		filters={"employee": employee, "docstatus": 1},
		fields=["from_date", "salary_structure"],
		order_by="from_date desc",
	)[0].salary_structure


def get_last_salary_slip(employee):
	salary_slips = frappe.get_list(
		"Salary Slip", filters={"employee": employee, "docstatus": 1}, order_by="start_date desc"
	)
	if not salary_slips:
		return
	return salary_slips[0].name



def get_nonworking_days(emp,opn,start_date,end_date):
	nwdays=float(opn)
	filters = {
		"docstatus": 1,
		"status": 'On Leave',
		"employee": emp,
		"attendance_date": ("between", [get_datetime(start_date),get_datetime(end_date)]),
	}
	
	lwp_leave_types = frappe.get_list("Leave Type", filters={"is_lwp": 1})
	lwp_leave_types = [leave_type.name for leave_type in lwp_leave_types]
	filters["leave_type"] = ("IN", lwp_leave_types)
	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"],debug=0)
	if record:
		nwdays += record[0].total_lwp if len(record) else 0

	filters = {
		"docstatus": 1,
		"status": 'Absent',
		"employee": emp,
		"attendance_date": ("between", [get_datetime(start_date),get_datetime(end_date)]),
	}
	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"],debug=0)
	if record:
		nwdays += record[0].total_lwp if len(record) else 0
	
	return nwdays

