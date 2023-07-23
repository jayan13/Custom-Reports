# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,get_datetime,get_link_to_form,get_first_day,get_last_day

def execute(filters=None):
	if not filters:
		filters = {}
	
	earnings=[]
	deductions=[]
	earnsql=frappe.db.sql(""" select DISTINCT(TRIM(SUBSTRING_INDEX(d.salary_component,'(',1))) AS salary_component from `tabSalary Structure` s left join `tabSalary Detail` d on d.parent=s.name  where d.parentfield='earnings' and d.amount>0 and s.company='{0}' order by salary_component """.format(filters.get("company")),as_dict=1)
	for ern in earnsql:
		earnings.append(ern.salary_component)
	dedusql=frappe.db.sql(""" select DISTINCT(TRIM(SUBSTRING_INDEX(d.salary_component,'(',1))) AS salary_component from `tabSalary Structure` s left join `tabSalary Detail` d on d.parent=s.name  where d.parentfield='deductions' and d.amount>0 and s.company='{0}' order by salary_component """.format(filters.get("company")),as_dict=1)
	for dedu in dedusql:
		deductions.append(dedu.salary_component)
	conditions=get_conditions(filters,earnings,deductions)
	#frappe.throw(str(deductions))
	return get_columns(earnings,deductions), get_data(conditions,filters,earnings,deductions)


def get_columns(earnings,deductions):
	
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
		"fieldname": "from_date",
		"fieldtype": "Date",
		"label": "Salary Effective Date",	
		"width": 150
		},
				
 	 ]
	if earnings:
		for ern in earnings:
			fldname=ern.replace(" ", "_").lower()
			columns.append({
			"fieldname": fldname,
			"fieldtype": "Currency",
			"label": ern,	
			"width": 100
			})
	if deductions:
		for ern in deductions:
			fldname=ern.replace(" ", "_").lower()
			columns.append({
			"fieldname": fldname,
			"fieldtype": "Currency",
			"label": ern,	
			"width": 100
			})

	columns.append({
			"fieldname": 'total',
			"fieldtype": "Currency",
			"label": 'Total',	
			"width": 100
			})

	return columns

def get_data(conditions,filters,earnings,deductions):
	data=[]
	
	date_to=filters.get("date_to")
	company=filters.get("company")
	conc=frappe.db.sql(""" select name,IF(parent_department='All Departments',name,parent_department) as parent_department from `tabDepartment` where %s  order by parent_department,name"""% (conditions),as_dict=1,debug=0)
	parent_department_name=''
	department_name=''
	for dept in conc:		
		department=dept.name.split('-')[0]
		parent_department=dept.parent_department.split('-')[0]
		if parent_department != parent_department_name:
			parent_department_name=parent_department
		if department != department_name:
			department_name=department

		empqry=''
		if filters.get("employee"):
			emps=filters.get("employee")
			empq="','".join([str(elem) for elem in emps])
			empqry = "  and e.name in ('{0}') ".format(empq)

		
		employee=frappe.db.sql(""" select e.department as emp_department,e.employee_name,e.name as employee from `tabEmployee` e where e.company='{0}' and e.status='Active' and e.department='{1}'  {2} """.format(company,dept.name,empqry),as_dict=1,debug=0)
		if employee:
			for emp in employee:
				dt={}
				dt.update({'employee':emp.employee})
				dt.update({'employee_name':emp.employee_name})
				dt.update({'department':department_name})
				dt.update({'parent_department':parent_department_name})
				salary_structure=''
				struass=frappe.db.sql(""" select s.salary_structure,s.name,s.from_date from `tabSalary Structure Assignment` s  where s.docstatus=1 and s.employee='{0}'  order by s.from_date DESC """.format(emp.employee),as_dict=1,debug=0)
				if struass:
					salary_structure=struass[0].salary_structure
					dt.update({'from_date':struass[0].from_date})

				esql=''	
				if len(earnings):
					for ern in earnings:
						salary_component=str(ern)
						fldname=salary_component.replace(" ", "_").lower()
						dt.update({fldname:0})
					es="','".join([str(elem) for elem in earnings])
					esql = "  and TRIM(SUBSTRING_INDEX(d.salary_component,'(',1)) in ('{0}') ".format(es)
				
				desql=''
				if len(deductions):
					for dedu in deductions:
						salary_component=str(dedu)
						fldname=salary_component.replace(" ", "_").lower()
						dt.update({fldname:0})

					de="','".join([str(elem) for elem in deductions])
					desql = "  and TRIM(SUBSTRING_INDEX(d.salary_component,'(',1)) in ('{0}') ".format(de)
				tot=0
				
				if salary_structure:
					er_tot=0
					if esql:
						earnsql=frappe.db.sql(""" select TRIM(SUBSTRING_INDEX(d.salary_component,'(',1)) AS salary_component,d.amount from  `tabSalary Detail` d  where d.parentfield='earnings' and d.amount>0 and d.parent='{0}' {1} order by salary_component """.format(salary_structure,esql),as_dict=1)
						for ern in earnsql:
							salary_component=str(ern.salary_component)
							fldname=salary_component.replace(" ", "_").lower()
							dt.update({fldname:ern.amount})
							er_tot+=float(ern.amount)
					de_tot=0
					if desql:						
						dedusql=frappe.db.sql(""" select TRIM(SUBSTRING_INDEX(d.salary_component,'(',1)) AS salary_component,d.amount from  `tabSalary Detail` d  where d.parentfield='deductions' and d.amount>0 and d.parent='{0}' {1} order by salary_component """.format(salary_structure,desql),as_dict=1)
						for dedu in dedusql:
							salary_component=str(dedu.salary_component)
							fldname=salary_component.replace(" ", "_").lower()
							dt.update({fldname:dedu.amount})
							de_tot+=float(dedu.amount)
					tot=er_tot-de_tot
					
				dt.update({'total':tot})
				data.append(dt)

	return data

def get_conditions(filters,earnings,deductions):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)		
	
	if filters.get("department"):
		department=filters.get("department")
		dept="','".join([str(elem) for elem in department])
		conditions += "  and name in ('{0}') ".format(dept)

	return conditions