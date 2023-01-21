# -*- coding: utf-8 -*-
# Copyright (c) 2017, Direction and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _, bold
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,get_datetime,get_link_to_form,get_first_day,get_last_day
from frappe import throw, msgprint, _
from erpnext.payroll.doctype.gratuity.gratuity import Gratuity

@frappe.whitelist()
def validate_expense(exp_year,exp_date,employee):

	emprv=frappe.db.sql(""" select * from `tabExpense Request Item` where docstatus=1 and employee='{0}' and date between DATE_SUB('{2}', INTERVAL {1} YEAR) and '{2}' """.format(employee,exp_year,exp_date),as_dict=1,debug=0)

	if emprv:
		return 1
	else:
		return 0
	
@frappe.whitelist()
def maintanse_items(sub_gp):
	return frappe.db.sql(""" select sub_group_items from `tabAsset Sub Group Items` where parent='{0}' """.format(sub_gp),as_dict=1,debug=0)

@frappe.whitelist()
def customer_outstanding(company,customer):
	outsta=0

	out=frappe.db.get_list('Sales Invoice',
    fields=['sum(outstanding_amount) as outstanding_amount'],
	filters={'docstatus':1,'company':company,'customer':customer,'outstanding_amount':['>',0]},
    group_by='customer')
	if out:
		outsta=out[0].outstanding_amount
	return outsta


@frappe.whitelist()
def customer_overdue(company,customer):
	overdue=0
	
	payment_terms = frappe.db.get_value('Customer', {'name':customer}, ['payment_terms'])
	if payment_terms:
		import re		
		
		payment_terms=re.findall('\d+', payment_terms)
		
		values = {'company': company,'customer':customer,'payment_terms':payment_terms}
		over = frappe.db.sql("""
			SELECT DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL %(payment_terms)s DAY)) as overdu from `tabSales Invoice` where docstatus = 1 and company=%(company)s and customer=%(customer)s and outstanding_amount <> 0 and DATEDIFF(CURDATE(),DATE_ADD(posting_date, INTERVAL %(payment_terms)s DAY)) >0 order by posting_date limit 0,1
		""", values=values, as_dict=1,debug=0)
		if over:
			overdue=over[0].overdu
	return overdue

@frappe.whitelist()
def customer_credit(company,customer):
	overdue=0   	
	overdue=frappe.db.get_value('Customer Credit Limit', {'company':company,'parent':customer}, ['credit_limit'])
	return overdue or 0

@frappe.whitelist()
def update_cost_acc(doc,event):
	
	item=['TELWA-330ML - 12 PACK','TELWA-330ML - 16 PACK','TELWA-600ML - 12 PACK','TELWA-600ML - 20 PACK','TELWA-600ML - 20 PCS - CTN','TELWA-1.5 L - 6 PACK','TELWA-1.5 L - 6 PCS - CTN','TELWA-NEW GALLON','TELWA-RE-FILLING GALLON']
	acc=['513101 - COGS .330 Ltrs - TELWA','513101 - COGS .330 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513102 - COGS .600 Ltrs - TELWA','513103 - COGS 1.5 Ltrs - TELWA','513103 - COGS 1.5 Ltrs - TELWA','513201 - COGS 20 Ltrs Bottle - TELWA','513202 - COGS 20 Ltrs Refill - TELWA']
	if doc.company=='Nigerienne De Reffraichissement Telwa – Socite a Resposabilite Limitee.':
		for itm in doc.items:
			if itm.item_code in item and itm.expense_account=='':
				index = item.index(itm.item_code)
				itm.expense_account=acc[index]

@frappe.whitelist()
def get_last_workingday(employee,leave_application):
	from_date=frappe.db.get_value('Leave Application', leave_application, ['from_date'])
	last_working=frappe.utils.getdate(from_date)
	df=frappe.utils.add_days(last_working,-1)
	if leave_application:		
		holiday_list,default_shift=frappe.db.get_value('Employee', employee, ['holiday_list','default_shift'])
		if default_shift:
			holiday_list=frappe.db.get_value('Shift Type', default_shift, ['holiday_list']) or holiday_list
		if holiday_list:
			holiday_date=frappe.db.get_all('Holiday',filters={'parent': holiday_list,'holiday_date':['<',last_working]},fields=['holiday_date'],pluck='holiday_date')
			if holiday_date:
				df=check_last_day(df,holiday_date)
	return df
