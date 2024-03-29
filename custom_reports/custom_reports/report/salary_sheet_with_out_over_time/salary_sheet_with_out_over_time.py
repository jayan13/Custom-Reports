# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

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
		"fieldname": "payment_days",
		"fieldtype": "Float",
		"label": "Paid Days",	
		"width": 100
		},
		{
		"fieldname": "paid_leaves",
		"fieldtype": "Float",
		"label": "Paid Leaves",	
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
		{
		"fieldname": "basic",
		"fieldtype": "Float",
		"label": "Basic Salay",	
		"width": 100
		},
		{
		"fieldname": "basic_paid",
		"fieldtype": "Float",
		"label": "Basic Paid",	
		"width": 100
		},
		{
		"fieldname": "allowance",
		"fieldtype": "Float",
		"label": "Total Allowance / Earning",	
		"width": 100
		},
		{
		"fieldname": "gross_pay",
		"fieldtype": "Float",
		"label": "Gross Salary",	
		"width": 100
		},
		{
		"fieldname": "total_deduction",
		"fieldtype": "Float",
		"label": "Total Deduction",	
		"width": 100
		},
		{
		"fieldname": "net_pay",
		"fieldtype": "Float",
		"label": "Net Salary",	
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
	parent_department_ern_tot=0
	parent_department_ded_tot=0
	department_tot=0
	department_ern_tot=0
	department_ded_tot=0
	for dept in conc:		
		department=dept.name.split('-')[0]
		parent_department=dept.parent_department.split('-')[0]
		if parent_department != parent_department_name:
			parent_department_name=parent_department
			parent_department_tot=0
			parent_department_ern_tot=0
			parent_department_ded_tot=0			
			emp_count_pare_dept=0
			parent_department_basic_tot=0
			parent_department_basic_pay_tot=0
			parent_department_allowance_tot=0
			

		if department != department_name:
			department_name=department
			department_tot=0
			department_ern_tot=0
			department_ded_tot=0			
			emp_count_dept=0
			department_basic_tot=0
			department_basic_pay_tot=0
			department_allowance_tot=0
			
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
			#gross_pay net_pay
			for slp in slip:
				emp_count+=1
				emp_count_pare_dept+=1
				emp_count_dept+=1
				gross_pay=slp.gross_pay
				net_pay=slp.net_pay
				dt={}
				dt.update({'slip':slp.name})
				dt.update({'employee':slp.employee})
				dt.update({'employee_name':slp.employee_name})
				dt.update({'department':department_name})
				dt.update({'parent_department':parent_department_name})
				dt.update({'gross_pay':gross_pay})
				dt.update({'net_pay':net_pay})
				dt.update({'total_deduction':slp.total_deduction})
				dt.update({'leave_without_pay':slp.leave_without_pay or 0+slp.absent_days or 0})				
				dt.update({'payment_days':slp.payment_days})
				
				paid_leaves=get_paid_leave(slp.employee,date_to)
				dt.update({'paid_leaves':paid_leaves})
				dt.update({'over_time':slp.over_time})
				dt.update({'holiday_over_time':slp.holiday_over_time})

				

				base=frappe.db.get_value('Salary Structure Assignment',{'salary_structure':slp.salary_structure,'employee':slp.employee},'base') or 0
				dt.update({'basic':base})
				earnings=[]
				deductions=[]
				earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(slp.name),as_dict=1,debug=0)
				basic_paid=0

				compres=frappe.db.sql(""" select GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(company),as_dict=1,debug=0)	
				compo=[]
				if compres:
					for comp in compres:
						cmplist=comp.get("salary_component")
						cmplistar=cmplist.split(",")
						compo+=cmplistar
				
				if earnin:
					for ern in earnin:
						if 'Basic' in str(ern.salary_component):
							basic_paid=ern.amount 
						else:
							if ern.salary_component in compo:
								gross_pay-=ern.amount
								net_pay-=ern.amount
								dt.update({'gross_pay':gross_pay})
								dt.update({'net_pay':net_pay})
							else:
								earnings.append(ern)

				dt.update({'earnings':earnings})
				deduct=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='deductions' and parent ='{0}' """.format(slp.name),as_dict=1,debug=0)
				if deduct:
					deductions=deduct
				dt.update({'deductions':deductions})
				dt.update({'basic_paid':basic_paid})
				allowance=float(gross_pay)-float(basic_paid)
				dt.update({'allowance':allowance})
				parent_department_tot+=float(net_pay or 0)
				parent_department_ern_tot+=float(gross_pay or 0)
				parent_department_ded_tot+=float(slp.total_deduction or 0)
				department_tot+=float(net_pay or 0)
				department_ern_tot+=float(gross_pay or 0)
				department_ded_tot+=float(slp.total_deduction or 0)
				dt.update({'emp_count':emp_count})
				dt.update({'emp_count_pare_dept':emp_count_pare_dept})
				dt.update({'emp_count_dept':emp_count_dept})
				dt.update({'parent_department_tot':parent_department_tot})
				dt.update({'parent_department_ern_tot':parent_department_ern_tot})
				dt.update({'parent_department_ded_tot':parent_department_ded_tot})
				dt.update({'department_tot':department_tot})
				dt.update({'department_ern_tot':department_ern_tot})
				dt.update({'department_ded_tot':department_ded_tot})

				department_basic_tot+=base
				department_basic_pay_tot+=basic_paid
				department_allowance_tot+=allowance
				parent_department_basic_tot+=base
				parent_department_basic_pay_tot+=basic_paid
				parent_department_allowance_tot+=allowance
				dt.update({'department_basic_tot':department_basic_tot})
				dt.update({'department_basic_pay_tot':department_basic_pay_tot})
				dt.update({'department_allowance_tot':department_allowance_tot})
				dt.update({'parent_department_basic_tot':parent_department_basic_tot})
				dt.update({'parent_department_basic_pay_tot':parent_department_basic_pay_tot})
				dt.update({'parent_department_allowance_tot':parent_department_allowance_tot})
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