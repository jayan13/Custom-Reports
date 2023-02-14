# Copyright (c) 2023, alantech and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, cstr, nowdate, comma_and, cint, getdate,add_days,date_diff,formatdate,format_date
from frappe import throw, msgprint, _
from frappe.model.document import Document


class ShiftRoster(Document):
	def on_update(self):
		frappe.db.delete("Employee Shift Roster", {"shift_roster": self.name})
		import json
		aList = json.loads(self.employee_list_data)
		for lst in aList:
			
			doc = frappe.get_doc({
    				'doctype': 'Employee Shift Roster',
    				'shift_roster': self.name,
					'employee':lst.get('employee'),
					'shift_type':lst.get('shift_type'),
					'day':lst.get('day'),
					'day_type':lst.get('day_type')
					})
			doc.insert()

		self.update_shift()

	def after_insert(self):
		import json
		aList = json.loads(self.employee_list_data)
		for lst in aList:
			
			doc = frappe.get_doc({
    				'doctype': 'Employee Shift Roster',
    				'shift_roster': self.name,
					'employee':lst.get('employee'),
					'shift_type':lst.get('shift_type'),
					'day':lst.get('day'),
					'day_type':lst.get('day_type')
					})
			doc.insert()

		self.update_shift()
			
	def on_submit(self):
		import json
		aList = json.loads(self.employee_list_data)
		for lst in aList:
			
			doc = frappe.get_doc({
    				'doctype': 'Employee Shift Roster',
    				'shift_roster': self.name,
					'employee':lst.get('employee'),
					'shift_type':lst.get('shift_type'),
					'day':lst.get('day'),
					'day_type':lst.get('day_type')
					})
			doc.insert()

	def on_cancel(self):
		frappe.db.delete("Employee Shift Roster", {"shift_roster": self.name})
		att=frappe.db.get_all('Attendance',filters={'shift_roster':self.name},fields=['name'])
		if att:
			for at in att:
				doc = frappe.get_doc('Attendance', at.name)
				doc.cancel()
		
		comp=frappe.db.get_all('Compensatory Leave Request',filters={'shift_roster':self.name},fields=['name'])
		if comp:
			for at in comp:
				doc = frappe.get_doc('Compensatory Leave Request', at.name)
				doc.cancel()
		shift=frappe.db.get_all('Shift Assignment',filters={'shift_roster':self.name},fields=['name'])
		if shift:
			for at in shift:
				doc = frappe.get_doc('Shift Assignment', at.name)
				doc.cancel()

	def on_trash(self):
		frappe.db.delete("Employee Shift Roster", {"shift_roster": self.name})

		att=frappe.db.get_all('Attendance',filters={'shift_roster':self.name},fields=['name'])
		if att:
			for at in att:
				doc = frappe.get_doc('Attendance', at.name)
				doc.cancel()
		
		comp=frappe.db.get_all('Compensatory Leave Request',filters={'shift_roster':self.name},fields=['name'])
		if comp:
			for at in comp:
				doc = frappe.get_doc('Compensatory Leave Request', at.name)
				doc.cancel()
		shift=frappe.db.get_all('Shift Assignment',filters={'shift_roster':self.name},fields=['name'])
		if shift:
			for at in shift:
				doc = frappe.get_doc('Shift Assignment', at.name)
				doc.cancel()
		
		

	def update_shift(self):
		
		emps=frappe.db.get_all('Employee',filters={'department':self.department},fields=['name','company','department','default_shift'])
		if emps:
			shiftay=[]
			for emp in emps:
				ros_days=frappe.db.get_all('Employee Shift Roster',filters={'shift_roster':self.name,'employee':emp.name},fields=['shift_roster','employee','shift_type','day','day_type'],order_by='day')
				if ros_days:				
					shfts={}
					shift=''
					i=1
					shift_strt=''
					rowcount=len(ros_days)
							
					for rd in ros_days:						
						if shift!=rd.shift_type:
							if i==1:
								shift_strt=rd.day
								shfts.update({'start_date':shift_strt})
								shfts.update({'shift_type':rd.shift_type})
								shfts.update({'employee':rd.employee})
								shfts.update({'default_shift':emp.default_shift})
								shfts.update({'shift_roster':rd.shift_roster})
								
							else:
								shift_end=add_days(getdate(rd.day),-1)							
								shfts.update({'end_date':shift_end})
								shiftay.append(shfts)
								shfts={}
								shift_strt=rd.day
														
								shfts.update({'start_date':shift_strt})
								shfts.update({'shift_type':rd.shift_type})
								shfts.update({'employee':rd.employee})
								shfts.update({'default_shift':emp.default_shift})
								shfts.update({'shift_roster':rd.shift_roster})

							shift=rd.shift_type	

						if rowcount==i:							
							shift_end=getdate(rd.day)
							shfts.update({'end_date':shift_end})
							shiftay.append(shfts)

						i+=1

			if shiftay:
				
				for shf in shiftay:					
					employee=shf.get('employee')
					default_shift=shf.get('default_shift')
					shift_type=shf.get('shift_type')
					start_date=shf.get('start_date')
					end_date=shf.get('end_date')
					shift_roster=shf.get('shift_roster')
					if default_shift!=shift_type:
						
						shfass=frappe.db.sql(""" SELECT name from `tabShift Assignment` where docstatus=1 and status='Active' and employee='{0}' and (('{1}' between start_date and end_date) or ('{2}' between start_date and end_date)) """.format(employee,start_date,end_date), as_dict=1,debug=0)
						if shfass:
							for shf in shfass:
								doc = frappe.get_doc('Shift Assignment',shf.name)
								doc.status='Inactive'
								doc.save()
								
						#if not shfass:
						empy=frappe.db.get_value('Employee',{'name':employee},['department','company'],as_dict=1,debug=1)
						
						doc = frappe.get_doc({
    						'doctype': 'Shift Assignment',
    						'start_date': getdate(start_date),
							'end_date':getdate(end_date),
							'shift_type':shift_type,
							'employee':employee,
							'status':'Active',
							'department':empy.department,
							'company':empy.company,
							'shift_roster':shift_roster,
							})
						doc.insert()
						doc.submit()

		

