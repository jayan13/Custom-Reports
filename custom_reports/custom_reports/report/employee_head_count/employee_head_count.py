# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,get_datetime,get_link_to_form,get_first_day,get_last_day

def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data(conditions,filters)

def get_columns():
	
	columns = [
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
		"fieldname": "last_month",
		"fieldtype": "Int",
		"label": "Last Month",	
		"width": 150
		},
		{
		"fieldname": "new_joined",
		"fieldtype": "Int",
		"label": "New Joined",	
		"width": 150
		},
		{
		"fieldname": "employees_left",
		"fieldtype": "Int",
		"label": "Employees Left",	
		"width": 150
		},		
		{
		"fieldname": "current_month",
		"fieldtype": "Int",
		"label": "Current Month",	
		"width": 150
		}
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	data=[]
	
	date_to=filters.get("date_to")
	company=filters.get("company")
		
	#mnth=frappe.utils.formatdate(date_to, "MMMM yyyy")	
	#filters.update({'month':mnth})
	
	conc=frappe.db.sql(""" select name,IF(parent_department='All Departments',name,parent_department) as parent_department from `tabDepartment` where %s  order by parent_department,name"""% (conditions),as_dict=1,debug=0)
	
	
	parent_department_name=''
	parent_department_last=0
	parent_department_new=0
	parent_department_left=0
	parent_department_current=0
	data=[]
	for dept in conc:
		parent_department=dept.parent_department.split('-')[0]
		department=dept.name.split('-')[0]
		if parent_department != parent_department_name:
			parent_department_name=parent_department
			parent_department_last=0
			parent_department_new=0
			parent_department_left=0
			parent_department_current=0

		dt={}				
		dt.update({'department':department})
		dt.update({'parent_department':parent_department_name})
		current_month=0
		employees_left=0
		new_joined=0
		last_month=0
		lmonth=add_days(get_first_day(getdate(date_to)),-1)

		pvmonth=frappe.db.sql(""" select count(e.employee) as cnt from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{2}') 
		 and YEAR(s.end_date)=YEAR('{2}')  group by e.department """.format(company,dept.name,lmonth),as_dict=1,debug=0)
		if pvmonth:
			last_month=pvmonth[0].cnt
			parent_department_last+=last_month

		newjoi=frappe.db.sql(""" select count(e.employee) as cnt from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{2}') 
		 and YEAR(s.end_date)=YEAR('{2}') and e.employee not in(select e.employee from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{3}') 
		 and YEAR(s.end_date)=YEAR('{3}')) and (select count(e.employee) from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{3}') 
		 and YEAR(s.end_date)=YEAR('{3}')) > 0 group by e.department """.format(company,dept.name,date_to,lmonth),as_dict=1,debug=0)
		#YEAR(e.date_of_joining)=YEAR('{2}') and MONTH(e.date_of_joining)=MONTH('{2}')
		if newjoi:
			new_joined=newjoi[0].cnt
			parent_department_new+=new_joined

		left=frappe.db.sql(""" select count(e.employee) as cnt from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{2}') 
		 and YEAR(s.end_date)=YEAR('{2}') and e.employee not in(select e.employee from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{3}') 
		 and YEAR(s.end_date)=YEAR('{3}')) and (select count(e.employee) from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{3}') 
		 and YEAR(s.end_date)=YEAR('{3}'))>0 group by e.department """.format(company,dept.name,lmonth,date_to),as_dict=1,debug=0)
		#YEAR(e.relieving_date)=YEAR('{2}') and MONTH(e.relieving_date)=MONTH('{2}')
		if left:
			employees_left=left[0].cnt
			parent_department_left+=employees_left

		current=frappe.db.sql(""" select count(e.employee) as cnt from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and (s.department='{1}' or e.department='{1}') and MONTH(s.end_date)=MONTH('{2}') 
		 and YEAR(s.end_date)=YEAR('{2}')  group by e.department """.format(company,dept.name,date_to),as_dict=1,debug=0)
		if current:
			current_month=current[0].cnt
			parent_department_current+=current_month

		dt.update({'last_month':last_month})
		dt.update({'new_joined':new_joined})
		dt.update({'employees_left':employees_left})
		dt.update({'current_month':current_month})
		dt.update({'parent_department_last':parent_department_last})
		dt.update({'parent_department_new':parent_department_new})
		dt.update({'parent_department_left':parent_department_left})
		dt.update({'parent_department_current':parent_department_current})
		
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
