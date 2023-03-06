import frappe
from frappe.utils import formatdate, getdate, date_diff, flt

@frappe.whitelist()
def get_report(payroll_entry=None):
    data = {}
    payro=frappe.db.get_value("Payroll Entry",payroll_entry,['start_date','end_date','company'], as_dict=1)
    data['company']=payro.company
    data['start_date']=frappe.utils.formatdate(payro.start_date, "MMMM yyyy")
    data['end_date']=frappe.utils.formatdate(payro.end_date, "MMMM yyyy")    
    
    slip=frappe.db.sql(""" select s.name,s.employee,s.salary_structure,s.employee_name,s.gross_pay,s.net_pay,s.total_deduction,s.leave_without_pay,s.payment_days,
    d.name as department,IF(d.parent_department='All Departments',d.name,d.parent_department) as parent_department 
    from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee 
    left join `tabDepartment` d on d.name=e.department where  s.docstatus in (0,1) and s.payroll_entry='{0}'  order by d.parent_department,d.name """.format(payroll_entry),as_dict=1,debug=0)
    
    compres=frappe.db.sql(""" select rmc.label,GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(payro.company),as_dict=1,debug=0)	
    compn=[]
    if compres:
        for comp in compres:
            lbl=comp.get("label")			
            lbl=lbl.lower()
            lbl=lbl.replace(" ", "_")
            compn.append({"label":comp.label,"salary_component":lbl})
    data['compn']=compn
    slips=[]

    emp_count=0
    emp_count_dept=0
    emp_count_pare_dept=0
    parent_department_name=''
    department_name=''
    parent_department_tot=0	
    department_tot=0

    if slip:
        for slp in slip:
            department=slp.department.split('-')[0] if slp.department else ''
            parent_department=slp.parent_department.split('-')[0] if slp.parent_department else ''
            if parent_department != parent_department_name:
                parent_department_name=parent_department
                parent_department_tot=0		
                emp_count_pare_dept=0

            if department != department_name:
                department_name=department
                department_tot=0                			
                emp_count_dept=0
                

            
            dt={}
            dt.update({'slip':slp.name})
            dt.update({'employee':slp.employee})
            dt.update({'employee_name':slp.employee_name})
            dt.update({'department':department_name})
            dt.update({'parent_department':parent_department_name})
            dt.update({'over_time':slp.over_time})				
            dt.update({'holiday_over_time':slp.holiday_over_time})
            
							
            earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(slp.name),as_dict=1,debug=0)
            paid=0

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
                slips.append(dt)
        
        dt={}
        net_pay=sum(d.get("net_pay") for d in slips)
        dt.update({'net_pay':net_pay})
        slips.append(dt)

    data['data']=slips
    return data

      
    

    
    