def check_last_day(day,Holiday):
	if day in Holiday:
		last_working=frappe.utils.getdate(day)
		day=frappe.utils.add_days(last_working,-1)
		check_last_day(day,Holiday)
	return day

@frappe.whitelist()
def send_notification(name,handover_staff,employee_name): 
	receiver,full_name=frappe.db.get_value('User', handover_staff, ['email','full_name'])
	url=frappe.utils.get_url()
	Email_Subject="""Pending Handover Approval {0}:{1}""".format(name,employee_name)
	pgurl='<a href="'+url+'/app/clearance-form/'+name+'" >'+name+'</a>'
	#receiver='jayakumar@alantechnologies.net'
	msg=""" Dear {0}<br> 
                    Employee Clearance Form (Leave/End of Service) handover is pending for your verification & approval for the employee {1}.<br> 
                    Please click here {2} to verify and approve<br> 
                    """.format(full_name,employee_name,pgurl)
	if receiver:
		email_args = {
                    "recipients": [receiver],
                    "message": msg,
                    "subject": Email_Subject,
                    "reference_doctype": 'Clearance Form',
                    "reference_name": name
                    }
		frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
	return 'Notification Email Send to '+handover_staff

@frappe.whitelist()
def get_ticket_issued(emp,from_date,to_date):
	sal7=frappe.db.sql(""" select sum(no_of_ticket_given) as ticket_no FROM `tabAdvance Air Ticket Request` where  employee='{0}' 
	and request_date between '{1}' and '{2}' and  docstatus=1 and ticket_type='Company' group by employee""".format(emp,from_date,to_date),as_dict=1,debug=0)
	if sal7:
		return sal7[0].ticket_no
	return 0

