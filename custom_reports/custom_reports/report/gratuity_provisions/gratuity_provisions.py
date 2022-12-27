# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe
#from erpnext.payroll.doctype.gratuity.gratuity import calculate_work_experience_and_amount
#employee gratuity_rule  return current_work_experience amount
from math import floor
from frappe import _, bold
from frappe.utils import flt, get_datetime, get_link_to_form
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
		"fieldname": "accr_d",
		"fieldtype": "Data",
		"label": "Accr'd ",	
		"width": 80
		},
		{
		"fieldname": "accrued",
		"fieldtype": "Data",
		"label": "Accrued ",	
		"width": 80
		},
		{
		"fieldname": "paid",
		"fieldtype": "Data",
		"label": "Paid ",	
		"width": 80
		},
		{
		"fieldname": "balance",
		"fieldtype": "Data",
		"label": "Balance",	
		"width": 100
		},
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	processing_month=filters.get("processing_month")
	gratuity_rule=filters.get("gratuity_rule")
	#nationality
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
		total_days=frappe.utils.date_diff(processing_month,emp.date_of_joining)
		gross_salary=get_gross_salary(emp.name,processing_month)
		absents=getabsents(emp.name,emp.opening_absent)		
		actual_worked=total_days-absents
		accrued=calculate_work_experience_and_amount(emp.name,gratuity_rule,processing_month)['amount']
		paid=0
		balance=accrued-paid
		parent_department_tot+=balance
		department_name_tot+=balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})			
		emp.update({'total_days':total_days})
		emp.update({'gross_salary':gross_salary})
		emp.update({'absent':absents})
		emp.update({'actual_worked':actual_worked})
		emp.update({'accr_d':'0'})
		emp.update({'accrued':accrued})		
		emp.update({'paid':paid})
		emp.update({'balance':balance})
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

def getabsents(emp,opn):
	absent=0
	sal=frappe.db.sql(""" select sum(l.total_leave_days)+{0} as absent from `tabLeave Application` l left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{1}' and p.is_lwp='1' and l.status='Approved' group by l.employee""".format(opn,emp),as_dict=1,debug=0)
	if sal:
		absent=sal[0].absent
	return absent

def getused(emp,opn):
	absent=0
	sal=frappe.db.sql(""" select sum(l.total_leave_days)+{0} as absent from `tabLeave Application` l left join `tabLeave Type` p on l.leave_type=p.name where l.employee='{1}' and p.is_lwp='0' and l.status='Approved' group by l.employee""".format(opn,emp),as_dict=1,debug=0)
	if sal:
		absent=sal[0].absent
	return absent

@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule,processing_month):
	current_work_experience = calculate_work_experience(employee, gratuity_rule,processing_month) or 0
	gratuity_amount = calculate_gratuity_amount(employee, gratuity_rule, current_work_experience,processing_month) or 0

	return {"current_work_experience": current_work_experience, "amount": gratuity_amount}


def calculate_work_experience(employee, gratuity_rule,processing_month):

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
	employee_total_workings_days = calculate_employee_total_workings_days(
		employee, date_of_joining, relieving_date
	)

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
		current_work_experience = floor(current_work_experience)

	#if current_work_experience < minimum_year_for_gratuity:
	#	frappe.throw(
	#		_("Employee: {0} have to complete minimum {1} years for gratuity").format(
	#			bold(employee), minimum_year_for_gratuity
	#		)
	#	)
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
	applicable_earnings_component = get_applicable_components(gratuity_rule)
	total_applicable_components_amount = get_total_applicable_component_amount(
		employee, applicable_earnings_component, gratuity_rule,processing_month
	)

	calculate_gratuity_amount_based_on = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, "calculate_gratuity_amount_based_on"
	)
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
				gratuity_amount += (
					year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
				)
				slab_found = True
				break

			if experience > slab.to_year and experience > slab.from_year and slab.to_year != 0:
				gratuity_amount += (
					(slab.to_year - slab.from_year)
					* total_applicable_components_amount
					* slab.fraction_of_applicable_earnings
				)
				year_left -= slab.to_year - slab.from_year
				slab_found = True
			elif slab.from_year <= experience and (experience < slab.to_year or slab.to_year == 0):
				gratuity_amount += (
					year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
				)
				slab_found = True

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
	gratuity_amount = 0
	if experience >= from_year and (to_year == 0 or experience < to_year):
		gratuity_amount = (
			total_applicable_components_amount * experience * fraction_of_applicable_earnings
		)
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