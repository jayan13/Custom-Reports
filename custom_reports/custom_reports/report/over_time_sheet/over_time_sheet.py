# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,get_datetime,get_link_to_form,get_first_day,get_last_day

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
		"fieldname": "over_time_hr",
		"fieldtype": "Data",
		"label": "Nor @1.25",	
		"width": 100
		},
		{
		"fieldname": "holiday_over_time_hr",
		"fieldtype": "Data",
		"label": "Holiday hr @ 1.5 hr",	
		"width": 100
		},
		{
		"fieldname": "over_time_incentive",
		"fieldtype": "Data",
		"label": "Normal Incentive hr @1.25",	
		"width": 100
		},
		{
		"fieldname": "holiday_over_time_incentive",
		"fieldtype": "Data",
		"label": "Holi Incentive hr @1.5",	
		"width": 100
		},						
 	 ]
	compres=frappe.db.sql(""" select rmc.label,GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(company),as_dict=1,debug=0)	

	if compres:
		for comp in compres:
			lbl=comp.get("label")			
			lbl=lbl.lower()
			lbl=lbl.replace(" ", "_")

			columns.extend([
				{
				"fieldname": lbl,
				"fieldtype": "Float",
				"label": comp.label,	
				"width": 100
				}
				]) 

	columns.extend([
				{
		"fieldname": "net_pay",
		"fieldtype": "Float",
		"label": "Payment Amount",	
		"width": 100
		}
		])   
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
			parent_department_ovr=0
			parent_department_ovr_inc=0
			parent_department_holi=0
			parent_department_holi_inc=0
			

		if department != department_name:
			department_name=department
			department_tot=0
			emp_count_dept=0
			department_ovr=0
			department_ovr_inc=0
			department_holi=0
			department_holi_inc=0
			
		empqry=''
		if filters.get("employee"):
			emps=filters.get("employee")
			empq="','".join([str(elem) for elem in emps])
			empqry = "  and s.employee in ('{0}') ".format(empq)
		
		if filters.get("payroll_entry"):
			payroll_entry=filters.get("payroll_entry")
			empqry+=" and s.payroll_entry='{0}' ".format(payroll_entry)

		slip=frappe.db.sql(""" select s.*,e.department as emp_department from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus in (0,1) and s.company='{0}' and s.department='{1}' and MONTH(s.end_date)=MONTH('{2}') and YEAR(s.end_date)=YEAR('{2}') {3} """.format(company,dept.name,date_to,empqry),as_dict=1,debug=0)
		
		if slip:
			
			for slp in slip:
				
				dt={}
				dt.update({'slip':slp.name})
				dt.update({'employee':slp.employee})
				dt.update({'employee_name':slp.employee_name})
				dt.update({'department':department_name})
				dt.update({'parent_department':parent_department_name})

				over_time_incentive=0
				over_time=slp.over_time
				if float(slp.over_time) > 48:
					over_time_incentive=float(slp.over_time)-48
					over_time=48
				holiday_over_time_incentive=0
				holiday_over_time=slp.holiday_over_time
				if float(slp.holiday_over_time)>16:
					holiday_over_time_incentive=float(slp.holiday_over_time)-16
					holiday_over_time=16

				dt.update({'over_time_hr':over_time})				
				dt.update({'holiday_over_time_hr':holiday_over_time})
				dt.update({'over_time_incentive':over_time_incentive})				
				dt.update({'holiday_over_time_incentive':holiday_over_time_incentive})

				parent_department_ovr+=over_time
				parent_department_ovr_inc+=over_time_incentive
				parent_department_holi+=holiday_over_time
				parent_department_holi_inc+=holiday_over_time_incentive
				department_ovr+=over_time
				department_ovr_inc+=over_time_incentive
				department_holi+=holiday_over_time
				department_holi_inc+=holiday_over_time_incentive

				dt.update({'parent_department_ovr':parent_department_ovr})            	
				dt.update({'parent_department_holi':parent_department_holi})
				dt.update({'parent_department_ovr_inc':parent_department_ovr_inc})	
				dt.update({'parent_department_holi_inc':parent_department_holi_inc})	
				dt.update({'department_ovr':department_ovr})
				dt.update({'department_holi':department_holi})	
				dt.update({'department_ovr_inc':department_ovr_inc})            	
				dt.update({'department_holi_inc':department_holi_inc})				
							
				earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(slp.name),as_dict=1,debug=0)
				paid=0
				
				
				#frappe.msgprint(str(earnin))		
				compres=frappe.db.sql(""" select rmc.label,GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(company),as_dict=1,debug=0)	
				if compres:
					for comp in compres:
						lbl=comp.get("label")
						lbl=lbl.lower()
						lbl=lbl.replace(" ", "_")
						dt.update({lbl:0})

				if compres:
					for comp in compres:
						cmplist=comp.get("salary_component")
						cmplistar=cmplist.split(",")
						if earnin:
							for ern in earnin:
								if ern.salary_component in cmplistar:
									lbl=comp.get("label")
									lbl=lbl.lower()
									lbl=lbl.replace(" ", "_")
									dt.update({lbl:ern.amount})
									paid+=ern.amount
				paid=flt(paid,2)
				dt.update({'net_pay':paid})
				department_tot+=float(paid or 0)
				parent_department_tot+=float(paid or 0)
				dt.update({'department_tot':department_tot})
				dt.update({'parent_department_tot':parent_department_tot})
				if paid:
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