@frappe.whitelist()
def get_ticket_given(emp,from_date,to_date):
	empy=frappe.db.get_value('Employee',{'name':emp},['openning_entry_date','date_of_joining','ticket_period','ticket_price','opening_ticket_balance','opening_ticket_balance_amount','used_tickets','opening_ticket_amount_used','no_of_tickets_eligible','ticket_provision_date','opening_absent'],as_dict=1,debug=0)
	ticket_per_month=0
	amount_balance=0
	usedno=0
	usedpri=0
	amount_used=0
	amount_accrued=0
	balance=0
	accrued=0
	
	years=0
	actual_worked=0
	total_days=0
	absents=0
	used=0
	ticket_price=0
	processing_month=to_date
	if empy.openning_entry_date:
		ticket_provision_date=empy.ticket_provision_date or empy.date_of_joining			
		total_days=frappe.utils.date_diff(empy.openning_entry_date,ticket_provision_date)+1
		if total_days > 0:
			absents+=float(empy.opening_absent)
			actual_worked+=total_days-absents
			balance+=float(empy.opening_ticket_balance)
			amount_balance+=float(empy.opening_ticket_balance_amount)
			accrued+=round(float(empy.opening_ticket_balance)+float(empy.used_tickets),3)
			amount_accrued+=round(empy.opening_ticket_amount_used+empy.opening_ticket_balance_amount,2)
			used+=float(empy.used_tickets)
			amount_used+=float(empy.opening_ticket_amount_used)
			ticket_price=empy.ticket_price
			#frappe.msgprint(str(accrued))
	tickets=get_tickect_setting(emp)
	if tickets:
		for ticket in tickets:
			totaldays=0				
			if ticket.from_date!=None and ticket.to_date!=None and getdate(processing_month) >= ticket.to_date:
				totaldays=frappe.utils.date_diff(ticket.to_date,ticket.from_date)+1					
				total_days+=totaldays
				date_from=ticket.from_date
				date_to=ticket.to_date
			elif ticket.from_date!=None and ticket.to_date==None and getdate(processing_month) >= ticket.from_date:
				totaldays=frappe.utils.date_diff(processing_month,ticket.from_date)+1					
				total_days+=totaldays
				date_from=ticket.from_date
				date_to=processing_month
			if totaldays:
				openabs=0
				absent=getabsents(emp,openabs,date_from,date_to)
				absents+=absent
				usedtickt=get_ticket_issued(emp,date_from,date_to)
				usedno=0					
				if usedtickt:
					usedno=usedtickt.ticket_no or 0
					
				actualworked=totaldays-absent
				actual_worked+=actualworked
				year=actualworked/365
				years+=year
				accru=0
				if float(ticket.periodical) > 0 and ticket.no_of_ticket_eligible:
					accru=(year/float(ticket.periodical))*float(ticket.no_of_ticket_eligible)

				bal=round(accru-float(usedno),3)
				accrued+=accru 
				balance+=bal
				used+=usedno
				ticket_price=ticket.ticket_fare
				amount_accrued+=accru*ticket.ticket_fare
				amount_used+=float(usedno)*ticket.ticket_fare
				amount_balance+=bal*ticket.ticket_fare
	elif(empy.openning_entry_date!=None and getdate(processing_month)>empy.openning_entry_date):
		totaldays=0
			
		totaldays=frappe.utils.date_diff(processing_month,empy.openning_entry_date)+1					
		total_days+=totaldays
		date_from=empy.openning_entry_date
		date_to=getdate(processing_month)
			
		if totaldays:
			openabs=0
			absent=getabsents(emp,openabs,date_from,date_to)
			absents+=absent
			usedtickt=get_ticket_issued(emp,date_from,date_to)
			usedno=0					
			if usedtickt:
				usedno=usedtickt.ticket_no or 0
					
			actualworked=totaldays-absent
			actual_worked+=actualworked
			year=actualworked/365
			years+=year
			accru=0
			if float(empy.ticket_period) > 0 and empy.no_of_tickets_eligible:
				accru=(year/float(empy.ticket_period))*float(empy.no_of_tickets_eligible)

			bal=round(accru-float(usedno),3)
			accrued+=accru 
			balance+=bal
			used+=usedno
			ticket_price=empy.ticket_price
			amount_accrued+=accru*empy.ticket_price
			amount_used+=float(usedno)*empy.ticket_price
			amount_balance+=bal*empy.ticket_price
	return {'balance':balance,'used':used,'amount_balance':amount_balance,'amount_used':amount_used}
def get_tickect_setting(emp):
	sal=frappe.db.sql(""" select * from `tabEmployee Ticket Settings` where employee='%s' and docstatus='1'  order by from_date"""% (emp),as_dict=1,debug=0)
	if sal:
		return sal
	return

def get_gross_salary(emp,processing_month):
	salary_structure=frappe.db.get_value("Salary Structure Assignment",{'employee':emp,'from_date':['<=',processing_month]},'salary_structure',debug=0)
	gsal=0
	sal=frappe.db.sql(""" select sum(amount) as gross_salary from `tabSalary Detail` where parent='%s' and parentfield='earnings'  group by parent"""% (salary_structure),as_dict=1,debug=0)
	if sal:
		gsal=sal[0].gross_salary
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

@frappe.whitelist()
def get_year_month_day(emp,date_from,date_to):
	empy=frappe.db.get_value('Employee',{'name':emp},['opening_absent'],debug=0)
	absent=getabsents(emp,empy,date_from,date_to)
	totaldays=frappe.utils.date_diff(date_to,date_from)+1
	
	from dateutil import relativedelta

	date1 = getdate(date_from)
	date2 = getdate(date_to)

	diff = relativedelta.relativedelta(date2, date1)

	years = diff.years
	months = diff.months
	days = diff.days

	return '{} years {} months {} days (Abs {} Days ) (Total {} Days)'.format(years, months, days,absent,totaldays)

