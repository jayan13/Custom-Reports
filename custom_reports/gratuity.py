# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from math import floor

import frappe
from frappe import _, bold
from frappe.utils import flt, get_datetime, get_link_to_form, add_days, getdate, date_diff
from frappe.model.document import Document
from erpnext.payroll.doctype.gratuity.gratuity import Gratuity

@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule):
	current_work_experience = calculate_work_experience(employee, gratuity_rule) or 0
	gratuity_amount = calculate_gratuity_amount(employee, gratuity_rule, current_work_experience) or 0

	return {"current_work_experience": current_work_experience, "amount": gratuity_amount}


def calculate_work_experience(employee, gratuity_rule):

	total_working_days_per_year, minimum_year_for_gratuity = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, ["total_working_days_per_year", "minimum_year_for_gratuity"]
	)

	date_of_joining, relieving_date, openning_entry_date, opening_absent = frappe.db.get_value(
		"Employee", employee, ["date_of_joining", "relieving_date","openning_entry_date","opening_absent"]
	)
	if not relieving_date:
		frappe.throw(
			_("Please set Relieving Date for employee: {0}").format(
				bold(get_link_to_form("Employee", employee))
			)
		)

	method = frappe.db.get_value(
		"Gratuity Rule", gratuity_rule, "work_experience_calculation_function"
	)

	non_from=date_of_joining
	if openning_entry_date:
		non_from=add_days(getdate(openning_entry_date), 1)

	#employee_total_workings_days = calculate_employee_total_workings_days(
	#	employee, date_of_joining, relieving_date
	#)
	total_workings_days = (get_datetime(relieving_date) - get_datetime(date_of_joining)).days+1
	employee_non_workings_days = get_nonworking_days(
		employee,opening_absent,non_from, relieving_date
	)
	employee_total_workings_days=total_workings_days-employee_non_workings_days

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
        
	#frappe.msgprint(str(current_work_experience))
    
	if current_work_experience < minimum_year_for_gratuity:
		frappe.throw(
			_("Employee: {0} have to complete minimum {1} years for gratuity").format(
				bold(employee), minimum_year_for_gratuity
			)
		)
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


def calculate_gratuity_amount(employee, gratuity_rule, experience):
	company=frappe.db.get_value('Employee',employee,'company')
	if experience > 5 and gratuity_rule in ['Rule Under Unlimited Contract on resignation (UAE)','Rule Under Unlimited Contract on resignation (UAE)-GRAND']:
		if company=='GRAND CONTINENTAL FLAMINGO HOTEL':
			if frappe.db.exists("Gratuity Rule", "Rule Under Limited Contract (UAE)-GRAND", cache=True):
				gratuity_rule = 'Rule Under Limited Contract (UAE)-GRAND'
			else:
				gratuity_rule = 'Rule Under Limited Contract (UAE)'
		else:
			gratuity_rule = 'Rule Under Limited Contract (UAE)'

	applicable_earnings_component = get_applicable_components(gratuity_rule)
	total_applicable_components_amount = get_total_applicable_component_amount(
		employee, applicable_earnings_component, gratuity_rule
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
				slab.fraction_of_applicable_earnings,company
			)
			if slab_found:
				break

		elif calculate_gratuity_amount_based_on == "Sum of all previous slabs":
			if slab.to_year == 0 and slab.from_year == 0:
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				if company=='GRAND CONTINENTAL FLAMINGO HOTEL':
					gratuity_amount += (
						year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
					)
				else:									
					gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)

				
				slab_found = True
				break

			if experience > slab.to_year and experience > slab.from_year and slab.to_year != 0:
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				yer=slab.to_year - slab.from_year
				if company=='GRAND CONTINENTAL FLAMINGO HOTEL':
					gratuity_amount += (
					(slab.to_year - slab.from_year)
					* total_applicable_components_amount
					* slab.fraction_of_applicable_earnings
					)
				else:
					gratuity_amount += (yer*day)*((total_applicable_components_amount*12)/365)

				
				year_left -= slab.to_year - slab.from_year
				slab_found = True
				
			elif slab.from_year <= experience and (experience < slab.to_year or slab.to_year == 0):
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				if company=='GRAND CONTINENTAL FLAMINGO HOTEL':
					gratuity_amount += (
					year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
					)
				else:
					gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)

				
				slab_found = True

	if not slab_found:
		frappe.throw(
			_("No Suitable Slab found for Calculation of gratuity amount in Gratuity Rule: {0}").format(
				bold(gratuity_rule)
			)
		)
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


def get_total_applicable_component_amount(employee, applicable_earnings_component, gratuity_rule):
	sal_slip = get_last_salary_slip(employee)
	if not sal_slip:
		frappe.throw(_("No Salary Slip is found for Employee: {0}").format(bold(employee)))
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
	fraction_of_applicable_earnings,company=''
):
	slab_found = False
	gratuity_amount = 0
	if experience >= from_year and (to_year == 0 or experience < to_year):
		
		#gratuity_amount = (		
		#	total_applicable_components_amount * experience * fraction_of_applicable_earnings
		#)
		day=fraction_of_applicable_earnings*30
		day=round(day)		
		if company=='GRAND CONTINENTAL FLAMINGO HOTEL':
			gratuity_amount = (
			total_applicable_components_amount * experience * fraction_of_applicable_earnings
			)
		else:		
			gratuity_amount =(experience*day)*((total_applicable_components_amount*12)/365)

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
		"status": ['in',['On Leave','Half Day']],
		"employee": emp,
		"attendance_date": ("between", [get_datetime(start_date),get_datetime(end_date)]),
	}
	
	ppl_leave_types = frappe.get_list("Leave Type", filters={"is_ppl": 1})
	ppl_leave_types = [leave_type.name for leave_type in ppl_leave_types]
	filters["leave_type"] = ("IN", ppl_leave_types)
	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"],debug=0)
	if record:
		nwdays += float(record[0].total_lwp)*.5 if len(record) else 0

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