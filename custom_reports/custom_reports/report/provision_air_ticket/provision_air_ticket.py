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
		"fieldname": "ticket_provision_date",
		"fieldtype": "Data",
		"label": "Provision Date ",	
		"width": 80
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
		"fieldtype": "Currency",
		"label": "No Of Ticket Eligible ",	
		"width": 80
		},
		{
		"fieldname": "accrued",
		"fieldtype": "Currency",
		"label": "Accrued ",	
		"width": 80
		},
		{
		"fieldname": "used_tickets",
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
	conc=frappe.db.sql(""" select e.*,d.parent_department,d.department_name from `tabEmployee` e left join `tabDepartment` d on e.department=d.name where  %s  order by d.parent_department,d.name"""% (conditions),as_dict=1,debug=0)

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
		used=0
		ticket_price=0
		perodical=str(emp.no_of_tickets_eligible)+"'s in a "+emp.ticket_period+' Years'
		eligible=emp.no_of_tickets_eligible
		#ticket_provision_date
		if emp.openning_entry_date:
			openabs=0
			ticket_provision_date=emp.ticket_provision_date or emp.date_of_joining			
			total_days=frappe.utils.date_diff(emp.openning_entry_date,ticket_provision_date)+1
			
			if total_days > 0:
				absents+=float(emp.opening_absent)
				actual_worked+=total_days-absents
				balance+=float(emp.opening_ticket_balance)
				amount_balance+=float(emp.opening_ticket_balance_amount)
				accrued+=round(float(emp.opening_ticket_balance)+float(emp.used_tickets),3)
				amount_accrued+=round(emp.opening_ticket_amount_used+emp.opening_ticket_balance_amount,2)
				used+=float(emp.used_tickets)
				amount_used+=float(emp.opening_ticket_amount_used)
				ticket_price=emp.ticket_price
				#frappe.msgprint('t='+str(emp.used_tickets))
		tickets=get_tickect_setting(emp.name)
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
					absent=getabsents(emp.name,openabs,date_from,date_to)
					absents+=absent
					usedtickt=get_ticket_issued(emp.name,date_from,date_to)
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

		elif(getdate(processing_month)>emp.openning_entry_date):
			totaldays=0
			
			totaldays=frappe.utils.date_diff(processing_month,emp.openning_entry_date)+1					
			total_days+=totaldays
			date_from=emp.openning_entry_date
			date_to=getdate(processing_month)
			
			if totaldays:
				openabs=0
				absent=getabsents(emp.name,openabs,date_from,date_to)
				absents+=absent
				usedtickt=get_ticket_issued(emp.name,date_from,date_to)
				usedno=0					
				if usedtickt:
					usedno=usedtickt.ticket_no or 0
					
				actualworked=totaldays-absent
				actual_worked+=actualworked
				year=actualworked/365
				years+=year
				accru=0
				if float(emp.ticket_period) > 0 and emp.no_of_tickets_eligible:
					accru=(year/float(emp.ticket_period))*float(emp.no_of_tickets_eligible)

				bal=round(accru-float(usedno),3)
				accrued+=accru 
				balance+=bal
				used+=usedno
				ticket_price=emp.ticket_price
				amount_accrued+=accru*emp.ticket_price
				amount_used+=float(usedno)*emp.ticket_price
				amount_balance+=bal*emp.ticket_price

						
		accrued=round(accrued,3)
		balance=round(balance,3)
		amount_accrued=round(amount_accrued,2)
		amount_used=round(amount_used,2)
		amount_balance=round(amount_balance,2)

		years+=round((actual_worked/365),3)
		years=round(years,3)

		parent_department_tot+=amount_balance
		department_name_tot+=amount_balance
		parent_department_emp_tot+=1
		department_name_emp_tot+=1
		emp.update({'parent_department_tot':parent_department_tot})
		emp.update({'department_name_tot':department_name_tot})
		emp.update({'parent_department_emp_tot':parent_department_emp_tot})
		emp.update({'department_name_emp_tot':department_name_emp_tot})
		emp.update({'department_name':departmentname})		
		emp.update({'perodical':perodical})	
		emp.update({'ticket_price':ticket_price})	
		emp.update({'total_days':total_days})
		emp.update({'absent':absents})
		emp.update({'actual_worked':actual_worked})
		emp.update({'years':years})
		emp.update({'eligible':eligible})
		emp.update({'accrued':accrued})
		emp.update({'used_tickets':used})		
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

def get_tickect_setting(emp):
	sal=frappe.db.sql(""" select * from `tabEmployee Ticket Settings` where employee='%s' and docstatus='1'  order by from_date"""% (emp),as_dict=1,debug=0)
	if sal:
		return sal
	return
	
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

def get_ticket_issued(emp,from_date,to_date):
	sal7=frappe.db.sql(""" select sum(no_of_ticket_given) as ticket_no FROM `tabAdvance Air Ticket Request` where  employee='{0}' 
	and request_date between '{1}' and '{2}' and  docstatus=1 and ticket_type='Company' group by employee""".format(emp,from_date,to_date),as_dict=1,debug=0)
	if sal7:
		return sal7[0].ticket_no
	return 0
	