@frappe.whitelist()
def get_annual_leaveamount(emp,reval_date):
	employee=frappe.db.get_value('Employee',{'name':emp},['company','ticket_period','opening_used_leaves','date_of_joining','no_of_tickets_eligible'],as_dict=1,debug=0)
	rule=get_provision_rule(employee.company,reval_date,0)
	provrule=''
	ticket_period=employee.ticket_period
	ticket_eligible=employee.no_of_tickets_eligible
	if rule:
		provrule=rule.name
	applicable_earnings_component=get_applicable_components_annual(provrule)
	sal=get_total_applicable_component_amount(emp, applicable_earnings_component, reval_date)

	gross_salary=get_gross_salary(emp,reval_date)
	tick=frappe.db.sql(""" select periodical,no_of_ticket_eligible from `tabEmployee Ticket Settings` where employee='%s' and docstatus='1'  order by from_date desc"""% (emp),as_dict=1,debug=0)
	if tick:
		ticket_period=tick[0].periodical
		ticket_eligible=employee.no_of_ticket_eligible
	
	used_leaves=getused(emp,employee.opening_used_leaves,reval_date,employee.date_of_joining)
	salary_structure=get_salary_structure(emp)
	salcomp=frappe.db.get_all('Salary Detail',filters={'parent':salary_structure,'depends_on_payment_days':'1','amount':['>','0'],'salary_component':['in',('Basic(A)','Basic')]},fields=['salary_component','amount','parentfield'])
	base_salary=0
	if salcomp:
		base_salary=salcomp[0].amount

	leave_entitled=get_leave_no(emp,reval_date)

	return {'sal':sal,'gross_salary':gross_salary,'ticket_period':ticket_period,'used_leaves':used_leaves,'base_salary':base_salary,'leave_entitled':leave_entitled,'salary_structure':salary_structure,'ticket_eligible':ticket_eligible}

def get_leave_no(emp,processing_month):
	
	set = frappe.db.sql(""" select new_leaves_allocated,unused_leaves from `tabLeave Allocation` where employee='{0}' 
	and '{1}' between from_date and to_date and leave_type='Annual Leave' """.format(emp,processing_month),as_dict=1,debug=0)
	if not set:
		return
	return set[0].new_leaves_allocated

def getused(emp,opn,start_date,end_date):
	used=float(opn)

	sal=frappe.db.sql(""" select count(*) as used FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and a.attendance_date between '{1}' and  '{2}' and a.leave_type='Annual Leave' """.format(emp,start_date,end_date),as_dict=1,debug=0)
	
	if sal:
		used+=sal[0].used
		
	return used

@frappe.whitelist()
def get_compen_amount(emp,reval_date):
	provrule=''	
	applicable_earnings_component=get_applicable_components_annual(provrule)
	sal=get_total_applicable_component_amount(emp, applicable_earnings_component, reval_date)
	return sal

def get_applicable_components_annual(rule=''):
	if rule:
		applicable_earnings_components = frappe.get_all(
		"Provision Applicable Component", filters={"parent": rule}, fields=["salary_component"],debug=0)
	if rule=='' or applicable_earnings_components=='':
		applicable_earnings_components = frappe.get_all(
		"Salary Component", filters={"type": 'Earning',}, fields=["name as salary_component"],debug=0)

	applicable_earnings_component = []
	if len(applicable_earnings_components):		
		applicable_earnings_component = [
		component.salary_component for component in applicable_earnings_components
		]

	return applicable_earnings_component

@frappe.whitelist()
def get_employee_salary(emp,date_from,date_to):
	salary_structure=get_salary_structure(emp)
	salcomp=frappe.db.get_all('Salary Detail',filters={'parent':salary_structure,'depends_on_payment_days':'1','amount':['>','0']},fields=['salary_component','amount','parentfield'])
	monthstart=get_first_day(date_to)	
	monthend=get_last_day(date_to)
	days_in_month=date_diff(getdate(monthend),getdate(monthstart))+1

	total_days=date_diff(date_to,monthstart)+1
	nonworking_days=get_nonworking_days(emp,0,monthstart,date_to)
	workingday=total_days-nonworking_days

	worked=get_worked_days(emp,monthstart,date_to)

	if salcomp:
		for comp in salcomp:
			if comp.parentfield=='earnings':
				comp.amount=round((float(comp.amount)/float(days_in_month))*float(workingday),2)
			if comp.parentfield=='deductions':
				comp.amount=round((float(comp.amount)/float(days_in_month))*float(workingday),2)*-1
	return salcomp

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