@frappe.whitelist()
def mark_attendance(shift_roster):
	ros_days=frappe.db.get_all('Employee Shift Roster',filters={'shift_roster':shift_roster},fields=['shift_roster','employee','shift_type','day','day_type'],order_by='day')
	
	if ros_days:
		for rsday in ros_days:
			date_of_joining=frappe.db.get_value('Employee',{'name':rsday.employee},['date_of_joining'])
			if getdate(rsday.day) < getdate(date_of_joining):
				continue
			
			if rsday.day_type in ['OW','UL','A','P','SL','RO','CO.L','AL']:
				attendance=frappe.db.get_value('Attendance',{'employee':rsday.employee,'attendance_date':rsday.day,'docstatus':'1'},['name','status'],as_dict=1)
				if attendance:
					if attendance.status=='On Leave' and rsday.day_type in ['SL','RO','CO.L','AL']:
						continue
					else:
						doc = frappe.get_doc('Attendance', attendance.name)
						doc.cancel()
						 

			emp=frappe.db.get_value('Employee',{'name':rsday.employee},['department','company'],as_dict=1)
			#Attendance shift attendance_date status leave_type description employee company shift_roster department				
			if rsday.day_type=='OW':
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'Present',
							'description':'Offday working',
							'department':emp.department,
							'company':emp.company,
							'shift':rsday.shift_type,
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()

				comp=frappe.db.get_value('Compensatory Leave Request',{'employee':rsday.employee,'work_from_date':rsday.day,'work_end_date':rsday.day},'name')
				if not comp:
					doc = frappe.get_doc({
    						'doctype': 'Compensatory Leave Request',
    						'leave_type': 'Compensatory Off',
							'work_from_date':rsday.day,
							'work_end_date':rsday.day,
							'employee':rsday.employee,
							'reason':'Off day or holiday Working',
							'shift_roster':rsday.shift_roster,
							})
					doc.insert()
					doc.submit()

			if rsday.day_type=='P':				
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'Present',
							'department':emp.department,
							'company':emp.company,
							'shift':rsday.shift_type,
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()

			if rsday.day_type=='AL':				
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'On Leave',
							'leave_type':'Annual Leave',
							'description':'Annual Leave',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()
			
			if rsday.day_type=='UL':				
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'On Leave',
							'leave_type':'Leave Without Pay',
							'description':'Unpaid Leave',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()

			if rsday.day_type=='A':								
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'Absent',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()
			if rsday.day_type=='SL':				
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'On Leave',
							'leave_type':'Sick Leave',
							'description':'Sick Leave',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()
			if rsday.day_type=='RO':				
				doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'On Leave',
							'leave_type':'Compensatory Off',
							'description':'Compensatory Off',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
				doc.insert()
				doc.submit()
			if rsday.day_type=='CO.L':
				comp=frappe.db.get_value('Compensatory Leave Request',{'employee':rsday.employee,'work_from_date':rsday.day,'work_end_date':rsday.day},'name')
				if comp:
					doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'On Leave',
							'leave_type':'Compassionate leave',
							'description':'Compassionate leave',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
					doc.insert()
					doc.submit()
				else:				
					doc = frappe.get_doc({
    						'doctype': 'Attendance',    												
							'attendance_date':rsday.day,
							'employee':rsday.employee,
							'status':'Absent',
							'department':emp.department,
							'company':emp.company,						
							'shift_roster':rsday.shift_roster,
							})
					doc.insert()
					doc.submit()
		frappe.db.commit()
	frappe.db.set_value('Shift Roster',shift_roster,'attendance_marked',1)
	return "marked"		


