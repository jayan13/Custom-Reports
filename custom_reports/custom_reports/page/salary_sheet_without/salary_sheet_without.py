import frappe
from frappe.utils import formatdate, getdate, date_diff

@frappe.whitelist()
def get_report(payroll_entry=None):
    data = {}
    payro=frappe.db.get_value("Payroll Entry",payroll_entry,['start_date','end_date','company'], as_dict=1)
    data['company']=payro.company
    data['start_date']=frappe.utils.formatdate(payro.start_date, "MMMM yyyy")
    data['end_date']=frappe.utils.formatdate(payro.end_date, "MMMM yyyy")    
    
    slip=frappe.db.sql(""" select s.*,d.name as department,IF(d.parent_department='All Departments',d.name,d.parent_department) as parent_department 
    from `tabSalary Slip` s 
    left join `tabDepartment` d on d.name=s.department where  s.docstatus in (0,1) and s.payroll_entry='{0}'  order by d.parent_department,d.name,s.employee """.format(payroll_entry),as_dict=1,debug=0)
    slips=[]
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
    department_basic_tot=0
    department_basic_pay_tot=0
    department_allowance_tot=0
    parent_department_basic_tot=0
    parent_department_basic_pay_tot=0
    parent_department_allowance_tot=0

    if slip:
        for slp in slip:
            department=slp.department.split('-')[0] if slp.department else ''
            parent_department=slp.parent_department.split('-')[0] if slp.parent_department else ''
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
				
            paid_leaves=get_paid_leave(slp.employee,payro.end_date)
            dt.update({'paid_leaves':paid_leaves})
            dt.update({'over_time':slp.over_time})
            dt.update({'holiday_over_time':slp.holiday_over_time})

            

            base=frappe.db.get_value('Salary Structure Assignment',{'salary_structure':slp.salary_structure,'employee':slp.employee},'base') or 0
            dt.update({'basic':base})
            earnings=[]
            deductions=[]
            salary_structure=[]
            earn_tot=0
            sal_stru=frappe.db.get_all('Salary Detail',filters={'parent':slp.salary_structure,'amount':['>',0],'parentfield':'earnings'},fields=['salary_component','amount'],order_by='idx asc')
            if sal_stru:
                salary_structure=sal_stru
                earn_tot=sum(d.get('amount') for d in sal_stru)

            compres=frappe.db.sql(""" select GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(payro.company),as_dict=1,debug=0)	
            compo=[]
            if compres:
                for comp in compres:
                    cmplist=comp.get("salary_component")
                    cmplistar=cmplist.split(",")
                    compo+=cmplistar

            earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}'  order by idx""".format(slp.name),as_dict=1,debug=0)
            basic_paid=0
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
            deduct=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='deductions' and parent ='{0}' order by idx""".format(slp.name),as_dict=1,debug=0)
            if deduct:
                deductions=deduct
            dt.update({'deductions':deductions})
            dt.update({'basic_paid':basic_paid})
            dt.update({'salary_structure':salary_structure})
            dt.update({'earn_tot':earn_tot})
            allowance=float(slp.gross_pay)-float(basic_paid)
            dt.update({'allowance':allowance})
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
            parent_department_tot+=float(net_pay or 0)
            department_tot+=float(net_pay or 0)           
            department_ern_tot+=float(gross_pay or 0)
            parent_department_ern_tot+=float(gross_pay or 0)
            parent_department_ded_tot+=float(slp.total_deduction or 0)           
            
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
            slips.append(dt)

        dt={}
        basic=sum(d.get('basic') for d in slips)
        dt.update({'basic':basic})
        basic_paid=sum(d.get('basic_paid') for d in slips)
        dt.update({'basic_paid':basic_paid})
        allowance=sum(d.get('allowance') for d in slips)
        dt.update({'allowance':allowance})
        gross_pay=sum(d.get('gross_pay') for d in slips)
        dt.update({'gross_pay':gross_pay})
        total_deduction=sum(d.get('total_deduction') for d in slips)
        dt.update({'total_deduction':total_deduction})
        net_pay=sum(d.get("net_pay") for d in slips)
        dt.update({'net_pay':net_pay})
        slips.append(dt)
    data['data']=slips
    return data

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
    

    
    