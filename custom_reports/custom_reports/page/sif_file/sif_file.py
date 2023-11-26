import frappe
from frappe.utils import formatdate, getdate, date_diff, flt
from datetime import datetime

@frappe.whitelist()
def get_report(company,payroll_entry=None,start_date=None,mol=None,employee=None):
	data = {}
	#data['company']=company
	data['slip']=[]
	dt=[]
	if payroll_entry or start_date:
		filt=''
		if payroll_entry:
			filt+=" and s.payroll_entry='{0}' ".format(payroll_entry)

		if mol:
			filt+=" and e.ministry_of_labor_employer_id='{0}' ".format(mol)

		if start_date:
			filt+=" and MONTH(s.end_date)=MONTH('{0}') and YEAR(s.end_date)=YEAR('{0}')".format(start_date)

		if employee:
			filt+=" and s.employee='{0}' ".format(employee)
		compres=frappe.db.sql(""" select GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(company),as_dict=1,debug=0)
		compo=[]
		if compres:
			for comp in compres:
				cmplist=comp.get("salary_component")
				cmplistar=cmplist.split(",")
				compo+=cmplistar
		
		sqldt =frappe.db.sql(""" 
		select s.name,s.employee,s.employee_name,e.ministry_of_labor_employer_id,e.employee_labor_card_number,e.bank_ac_no,
		e.routing_number,s.net_pay as fix_pay,0 as vary_pay,s.leave_without_pay,s.payment_days,s.start_date,s.end_date 
		from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee 
		where s.docstatus=1 and s.company='{0}' {1} """.format(company,filt),as_dict=1,debug=0)
		for slp in sqldt:
			fix_pay=slp.get('fix_pay')
			vary_pay=slp.get('vary_pay')

			earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}'  order by idx""".format(slp.name),as_dict=1,debug=0)
			if earnin:
				for ern in earnin:
					if ern.salary_component in compo:
						fix_pay-=ern.amount
						vary_pay+=ern.amount
						slp.update({'fix_pay':fix_pay})
						slp.update({'vary_pay':vary_pay})
			dt.append(slp)
		data['slip']=dt
	else:
		frappe.throw("please select payroll entry or payroll month")

	return data