@frappe.whitelist()
def employee_list(department,date_from,date_to):
	dt_from=date_from
	dt_to=date_to
	emp=frappe.db.get_all('Employee',filters={'department': department},fields=['name','employee_name','default_shift','weekly_off','weekly_off_2','holiday_list'],order_by='name')
	html='Employee Not Found'
	head=''
	body=''		
	wekkday=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
	
	daytype=['OW','AL','UL','CO.L','RO','P','A','PH','O','SL','BT']
	dayname=['Offday working','Annual Leave','Unpaid Leave','Compassionate Leave','Replacement Off Day','Present','Absant','Public Holiday','Day Off','Sick Leave','Business Trip']
	shift=frappe.db.get_all('Shift Type',fields=['name','start_time','end_time']) #start_time end_time txt.split(", ") 
	shifts=[]
	for shif in shift:
		label=''
		name=shif.name
		if '(' in str(shif.name):
			name=name.split("(")[0]
		start_time=str(shif.start_time).split(':')
		end_time=str(shif.end_time).split(':')
		label=name+' ('+str(start_time[0])+':'+str(start_time[1])+'-'+str(end_time[0])+':'+str(end_time[1])+')'
		shifts.append({'name':shif.name,'label':label})
	#frappe.msgprint(str(shifts))
	user_def_shift=''
	holi_days={}
	dayarray=[]
	if emp:
		com_holyday=frappe.db.get_value('Company',emp[0].company,'default_holiday_list')
		head+='<tr>'
		head+='<th style="width: 200px;border: 1px solid #d3c2c2;padding: 2px;text-align: center;position: sticky;top: 0;left: 0;  z-index: 2;background: white;">Name</th>'
		head+='<th style="width: 90px;border: 1px solid #d3c2c2;padding: 2px;text-align: center;position: sticky;top: 0;  z-index: 1;background: white;">Employee</th>'		
		head+='<th style="width: 100px;border: 1px solid #d3c2c2;padding: 2px;text-align: center;position: sticky;top: 0;  z-index: 1;background: white;">Default Shift <br> Weekly Off</th>'
		date_from=add_days(getdate(date_from),-1)
		daycount=date_diff(getdate(date_to),getdate(date_from))
		
		for x in range(daycount):
			
			date_from=add_days(getdate(date_from),1)
			dayarray.append(str(date_from))
			d=add_days(getdate(date_from),1).weekday()			
			head+='<th style="width: 90px;border: 1px solid #d3c2c2;padding: 2px;text-align: center;position: sticky;top: 0;  z-index: 1;background: white;"><input type="hidden" name="dat[]" value="'+str(date_from)+'" class="dat"/>'+str(formatdate(date_from))+'<br>'+str(wekkday[d])+'</th>'
		head+='</tr>'
		
		for em in emp:
			daylist=''
			holy_day=em.holiday_list or com_holyday
			if em.default_shift:
				user_def_shift=em.default_shift
			empshift=employee_shift(em.name,date_from,date_to,user_def_shift)
			
			if empshift:
				hay=get_holyday(empshift)
				if hay:
					holy_day=hay

			if holy_day:
				if holi_days.get(holy_day):	
					daylist=holi_days.get(holy_day)

				else:
					daylist=get_holydays(holy_day)
					holi_days.update({holy_day:daylist})
					
			
			#if daylist:
			#	frappe.msgprint(str(daylist))

			rostdays=get_roster_days(em.name,dt_from,dt_to)
			#frappe.msgprint(str(rostdays))
			body+='<tr>'
			body+='<td style="width: 200px;border: 1px solid #d3c2c2;padding:4px;position: sticky;  left: 0;  background: white;  z-index: 1;">'+str(em.employee_name)+'</td>'
			body+='<td style="width: 90px;border: 1px solid #d3c2c2;padding:4px;"><input type="text" style="width:120px;" name="employee[]" value="'+str(em.name)+'"  class="emp" /></td>'
			body+='<td style="width: 90px;border: 1px solid #d3c2c2;padding:4px;">'+str(em.default_shift)+'<br>'+str(em.weekly_off)+','+str(em.weekly_off_2)+'</td>'
			for x in range(daycount):
				#dayarray[x]
				body+='<td style="width: 90px;border: 1px solid #d3c2c2;padding:4px;">'
				d=add_days(getdate(dayarray[x]),1).weekday()
				cwday=str(wekkday[d])
				rosshift=empshift
				rosdays='P'
				weekf=''
				if(daylist):
					for dayl in daylist:
						if dayarray[x] in dayl.values():
							if dayl.weekly_off:
								rosdays='O'
							else:
								rosdays='PH'
				if cwday==em.weekly_off_2 or cwday==em.weekly_off:
					rosdays='O'
				if rosdays=='O':
					weekf=' style="background-color: #f5ebeb;" '
				if rostdays:
					for rst in rostdays:
						if dayarray[x] in rst.values():
							rosshift=rst.shift_type
							rosdays=rst.day_type


				attant=frappe.db.sql(""" select status,leave_type from `tabAttendance` where docstatus=1 and 
					attendance_date='{0}' and status in ('On Leave','Absent') and employee='{1}' order by creation desc""".format(dayarray[x],em.name), as_dict=1,debug=0)
				if attant:
					if attant[0].status=='On Leave':
						if attant[0].leave_type=='Compassionate leave':
							rosdays='CO.L'
							rosshift='OFF'
						if attant[0].leave_type=='Compensatory Off':
							rosdays='RO'
							rosshift='OFF'
						if attant[0].leave_type=='Annual Leave':
							rosdays='AL'
							rosshift='OFF'
						if attant[0].leave_type=='Sick Leave':
							rosdays='SL'
							rosshift='OFF'
						if attant[0].leave_type=='Leave Without Pay':
							rosdays='UL'
							rosshift='OFF'
						
					elif(attant[0].status=='Absent'):
						rosdays='A'
					elif(attant[0].status=='Present'):
						rosdays='P'

				ids=str(em.name)+'_'+str(dayarray[x])
				body+='<select name="shift[]" id="'+ids+'_s" class="chkcng" style="margin-bottom:6px;"><option value=""></option>'
				for sh in shifts:
					ssel=''
					if rosshift==str(sh.get('name')):
						ssel=' selected'
					body+='<option value="'+str(sh.get('name'))+'" '+ssel+'>'+str(sh.get('label'))+'</option>'

				body+='</select><br>'

				body+='<select name="daytype[]" class="chkcng" id="'+ids+'_d" '+weekf+' >'
				body+='<option value=""></option>'
				if rosdays and rosdays not in daytype:
						body+='<option value="'+rosdays+'"selected >'+rosdays+'</option>'
				for dy in range(11):
					sseld=''
					if daytype[dy]==str(rosdays):
						sseld=' selected'
					body+='<option value="'+str(daytype[dy])+'" '+sseld+'>'+str(dayname[dy])+'</option>'

				body+='</select></td>'

			body+='</tr>'
	html='<div style="overflow: scroll;max-height:500px;"><table style="width: max-content;table-layout: fixed;">'+head+body+'</table></div>'
	return html

