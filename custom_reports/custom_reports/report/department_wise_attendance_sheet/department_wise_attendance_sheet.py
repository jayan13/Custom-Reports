# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,get_datetime,get_link_to_form,get_first_day,get_last_day

import erpnext
from erpnext.hr.doctype.employee.employee import (get_holiday_list_for_employee,)

def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(filters), get_data(conditions,filters)

def get_columns(filters):
	company=filters.get("company")
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
		"fieldname": "department",
		"fieldtype": "Data",
		"label": "Department",	
		"width": 150
		},
		{
		"fieldname": "presnt",
		"fieldtype": "Float",
		"label": "Presnt",	
		"width": 100
		},
		{
		"fieldname": "weekly_off",
		"fieldtype": "Float",
		"label": "Off Day",	
		"width": 100
		},
		{
		"fieldname": "holiday",
		"fieldtype": "Float",
		"label": "Holiday",	
		"width": 100
		},
		{
		"fieldname": "compensatory_off",
		"fieldtype": "Float",
		"label": "Compensatory Off",	
		"width": 100
		},
		{
		"fieldname": "annual_leave",
		"fieldtype": "Float",
		"label": "Annual Leave",	
		"width": 100
		},
		{
		"fieldname": "sick_leave",
		"fieldtype": "Float",
		"label": "Sick Leave",	
		"width": 100
		},
		{
		"fieldname": "maternity_leave",
		"fieldtype": "Float",
		"label": "Maternity Leave",	
		"width": 100
		},
		{
		"fieldname": "other",
		"fieldtype": "Float",
		"label": "Spcial Leave",	
		"width": 100
		},		
		{
		"fieldname": "leave_without_pay",
		"fieldtype": "Float",
		"label": "Unpaid Leaves",	
		"width": 100
		},		
		{
		"fieldname": "over_time",
		"fieldtype": "Float",
		"label": "Over Time @1.25",	
		"width": 100
		},
		{
		"fieldname": "holiday_over_time",
		"fieldtype": "Float",
		"label": "Over Time @1.50",	
		"width": 100
		},						
 	 ]
	

	
	return columns

def get_data(conditions,filters):
	data=[]
	
	date_to=filters.get("date_to")
	company=filters.get("company")
		
	#mnth=frappe.utils.formatdate(date_to, "MMMM yyyy")	
	#filters.update({'month':mnth})
	
	conc=frappe.db.sql(""" select name,IF(parent_department='All Departments',name,parent_department) as parent_department from `tabDepartment` where %s  order by parent_department,name"""% (conditions),as_dict=1,debug=0)
	
	emp_count=0
	emp_count_dept=0
	emp_count_pare_dept=0
	parent_department_name=''
	department_name=''
	parent_department_tot=0
	
	department_tot=0
	
	for dept in conc:		
		department=dept.name.split('-')[0]
		parent_department=dept.parent_department.split('-')[0]
		if parent_department != parent_department_name:
			parent_department_name=parent_department
			parent_department_tot=0		
			emp_count_pare_dept=0
			

		if department != department_name:
			department_name=department
			department_tot=0
			emp_count_dept=0
			
		empqry=''
		if filters.get("employee"):
			emps=filters.get("employee")
			empq="','".join([str(elem) for elem in emps])
			empqry = "  and s.employee in ('{0}') ".format(empq)
		
		if filters.get("payroll_entry"):
			payroll_entry=filters.get("payroll_entry")
			empqry+=" and s.payroll_entry='{0}' ".format(payroll_entry)

		slip=frappe.db.sql(""" select s.*,e.department as emp_department from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{2}') and YEAR(s.end_date)=YEAR('{2}') {3} """.format(company,dept.name,date_to,empqry),as_dict=1,debug=0)
		
		if slip:
			
			for slp in slip:
				
				dt={}
				dt.update({'slip':slp.name})
				dt.update({'employee':slp.employee})
				dt.update({'employee_name':slp.employee_name})
				dt.update({'department':department_name})
				dt.update({'parent_department':parent_department_name})
				dt.update({'over_time':slp.over_time})				
				dt.update({'holiday_over_time':slp.holiday_over_time})			
						
				paid_leaves=get_paid_leave(slp.employee,date_to)
				dt.update({'paid_leaves':paid_leaves})				
				start_date=get_first_day(getdate(date_to))
				end_date=get_last_day(getdate(date_to))
				totdays=date_diff(end_date,start_date)+1
				holidays=get_holidays_for_employee(slp.employee, start_date, end_date, only_non_weekly=True)
				holiday=0
				if holidays:
					holiday=len(holidays)
				dt.update({'holiday':holiday})

				weekly_offs=get_holidays_for_employee(slp.employee, start_date, end_date, only_non_weekly=False)
				weekly_off=0
				if weekly_offs:
					weekly_off=len(weekly_offs)
				dt.update({'weekly_off':weekly_off})
				#'Annual Leave','Sick Leave','Maternity leave - Full Pay','Maternity leave - Half Pay'
				absent=get_absent(slp.employee,start_date,end_date)
				compensatory_off=leave_count(slp.employee,date_to,'Compensatory Off')
				annual_leave=leave_count(slp.employee,date_to,'Annual Leave')
				sick_leave=leave_count(slp.employee,date_to,'Sick Leave')
				m1=leave_count(slp.employee,date_to,'Maternity leave - Full Pay')
				m2=leave_count(slp.employee,date_to,'Maternity leave - Half Pay')
				maternity_leave=float(m1)+float(m2)
				
				leave_without_pay=leave_count(slp.employee,date_to,'Leave Without Pay')
				dt.update({'leave_without_pay':slp.leave_without_pay})	
				dt.update({'compensatory_off':compensatory_off})
				other=spl_leave(slp.employee,start_date,end_date)
				dt.update({'absent':absent})
				dt.update({'annual_leave':annual_leave})
				dt.update({'sick_leave':sick_leave})
				dt.update({'maternity_leave':maternity_leave})
				dt.update({'other':other})
				
				presnt=float(totdays)-float(holiday)-float(weekly_off)-float(absent)-float(annual_leave)-float(sick_leave)-float(maternity_leave)-float(other)-float(compensatory_off)-float(leave_without_pay)
				dt.update({'presnt':presnt})
				
				department_tot+=float(presnt or 0)
				parent_department_tot+=float(presnt or 0)
				dt.update({'department_tot':department_tot})
				dt.update({'parent_department_tot':parent_department_tot})

				emp_count+=1
				emp_count_pare_dept+=1
				emp_count_dept+=1
				dt.update({'emp_count':emp_count})
				dt.update({'emp_count_pare_dept':emp_count_pare_dept})
				dt.update({'emp_count_dept':emp_count_dept})	

				data.append(dt)
				
	#frappe.msgprint(str(data))
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)		
	
	if filters.get("department"):
		department=filters.get("department")
		dept="','".join([str(elem) for elem in department])
		conditions += "  and name in ('{0}') ".format(dept)

	return conditions


