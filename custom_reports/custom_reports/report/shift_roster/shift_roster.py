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
	cndd=conditions+" and (e.relieving_date is null or e.relieving_date > '{0}')".format(filters.get("date_from"))
	employee=frappe.db.sql(""" select r.employee,e.employee_name from `tabEmployee Shift Roster` r left join `tabShift Roster` s on r.shift_roster=s.name left join `tabEmployee` e on e.name=r.employee where  %s group by r.employee order by r.employee"""% (cndd),as_dict=1,debug=0)
	
	for emp in employee:

		cond=conditions+" and r.employee= '{0}' ".format(emp.employee)
		attn=frappe.db.sql(""" select r.day,r.day_type from `tabEmployee Shift Roster` r left join `tabShift Roster` s on r.shift_roster=s.name where  %s  order by r.day"""% (cond),as_dict=1,debug=0)
		precnt=0
		totcnt=len(attn)
		for at in attn:
			label=str(at.day).replace('-','_')
			emp.update({label:at.day_type})
			if at.day_type in ['P','OW']:				
				precnt+=1
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
		conditions += " and r.day >= '{0}'".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and r.day <= '{0}'".format(date_to)
	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += "  and r.employee = '{0}'".format(employee)

	return conditions


	