def employee_shift(emp,date_from,date_to,def_holy=''):
	ushift=def_holy
	shift = frappe.db.sql(""" SELECT shift_type from `tabShift Assignment` where employee='{0}' and status='Active' and (('{1}' between start_date and end_date) or ('{2}' between start_date and end_date)) """.format(emp,date_from,date_to), as_dict=1,debug=0)
	if shift:
		ushift=shift[0].shift_type
	return ushift

def get_holyday(shift):
	holiday_list=frappe.db.get_value('Shift Type', {'name':shift}, ['holiday_list'])
	return holiday_list

def get_holydays(holy_day):
	#dy={}
	hlist=frappe.db.get_all('Holiday',filters={'parent': holy_day},fields=['name','holiday_date','description','weekly_off'])
	if len(hlist):
		for hl in hlist:
			hl.holiday_date=str(hl.holiday_date)
		#	dy.update({str(hl.holiday_date):hl.description})
		#return dy
		return hlist
	return
def get_roster_days(emp,date_from,date_to):

	ros=frappe.db.sql(""" SELECT day,day_type,shift_type from `tabEmployee Shift Roster`  where employee='{0}' and day between '{1}' and '{2}' """.format(emp,date_from,date_to), as_dict=1,debug=0)
	if ros:
		for rs in ros:
			rs.day=str(rs.day)
		return ros
	return
