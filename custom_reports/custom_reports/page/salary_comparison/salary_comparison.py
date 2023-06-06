import frappe
from frappe.utils import formatdate, getdate, date_diff, flt,get_first_day,get_last_day,add_days

@frappe.whitelist()
def get_report(payroll_entry=None):
    data = {}
    #payro={}
    payro=frappe.db.get_value("Payroll Entry",payroll_entry,['start_date','end_date','company'], as_dict=1)
    
    #payrosql=frappe.db.get_all("Payroll Entry", filters={'company':company,'docstatus':'1'}, fields=['start_date','end_date','name','company'], order_by='start_date desc', start=0, page_length=1,debug=0)
    
    #if payrosql:
     #   payro=payrosql[0]
    #else:
    #    return data

    months=[]
    #payroll_entry=payro.name
    data['company']=payro.company
    data['start_date']=frappe.utils.formatdate(payro.start_date, "MMMM yyyy")
    data['end_date']=frappe.utils.formatdate(payro.end_date, "MMMM yyyy")    
    
    prvmth=add_days(get_first_day(getdate(payro.start_date)),-1)
    pprvmth=add_days(get_first_day(getdate(prvmth)),-1)

    months.append(frappe.utils.formatdate(payro.start_date, "MMM yy"))
    months.append(frappe.utils.formatdate(prvmth, "MMM yy"))
    months.append(frappe.utils.formatdate(pprvmth, "MMM yy"))
    data['months']=months
    
    slip=frappe.db.sql(""" select s.name,s.employee,s.salary_structure,s.employee_name,s.gross_pay,s.net_pay,s.total_deduction,s.leave_without_pay,s.payment_days,s.over_time,s.holiday_over_time,
    d.name as department,IF(d.parent_department='All Departments',d.name,d.parent_department) as parent_department 
    from `tabSalary Slip` s 
    left join `tabDepartment` d on d.name=s.department where  s.docstatus in (0,1) and s.payroll_entry='{0}'  order by d.parent_department,d.name,s.employee """.format(payroll_entry),as_dict=1,debug=0)
    
    compres=frappe.db.sql(""" select rmc.label,GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(payro.company),as_dict=1,debug=0)	
    
    slips=[]

    emp_count=0
    emp_count_dept=0
    emp_count_pare_dept=0
    s1_department_tot=0
    s2_department_tot=0
    s3_department_tot=0
    o1_department_tot=0
    o2_department_tot=0
    o3_department_tot=0
    s1_parent_department=0
    s2_parent_department=0
    s3_parent_department=0
    o1_parent_department=0
    o2_parent_department=0
    o3_parent_department=0
    parent_department_name=''
    department_name=''

    s1_gtot=0
    s2_gtot=0
    s3_gtot=0
    o1_gtot=0
    o2_gtot=0
    o3_gtot=0
    
    if slip:
        for slp in slip:
            department=slp.department.split('-')[0] if slp.department else ''
            parent_department=slp.parent_department.split('-')[0] if slp.parent_department else ''
            if parent_department != parent_department_name:
                parent_department_name=parent_department               	
                emp_count_pare_dept=0
                s1_parent_department=0
                s2_parent_department=0
                s3_parent_department=0
                o1_parent_department=0
                o2_parent_department=0
                o3_parent_department=0

            if department != department_name:
                department_name=department                              			
                emp_count_dept=0
                s1_department_tot=0
                s2_department_tot=0
                s3_department_tot=0
                o1_department_tot=0
                o2_department_tot=0
                o3_department_tot=0
                
            dt={}
            dt.update({'slip':slp.name})
            dt.update({'employee':slp.employee})
            dt.update({'employee_name':slp.employee_name})
            dt.update({'department':department_name})
            dt.update({'parent_department':parent_department_name})
							
            earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(slp.name),as_dict=1,debug=0)
            overtime=0
            sal=0
            if compres:
                for comp in compres:
                    cmplist=comp.get("salary_component")
                    cmplistar=cmplist.split(",")
                    if earnin:
                        for ern in earnin:
                            if ern.salary_component in cmplistar:
                                overtime+=ern.amount
                            
            sal=slp.net_pay-overtime                    
            #sal=flt(sal,2)
            #overtime=flt(overtime,2)
            
            dt.update({'overtime':overtime})
            dt.update({'sal':sal})
            s1_parent_department+=sal
            s1_department_tot+=sal
            o1_parent_department+=overtime
            o1_department_tot+=overtime
            s1_gtot+=sal
            o1_gtot+=overtime

            p1=frappe.db.sql(""" select name,net_pay from `tabSalary Slip` where  docstatus in (0,1) and employee='{0}' and MONTH(start_date)=MONTH('{1}') and YEAR(start_date)=YEAR('{1}') """.format(slp.employee,prvmth),as_dict=1,debug=0)
            if p1:
                earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(p1[0].name),as_dict=1,debug=0)
                overtime=0
                sal=0
                if compres:
                    for comp in compres:
                        cmplist=comp.get("salary_component")
                        cmplistar=cmplist.split(",")
                        if earnin:
                            for ern in earnin:
                                if ern.salary_component in cmplistar:
                                    overtime+=ern.amount
                                
                sal=p1[0].net_pay-overtime                    
                #sal=flt(sal,2)
                #overtime=flt(overtime,2)
                dt.update({'overtimep':overtime})
                dt.update({'salp':sal})
                s2_parent_department+=sal
                s2_department_tot+=sal
                o2_parent_department+=overtime
                o2_department_tot+=overtime
                s2_gtot+=sal
                o2_gtot+=overtime

            else:
                dt.update({'overtimep':0})
                dt.update({'salp':0})

            p2=frappe.db.sql(""" select name,net_pay from `tabSalary Slip` where  docstatus in (0,1) and employee='{0}' and MONTH(start_date)=MONTH('{1}') and YEAR(start_date)=YEAR('{1}')  """.format(slp.employee,pprvmth),as_dict=1,debug=0)
            if p2:
                earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}' """.format(p2[0].name),as_dict=1,debug=0)
                overtime=0
                sal=0
                if compres:
                    for comp in compres:
                        cmplist=comp.get("salary_component")
                        cmplistar=cmplist.split(",")
                        if earnin:
                            for ern in earnin:
                                if ern.salary_component in cmplistar:
                                    overtime+=ern.amount
                                
                sal=p2[0].net_pay-overtime                    
                #sal=flt(sal,2)
                #overtime=flt(overtime,2)
                dt.update({'overtimepp':overtime})
                dt.update({'salpp':sal})
                s3_parent_department+=sal
                s3_department_tot+=sal
                o3_parent_department+=overtime
                o3_department_tot+=overtime
                s3_gtot+=sal
                o3_gtot+=overtime

            else:
                dt.update({'overtimepp':0})
                dt.update({'salpp':0})
            
            emp_count+=1
            emp_count_pare_dept+=1
            emp_count_dept+=1
            dt.update({'emp_count':emp_count})
            dt.update({'emp_count_pare_dept':emp_count_pare_dept})
            dt.update({'emp_count_dept':emp_count_dept})
            
            dt.update({'s1_parent_department':s1_parent_department})
            dt.update({'s2_parent_department':s2_parent_department})
            dt.update({'s3_parent_department':s3_parent_department})
            dt.update({'o1_parent_department':o1_parent_department})
            dt.update({'o2_parent_department':o2_parent_department})
            dt.update({'o3_parent_department':o3_parent_department})
            dt.update({'s1_department_tot':s1_department_tot})
            dt.update({'s2_department_tot':s2_department_tot})
            dt.update({'s3_department_tot':s3_department_tot})
            dt.update({'o1_department_tot':o1_department_tot})
            dt.update({'o2_department_tot':o2_department_tot})
            dt.update({'o3_department_tot':o3_department_tot})

            slips.append(dt)
        
        
        dt={}
        dt.update({'s1_department_tot':s1_gtot})
        dt.update({'s2_department_tot':s2_gtot})
        dt.update({'s3_department_tot':s3_gtot})
        dt.update({'o1_department_tot':o1_gtot})
        dt.update({'o2_department_tot':o2_gtot})
        dt.update({'o3_department_tot':o3_gtot})
        slips.append(dt)
        

    data['data']=slips
    #frappe.throw(str(data))
    return data

      
    

    
    