accured_days=0
@frappe.whitelist()
def calculate_work_experience_and_amount(employee, gratuity_rule,processing_month):
	openabs=frappe.db.get_value('Employee',{'name':employee},['opening_absent'],debug=0)
	global accured_days
	accured_days=0
	current_work_experience = calculate_work_experience(employee, gratuity_rule,processing_month,openabs) or 0
	
	gratuity_amount = calculate_gratuity_amount(employee, gratuity_rule, current_work_experience,processing_month) or 0
	#frappe.msgprint('days='+str(accured_days))
	return {"current_work_experience": current_work_experience, "amount": gratuity_amount,"accured_days":accured_days}


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

	#if current_work_experience < minimum_year_for_gratuity:
	#	current_work_experience=0
		
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
		employee, applicable_earnings_component, processing_month
	)
	
	if experience > 5 and gratuity_rule=='Rule Under Unlimited Contract on resignation (UAE)':
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
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				if gratuity_rule=='Rule Under Limited Contract (UAE)-GRAND':
					gratuity_amount += (
						year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
					)
				else:									
					gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)

				accured_days+=(year_left*day)
				slab_found = True
				break

			if experience > slab.to_year and experience > slab.from_year and slab.to_year != 0:
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				yer=slab.to_year - slab.from_year
				if gratuity_rule=='Rule Under Limited Contract (UAE)-GRAND':
					gratuity_amount += (
					(slab.to_year - slab.from_year)
					* total_applicable_components_amount
					* slab.fraction_of_applicable_earnings
					)
				else:
					gratuity_amount += (yer*day)*((total_applicable_components_amount*12)/365)

				accured_days+=(yer*day)
				year_left -= slab.to_year - slab.from_year
				slab_found = True
				#frappe.msgprint(str(experience)+'-('+str(slab.from_year)+'-'+str(slab.to_year)+')-'+str(slab.fraction_of_applicable_earnings)+'*'+str(slab.to_year - slab.from_year)+'*'+str(total_applicable_components_amount))
			elif slab.from_year <= experience and (experience < slab.to_year or slab.to_year == 0):
				day=slab.fraction_of_applicable_earnings*30
				day=round(day)
				if gratuity_rule=='Rule Under Limited Contract (UAE)-GRAND':
					gratuity_amount += (
					year_left * total_applicable_components_amount * slab.fraction_of_applicable_earnings
					)
				else:
					gratuity_amount += (year_left*day)*((total_applicable_components_amount*12)/365)

				accured_days+=(year_left*day)
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


def get_total_applicable_component_amount(employee, applicable_earnings_component, processing_month):
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
	stru=frappe.get_list(
		"Salary Structure Assignment",
		filters={"employee": employee, "docstatus": 1},
		fields=["from_date", "salary_structure"],
		order_by="from_date desc",
	)
	if stru:
		return stru[0].salary_structure
	return
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

def get_worked_days(emp,start_date,end_date):
	nwdays=0
	filters = {
		"docstatus": 1,
		"status": 'On Leave',
		"employee": emp,
		"attendance_date": ("between", [get_datetime(start_date),get_datetime(end_date)]),
	}
	
	lwp_leave_types = frappe.get_list("Leave Type", filters={"is_lwp": 0})
	lwp_leave_types = [leave_type.name for leave_type in lwp_leave_types]
	filters["leave_type"] = ("IN", lwp_leave_types)
	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"],debug=0)
	if record:
		nwdays += record[0].total_lwp if len(record) else 0

	filters = {
		"docstatus": 1,
		"status": 'Present',
		"employee": emp,
		"attendance_date": ("between", [get_datetime(start_date),get_datetime(end_date)]),
	}
	record = frappe.get_all("Attendance", filters=filters, fields=["COUNT(name) as total_lwp"],debug=0)
	if record:
		nwdays += record[0].total_lwp if len(record) else 0
	
	return nwdays