# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	max_chk=frappe.db.sql(""" select max(cin.ckin) as checkincnt from (select count(c.name) as ckin  
	from `tabEmployee Checkin` c left join `tabEmployee` e on e.name=c.employee
	where %s group by DATE(`time`),c.employee) cin """% conditions,as_dict=1,debug=0)[0]
	import math
	cnt=1
	msgprint(str(max_chk))
	if max_chk.checkincnt:
		if max_chk.checkincnt > 2:
			cnt=math.ceil(max_chk.checkincnt/2)
	
	return get_columns(cnt), get_data(cnt,conditions)

def get_columns(cnt):
	
	columns = [
		{
		"fieldname": "date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},
		{
		"fieldname": "employee",
		"fieldtype": "Link",
		"label": "Employee",
		"options": "Employee",
		"width": 100
		},
		{
		"fieldname": "employee_name",
		"fieldtype": "Data",
		"label": "Employee Name",	
		"width": 200
		},
		{
		"fieldname": "shift",
		"fieldtype": "Link",
		"label": "Shift",
		"options": "Shift Type",	
		"width": 100
		},
		{
		"fieldname": "device_id",
		"fieldtype": "Data",
		"label": "Device ID",	
		"width": 100
		},
 	 ]	
	#columns = [_("Date") + ":Date:100",_("Employee") + ":Link/Employee:120", _("Employee Name") + ":Data:150", _("Shift") + ":Link/Shift Type:100", _("Device ID") + ":Data:100",]
	
	for ct in range(cnt):
		cc=ct+1		
		columns.append({
		"fieldname": "in"+str(ct),
		"fieldtype": "Data",
		"label": "IN-"+str(cc),	
		"width": 100
		})
		columns.append({
		"fieldname": "out"+str(ct),
		"fieldtype": "Data",
		"label": "OUT-"+str(cc),	
		"width": 100
		})
		
	#msgprint(str(columns))
	return columns

def get_data(cnt,conditions):
	sql=" "
	for ct in range(cnt):		
		strt=ct
		sql += ",(select TIME_FORMAT(TIME(`time`), '%H:%i:%s') from `tabEmployee Checkin` where log_type='IN' and employee=c.employee and DATE(`time`)=DATE(c.`time`) order by `time` limit {0},1 ) as in{0},(select TIME_FORMAT(TIME(`time`), '%H:%i:%s') from `tabEmployee Checkin` where log_type='OUT' and employee=c.employee and DATE(`time`)=DATE(c.`time`) order by `time` limit {0},1) as out{0}".format(strt)

	data=frappe.db.sql(""" select DATE(c.time) as `date`,c.employee,c.employee_name,c.shift,c.device_id%s  
	from `tabEmployee Checkin` c left join `tabEmployee` e on e.name=c.employee
	where %s group by DATE(c.`time`),c.employee """% (sql,conditions),as_dict=1,debug=0)
	#msgprint(str(data))
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(c.time) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(c.time) <= '{0}'".format(date_to)

	if filters.get("employee"):
		employee=filters.get("employee")
		conditions += " and c.employee = '{0}'".format(employee)

	if filters.get("company"):
		company=filters.get("company")
		conditions += " and e.company = '{0}'".format(company)

	return conditions