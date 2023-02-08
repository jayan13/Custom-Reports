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
		"fieldname": "basic_salary",
		"fieldtype": "Data",
		"label": "Basic Salary ",	
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
		"fieldname": "opening_balance_amount",
		"fieldtype": "Data",
		"label": "Opening Bal Amt ",	
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
		"fieldname": "used",
		"fieldtype": "Currency",
		"label": "Used ",	
		"width": 80
		},
		{
		"fieldname": "balance",
		"fieldtype": "Currency",
		"label": "Balance ",	
		"width": 80
		},
		{
		"fieldname": "amount_accrued",
		"fieldtype": "Currency",
		"label": "Amount Accrued",	
		"width": 100
		},
		{
		"fieldname": "amount_used",
		"fieldtype": "Currency",
		"label": "Amount Used",	
		"width": 100
		},
		{
		"fieldname": "amount_balance",
		"fieldtype": "Currency",
		"label": "Amount Balance",	
		"width": 100
		},
 	 ]	
	    
		
	return columns

def get_data(conditions,filters):
	
	processing_month=filters.get("processing_month")
	company=filters.get("company")
	conc=frappe.db.sql(""" select e.*,d.parent_department,d.department_name from `tabEmployee` e left join `tabDepartment` d on e.department=d.name where e.status='Active' and   %s  order by d.parent_department,d.name"""% (conditions),as_dict=1,debug=0)
	
	data=[]
	parent_department=''
	department_name=''
	parent_department_tot=0
	department_name_tot=0
	parent_department_emp_tot=0
	department_name_emp_tot=0
	#Provision Annual Leave Setting
	alrules=get_provision_rule(company)
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
		#leave_provision_date
		start_date=emp.date_of_joining
		openabs=0
		opnused=0
		leave_code='0d'
		gross_salary=0
		usedleave=0
		accrued=0
		balance=0
		absents=0
		basic_salary=0
		amount_balance=0
		opening_balance_amount=0
		total_days=0
		actual_worked=0
		amount_accrued=0
		amount_used=0

		date_from=filters.get("date_from")
		if date_from:
			start_date=getdate(date_from)
			allo=get_leave_no(emp.name,processing_month)
			totleave=emp.leaves_per_year
			if allo:
				totleave=allo.new_leaves_allocated
			openabs=0
			opnused=0
			totaldays=date_diff(processing_month,start_date)+1						
			total_days+=totaldays			
			gross_salary=get_gross_salary(emp.name,company,processing_month)
			absent=getabsents(emp.name,openabs,start_date,processing_month)
			absents+=absent
			usedleaves=getused(emp.name,opnused,start_date,processing_month)
			usedleave+=usedleaves
			leave_code=str(totleave)+'D'
			actualworked=totaldays-absent
			actual_worked+=actualworked
			#accru=round((actualworked/365)*float(totleave),4)
			accru=round(round(float(totleave)/365,4)*actualworked,4)										
			accrued+=accru
			bala=round(accru-usedleaves,4)
			balance+=bala
			amountaccrued=round(((gross_salary*12)/365)*accru,2)
			amount_accrued+=amountaccrued
			amountused=round(((gross_salary*12)/365)*usedleaves,2)
			amount_used+=amountused
			amount_balance+=round(amountaccrued-amountused,2)
		else:

			if alrules:
				for rul in alrules:
					if emp.openning_entry_date:
						if (rul.date_from==None or (rul.date_from!=None and getdate(rul.date_from) <= emp.openning_entry_date)) and rul.date_to!=None and getdate(rul.date_to)>=emp.openning_entry_date:
							leave_provision_date=emp.leave_provision_date or emp.date_of_joining
							totaldays=date_diff(emp.openning_entry_date,leave_provision_date)+1
							total_days+=totaldays
							applicable_earnings_component=get_applicable_components(rul.name)
							sal=get_total_applicable_component_amount(emp.name, applicable_earnings_component, processing_month)
							actualworked=totaldays-float(emp.opening_absent)
							absents+=float(emp.opening_absent)
							actual_worked+=actualworked
							if emp.opening_leaves_accrued > 0:
								accru=emp.opening_leaves_accrued
							else:
								#accru=round((actualworked/365)*emp.leaves_per_year,4)
								accru=round(round(emp.leaves_per_year/365,4)*actualworked,4)

							accrued+=accru
							leave_code=str(emp.leaves_per_year)+'D'
							usedleaves=float(emp.opening_used_leaves.replace(',',''))
							usedleave+=usedleaves
							bala=round(accru-float(emp.opening_used_leaves.replace(',','')),4)
							balance+=bala
							if getdate(processing_month)<=getdate('2022-12-31'):
								basic_salary=sal
							opening_balance_amount=emp.opening_balance_amount
							#amountbalance=round(((sal*12)/365)*bala,2)
							#amount_balance+=amountbalance
							if company=='GRAND CONTINENTAL FLAMINGO HOTEL' and getdate(processing_month)<=getdate('2022-12-31'):
								ondaydalary=round(sal/30,4)
							else:
								ondaydalary=(sal*12)/365
							
							
							amountused=round(ondaydalary*usedleaves,2)
							amount_used+=amountused

							#if emp.opening_balance_amount > 0:
							#	amountaccrued=emp.opening_balance_amount+amountused
							#else:
							#	amountaccrued=round(ondaydalary*accru,2)

							amountaccrued=round(ondaydalary*accru,2)
							amount_accrued+=amountaccrued
							#frappe.msgprint(str(amountaccrued))

							if emp.opening_balance_amount > 0 and getdate(processing_month)<=getdate('2022-12-31'):
								amount_balance+=emp.opening_balance_amount
							else:
								amount_balance+=round(amountaccrued-amountused,2)

						elif getdate(processing_month) > emp.openning_entry_date and getdate(rul.date_from) <= getdate(processing_month):
							
							totleave=emp.leaves_per_year
							tot_leave=get_leave_no(emp.name,processing_month)
							if tot_leave:
								totleave=tot_leave.new_leaves_allocated
							day = getdate(emp.openning_entry_date)
							start_date = add_days(day, 1)
							openabs=0
							opnused=0
							totaldays=date_diff(processing_month,emp.openning_entry_date)						
							total_days+=totaldays
							applicable_earnings_component=get_applicable_components(rul.name)
							gross_salary=get_total_applicable_component_amount(emp.name, applicable_earnings_component, processing_month)
							absent=getabsents(emp.name,openabs,start_date,processing_month)
							absents+=absent
							usedleaves=getused(emp.name,opnused,start_date,processing_month)
							usedleave+=usedleaves
							leave_code=str(totleave)+'D'
							actualworked=totaldays-absent
							actual_worked+=actualworked
							#accru=round((actualworked/365)*float(totleave),4)
							accru=round(round(float(totleave)/365,4)*actualworked,4)										
							accrued+=accru
							bala=round(accru-usedleaves,4)
							balance+=bala
							amountaccrued=round(((gross_salary*12)/365)*accru,2)
							amount_accrued+=amountaccrued
							amountused=round(((gross_salary*12)/365)*usedleaves,2)
							amount_used+=amountused
							amount_balance+=round(amountaccrued-amountused,2)
							#frappe.msgprint(str(amountaccrued))
							#amountbalance=round(((gross_salary*12)/365)*balance,2)
							#amount_balance+=amountbalance
					else:
						leave_provision_date=emp.leave_provision_date or emp.date_of_joining
						applicable_earnings_component=get_applicable_components(rul.name)
						sal=0
						if rul.date_from==None and rul.date_to!=None and getdate(leave_provision_date)<=getdate(rul.date_to):
							start_date=leave_provision_date
							if getdate(rul.date_to) < getdate(processing_month):
								end_date=rul.date_to
							else:
								end_date=processing_month
							basic_salary=get_total_applicable_component_amount(emp.name, applicable_earnings_component, processing_month)
							sal=basic_salary
							if getdate(processing_month)>getdate('2022-12-31'):
								basic_salary=0
						if rul.date_from!=None and rul.date_to==None:
							if getdate(rul.date_from) > getdate(leave_provision_date):
								start_date=rul.date_from
							else:
								start_date=leave_provision_date

							end_date=processing_month
							gross_salary=get_total_applicable_component_amount(emp.name, applicable_earnings_component, processing_month)
							sal=gross_salary
						#-----------------------------------------

						totaldays=date_diff(end_date,start_date)+1
						total_days+=totaldays
						totleave=get_leave_no(emp.name,processing_month)
						leaves_per_year=emp.leaves_per_year
						if totleave:
							leaves_per_year=totleave.new_leaves_allocated	
						
						absent=getabsents(emp.name,openabs,start_date,end_date)
						absents+=absent
						usedleaves=getused(emp.name,opnused,start_date,end_date)
						usedleave+=usedleaves
						leave_code=str(leaves_per_year)+'D'
						actualworked=totaldays-absent
						actual_worked+=actualworked
						accru=round(round(float(leaves_per_year)/365,4)*actualworked,4)										
						accrued+=accru
						bala=round(accru-usedleaves,4)
						balance+=bala
						amountaccrued=round(((sal*12)/365)*accru,2)
						amount_accrued+=amountaccrued
						amountused=round(((sal*12)/365)*usedleaves,2)
						amount_used+=amountused
						amount_balance+=round(amountaccrued-amountused,2)	

			else:
				totleave=get_leave_no(emp.name,processing_month)
				leaves_per_year=emp.leaves_per_year
				if totleave:
					leaves_per_year=totleave.new_leaves_allocated

				day = getdate(emp.openning_entry_date)
				start_date = add_days(day, 1)
				openabs=emp.opening_absent
				opnused=emp.opening_used_leaves.replace(',','')
				leave_provision_date=emp.leave_provision_date or emp.date_of_joining
				total_days=date_diff(processing_month,leave_provision_date)+1
				applicable_earnings_component=[]
				gross_salary=get_total_applicable_component_amount(emp.name, applicable_earnings_component, processing_month)
				absents=getabsents(emp.name,openabs,start_date,processing_month)
				usedleave=getused(emp.name,opnused,start_date,processing_month)
				leave_code=str(leaves_per_year)+'D'
				actual_worked=total_days-absents
				#accrued=round((actual_worked/365)*leaves_per_year,4)
				accrued=round(round(leaves_per_year/365,4)*actual_worked,4)			
				balance=round(accrued-usedleave,4)
				amount_accrued=round(((gross_salary*12)/365)*accrued,2)
				#frappe.msgprint(str(amount_accrued))
				amount_used=round(((gross_salary*12)/365)*usedleave,2)
				amount_balance=round(amount_accrued-amount_used,2)
			
			
		accrued=round(accrued,3)
		balance=round(balance,3)
		amount_accrued=round(amount_accrued,2)
		amount_used=round(amount_used,2)
		amount_balance=round(amount_balance,2)
		

		parent_department_tot+=amount_balance
		department_name_tot+=amount_balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		

		emp.update({'opening_balance_amount':opening_balance_amount})
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})
		emp.update({'department_name':departmentname})
		emp.update({'total_days':total_days})
		emp.update({'basic_salary':basic_salary})
		emp.update({'gross_salary':gross_salary})
		emp.update({'absent':absents})
		emp.update({'leave_code':leave_code})
		emp.update({'actual_worked':actual_worked})
		emp.update({'accrued':accrued})
		emp.update({'used':usedleave})
		emp.update({'amount_accrued':amount_accrued})
		emp.update({'amount_used':amount_used})
		emp.update({'balance':balance})
		emp.update({'amount_balance':amount_balance})
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
		conditions += " and DATE(e.date_of_joining) <= '{0}' ".format(processing_month)
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