def get_paid_leave(emp,sal_date):
	absent=0
	sal3=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and MONTH(a.attendance_date)=MONTH('{1}') and YEAR(a.attendance_date)=YEAR('{1}') and l.is_ppl='1' """.format(emp,sal_date),as_dict=1,debug=0)
	if sal3:
		absent+=float(sal3[0].absent)/2
	
	sal4=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='On Leave' and a.employee='{0}' and MONTH(a.attendance_date)=MONTH('{1}') and YEAR(a.attendance_date)=YEAR('{1}') and l.is_lwp='0' and l.is_ppl='0' """.format(emp,sal_date),as_dict=1,debug=0)
	if sal4:
		absent+=sal4[0].absent
	
	sal6=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` a left join `tabLeave Type` l on l.name=a.leave_type 
	where a.docstatus=1 and a.status='Half Day' and a.employee='{0}' and MONTH(a.attendance_date)=MONTH('{1}') and YEAR(a.attendance_date)=YEAR('{1}') and l.is_lwp='0' and l.is_ppl='0'  """.format(emp,sal_date),as_dict=1,debug=0)
	if sal6:
		absent+=float(sal6[0].absent)/2
	
	return absent

def get_holidays_for_employee(employee, start_date, end_date, only_non_weekly=False):
	raise_exception=True
	holiday_list = get_holiday_list_for_employee(employee, raise_exception=raise_exception)

	if not holiday_list:
		return []

	filters = {"parent": holiday_list, "holiday_date": ("between", [start_date, end_date])}

	if only_non_weekly:
		filters["weekly_off"] = False
	else:
		filters["weekly_off"] = True

	holidays = frappe.get_all("Holiday", fields=["description", "holiday_date"], filters=filters,debug=0)

	return holidays

def leave_count(emp,sal_date,leave_type):
	absent=0
	sal4=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` 
	where docstatus=1 and status='On Leave' and employee='{0}' and MONTH(attendance_date)=MONTH('{1}') and YEAR(attendance_date)=YEAR('{1}') and leave_type='{2}'  """.format(emp,sal_date,leave_type),as_dict=1,debug=0)
	if sal4:
		absent+=sal4[0].absent
	
	sal6=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` 
	where docstatus=1 and status='Half Day' and employee='{0}' and MONTH(attendance_date)=MONTH('{1}') and YEAR(attendance_date)=YEAR('{1}') and leave_type='{2}' """.format(emp,sal_date,leave_type),as_dict=1,debug=0)
	if sal6:
		absent+=float(sal6[0].absent)/2

	return absent

def get_absent(emp,start_date,end_date):
	absent=0
	sal5=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where docstatus=1 and status='Absent' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}'""".format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal5:
		absent+=sal5[0].absent
	return absent

def spl_leave(emp,start_date,end_date):
	
	absent=0
	sal5=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where docstatus=1 and status='On Leave' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}' and leave_type not in ('Annual Leave','Sick Leave','Maternity leave - Full Pay','Maternity leave - Half Pay','Compensatory Off','Leave Without Pay') """.format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal5:
		absent+=sal5[0].absent

	sal6=frappe.db.sql(""" select count(*) as absent FROM `tabAttendance` where docstatus=1 and status='Half Day' and employee='{0}' 
	and attendance_date between '{1}' and  '{2}' and leave_type not in ('Annual Leave','Sick Leave','Maternity leave - Full Pay','Maternity leave - Half Pay','Compensatory Off','Leave Without Pay') """.format(emp,start_date,end_date),as_dict=1,debug=0)
	if sal6:
		absent+=float(sal6[0].absent)/2	
		
	return absent