# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime,timedelta,time
from frappe.utils import add_to_date,getdate,today,get_datetime
#from frappe.utils.background_jobs import enqueue

def send_mail(doc,event):

    checkincount_inday=frappe.db.sql("""select count(c.name) as ckin  from `tabEmployee Checkin` c 
	where log_type='IN' and c.employee='%s' and DATE(c.time)=DATE('%s') group by DATE(`time`),c.employee"""%(doc.employee,doc.time),as_dict=1,debug=0)[0].ckin or 0

    tm=''    
    if doc.log_type=='IN' and doc.shift and checkincount_inday < 2:
        shifttp=frappe.get_doc("Shift Type",doc.shift)
        tm=shifttp.start_time
        if shifttp.enable_entry_grace_period:
            tm=get_datetime(shifttp.start_time) + timedelta(minutes=shifttp.late_entry_grace_period)
        
        tm=get_datetime(str(tm))

        intime=get_datetime(str(doc.time).split(' ')[1])
        if intime > tm:
            company, attendance_device_id = frappe.db.get_value('Employee', doc.employee, ['company', 'attendance_device_id'])
            if company=='World Wide Emirates Services - Sole Proprietorship LLC':
                receiver='hemy.m@worldwidees.com'
            else:
                receiver='hemy@binbuttigroup.com'

            receiver='jayakumar@alantechnologies.net'
            msg=""" Content: Staff {2}:{3} with employee number {6} has checked in late at {1} .<br><br> 
                    Login Entry : {0}<br> 
                    Login Time : {1}<br> 
                    Employee Code : {2}<br>
                    Employee Name : {3}<br>
                    Shift : {4}<br>
                    Device ID : {5}<br>
                    Emp Code : {6} <br>
                    Company : {7}
                    """.format(doc.name,doc.get_formatted('time'),doc.employee,doc.employee_name,doc.shift,doc.device_id,attendance_device_id,company)

            if receiver:
                email_args = {
                    "recipients": [receiver],
                    "message": msg,
                    "subject": 'late check in notification - {0} - {1}'.format(doc.employee_name, doc.get_formatted('time')),
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name
                    }
                frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
                #frappe.msgprint(" email send ")

