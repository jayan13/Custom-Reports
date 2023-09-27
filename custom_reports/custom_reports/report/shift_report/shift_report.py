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
	rounded,cstr
)
from erpnext.hr.utils import get_holiday_dates_for_employee

def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(filters), get_data(conditions,filters)

def get_columns(filters):
	date_from=filters.get("date_from")
	date_to=filters.get("date_to")
	date_from=add_days(getdate(date_from),-1)
	daycount=date_diff(getdate(date_to),getdate(date_from))
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
		"label": "Name",		
		"width": 200
		}
 	 ]
	wekkday=['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
	
	for x in range(daycount):
					
		date_from=add_days(getdate(date_from),1)
		d=add_days(getdate(date_from),1).weekday()
		cwday=cstr(formatdate(date_from))+'<br>'+str(wekkday[d])
		label=str(date_from).replace('-','_')		
		columns.extend([
				{
				"label": cwday,
				"fieldname": label,
				"fieldtype": "Data",
				"width": 60
				}
				])

	columns.extend([
				{
				"label": 'Tot Days',
				"fieldname": 'total_days',
				"fieldtype": "Data",
				"width": 60
				},
				{"label": 'Tot Present',
				"fieldname": 'total_present',
				"fieldtype": "Data",
				"width": 60
				}
				])
		
	return columns

def get_data(conditions,filters):
	shifts={}
	shift_types=frappe.db.get_all('Shift Type',fields=['name','start_time','end_time'])
	for shf in shift_types:
		start_time=str(shf.start_time).split(':')
		end_time=str(shf.end_time).split(':')
		label=str(start_time[0])+':'+str(start_time[1])+'-'+str(end_time[0])+':'+str(end_time[1])
		shifts.update({shf.name:label})
	cndd=conditions+" and (e.relieving_date is null or e.relieving_date > '{0}')".format(filters.get("date_from"))
	employee=frappe.db.sql(""" select r.employee,e.employee_name from `tabEmployee Shift Roster` r left join `tabShift Roster` s on r.shift_roster=s.name left join `tabEmployee` e on e.name=r.employee where  %s group by r.employee order by r.employee"""% (cndd),as_dict=1,debug=0)
	
	for emp in employee:

		cond=conditions+" and r.employee= '{0}' ".format(emp.employee)
		attn=frappe.db.sql(""" select r.day,r.day_type,r.shift_type from `tabEmployee Shift Roster` r left join `tabShift Roster` s on r.shift_roster=s.name where  %s  order by r.day"""% (cond),as_dict=1,debug=0)
		precnt=0
		totcnt=len(attn)
		for at in attn:
			
			label=str(at.day).replace('-','_')
			if at.day_type in ['P','OW']:
				day_type=shifts.get(at.shift_type)
				precnt+=1
			else:
				day_type='OFF'
			emp.update({label:day_type})
		emp.update({'total_days':totcnt})
		emp.update({'total_present':precnt})
	return employee

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and s.company= '{0}' ".format(company)
	
	if filters.get("department"):
		department=filters.get("department")
		dept="','".join([str(elem) for elem in department])
		conditions += "  and s.department in ('{0}') ".format(dept)

	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += "  and r.day >= '{0}'".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and r.day <= '{0}'".format(date_to)
	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += "  and r.employee = '{0}'".format(employee)

	return conditions


	