import csv
import os
@frappe.whitelist()
def down_report(company,payroll_entry=None,start_date=None,mol=None,employee=None):
	data =''
	dt=[]
	tot=0
	if payroll_entry or start_date:
		filt=''
		if payroll_entry:
			filt+=" and s.payroll_entry='{0}' ".format(payroll_entry)

		if mol:
			filt+=" and e.ministry_of_labor_employer_id='{0}' ".format(mol)

		if start_date:
			filt+=" and MONTH(s.end_date)=MONTH('{0}') and YEAR(s.end_date)=YEAR('{0}')".format(start_date)

		if employee:
			filt+=" and s.employee='{0}' ".format(employee)
		compres=frappe.db.sql(""" select GROUP_CONCAT(rmc.salary_component) as salary_component from `tabSalary Sheet Report Settings` re left join `tabSalary Report Removed Components` rmc on re.name=rmc.parent where re.company='{0}' group by rmc.label order by rmc.display_order """.format(company),as_dict=1,debug=0)
		compo=[]
		if compres:
			for comp in compres:
				cmplist=comp.get("salary_component")
				cmplistar=cmplist.split(",")
				compo+=cmplistar
		
		sqldt =frappe.db.sql(""" 
		select s.name,s.employee,s.employee_name,e.ministry_of_labor_employer_id,e.employee_labor_card_number,e.bank_ac_no,
		e.routing_number,s.net_pay,s.net_pay as fix_pay,0 as vary_pay,s.leave_without_pay,s.payment_days,s.start_date,s.end_date 
		from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee 
		where s.docstatus=1 and s.company='{0}' {1} """.format(company,filt),as_dict=1,debug=0)
		for slp in sqldt:
			fix_pay=slp.get('fix_pay')
			vary_pay=slp.get('vary_pay')
			tot+=float(slp.get('net_pay'))
			earnin=frappe.db.sql(""" select salary_component,amount from `tabSalary Detail` where parentfield='earnings' and parent ='{0}'  order by idx""".format(slp.name),as_dict=1,debug=0)
			if earnin:
				for ern in earnin:
					if ern.salary_component in compo:
						fix_pay-=ern.amount
						vary_pay+=ern.amount
						slp.update({'fix_pay':fix_pay})
						slp.update({'vary_pay':vary_pay})
			dt.append(slp)
		data=dt
	else:
		frappe.throw("please select payroll entry or payroll month")
	 
	csv_content = ''
	for row in data:
		csv_content += f'EDR,{row.employee_labor_card_number},{row.routing_number},{row.bank_ac_no},{row.start_date},{row.end_date},{row.payment_days},{row.fix_pay},{row.vary_pay},{row.leave_without_pay}\n'
	
	empl=frappe.db.sql("""select ba.bank_account_no,b.routing_number 
	from `tabBank Account` ba left join `tabBank` b on b.name=ba.bank 
	where ba.company='{0}' order by is_default desc """.format(company),as_dict=1,debug=0)
	
	emplr_rout=''
	emplr_bacc=''
	if empl:
		emplr_rout=empl[0].routing_number
		emplr_bacc=empl[0].bank_account_no
	date=str(datetime.now().strftime('%Y-%m-%d'))
	time=str(datetime.now().strftime('%H%M'))
	salmth=str(datetime.now().strftime('%m%Y'))
	edrcnt=len(data)
	dfcr=frappe.db.get_default("currency")
	csv_content += f'SCR,{mol},{row.routing_number},{date},{time},{salmth},{edrcnt},{tot},{dfcr},\n'
    # Save the CSV content to a file
	file_path = '/tmp/'+mol+'.csv'  # You can customize the file path
	with open(file_path, 'w', newline='') as csv_file:
		csv_file.write(csv_content)
	return file_path


@frappe.whitelist()
def down_file(file):
    file_name=str(datetime.now().strftime('%y%m%d%H%M%S'))+'.csv'
    with open(file, "rb") as fileobj:
        filedata = fileobj.read()
    frappe.response['content_type'] = 'text/csv'
    frappe.response['content_disposition'] = 'attachment; filename="{0}"'.format(file_name)
    frappe.local.response.filename = file_name
    frappe.local.response.filecontent = filedata
    frappe.local.response.type = "download"


@frappe.whitelist()
def generate_csv(payroll):
    # Example: Query data from a DocType Salary Slip  . payroll_entry  docstatus 1  employee
    #data = frappe.get_all('YourDocType', filters={}, fields=['field1', 'field2'])
	data =frappe.db.sql(""" select s.employee,e.eid_number,s.net_pay from `tabSalary Slip` s left join `tabEmployee` e on e.name=s.employee where s.docstatus=1 and s.payroll_entry='{0}' """.format(payroll),as_dict=1,debug=1)
	# Create a CSV string
	csv_content = 'Name,Eid,Amount\n'
	for row in data:
		csv_content += f'{row.employee},{row.eid_number},{row.net_pay}\n'

    # Save the CSV content to a file
	file_path = '/tmp/output.csv'  # You can customize the file path
	with open(file_path, 'w', newline='') as csv_file:
		csv_file.write(csv_content)
		
	return file_path

@frappe.whitelist()
def download_csv(payroll):
	file_path = generate_csv(payroll)
	#file_name = os.path.basename(file_path)
	file_name=str(datetime.now().strftime('%y%m%d%H%M%S'))+'.csv'
	with open(file_path, "rb") as fileobj:
		filedata = fileobj.read()
	frappe.response['content_type'] = 'text/csv'
	frappe.response['content_disposition'] = 'attachment; filename="{0}"'.format(file_name)
	frappe.local.response.filename = file_name
	frappe.local.response.filecontent = filedata
	frappe.local.response.type = "download"