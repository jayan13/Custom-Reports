# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime,timedelta,time
from frappe.utils import add_to_date,getdate,today,get_datetime
#from frappe.utils.background_jobs import enqueue

def send_mail(doc,event):
    tm=''    
    if doc.log_type=='IN' and doc.shift:
        shifttp=frappe.get_doc("Shift Type",doc.shift)
        tm=shifttp.start_time
        if shifttp.enable_entry_grace_period:
            tm=get_datetime(shifttp.start_time) + timedelta(minutes=shifttp.late_entry_grace_period)

        tm=get_datetime(str(tm))

        intime=get_datetime(str(doc.time).split(' ')[1])
        if intime > tm:
            receiver='jayakumar@alantechnologies.net'
            msg=""" Login Entry : {0}\n 
                    Login Time : {1}\n 
                    Employee Code : {2}\n
                    Employee Name : {3}\n
                    Shift : {4}\n
                    Device ID : {5}
                    """.format(doc.name,doc.time,doc.employee,doc.employee_name,doc.shift,doc.device_id)

            if receiver:
                email_args = {
                    "recipients": [receiver],
                    "message": msg,
                    "subject": '{0} - Late Login {1}'.format(doc.employee, doc.time),
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name
                    }
                frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
                frappe.msgprint(" email send ")

