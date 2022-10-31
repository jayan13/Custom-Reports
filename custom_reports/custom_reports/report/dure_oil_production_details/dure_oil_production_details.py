# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data(conditions,filters)

def get_columns():
	
	columns = [
		{
		"fieldname": "posting_date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},		
		{
		"fieldname": "waste_oil_consumed",
		"fieldtype": "Data",
		"label": "Waste oil consumed",	
		"width": 100
		},
		{
		"fieldname": "waste_water_qty",
		"fieldtype": "Data",
		"label": "Waste water Qty",	
		"width": 100
		},
		{
		"fieldname": "waste_water_per",
		"fieldtype": "Currency",
		"label": "Waste water %",	
		"width": 100
		},
		{
		"fieldname": "lightend_qty",
		"fieldtype": "Data",
		"label": "Lightend Qty",	
		"width": 100
		},
		{
		"fieldname": "lightend_per",
		"fieldtype": "Currency",
		"label": "Lightend %",	
		"width": 100
		},
		{
		"fieldname": "lightlube_qty",
		"fieldtype": "Data",
		"label": "Lightlube Qty",	
		"width": 100
		},
		{
		"fieldname": "lightlube_per",
		"fieldtype": "Currency",
		"label": "Lightlube %",	
		"width": 100
		},
		{
		"fieldname": "asphalt_qty",
		"fieldtype": "Data",
		"label": "Asphalt Qty",	
		"width": 100
		},
		{
		"fieldname": "asphalt_per",
		"fieldtype": "Currency",
		"label": "Asphalt %",	
		"width": 100
		},		
		{
		"fieldname": "total_recovery",
		"fieldtype": "Data",
		"label": "Total Recovery %",	
		"width": 100
		},		
		{
		"fieldname": "lightend_consumption",
		"fieldtype": "Data",
		"label": "Lightend issued to internal consumption",	
		"width": 100
		},		
		{
		"fieldname": "lightlube_pump",
		"fieldtype": "Data",
		"label": "Lightlube issued to Vacuum Pump",	
		"width": 100
		},		
		{
		"fieldname": "asphalt_issued",
		"fieldtype": "Data",
		"label": "Asphalt Issued to VHBO",	
		"width": 100
		},		
		{
		"fieldname": "VHBO_issued",
		"fieldtype": "Data",
		"label": "Asphalt Issued to BM07",	
		"width": 100
		},		
		{
		"fieldname": "lightlube_issued",
		"fieldtype": "Data",
		"label": "PLO issued to BM07",	
		"width": 100
		},
		{
		"fieldname": "VHBO_production",
		"fieldtype": "Data",
		"label": "VHBO",	
		"width": 100
		},
		{
		"fieldname": "hbo",
		"fieldtype": "Data",
		"label": "BM07",	
		"width": 100
		},		
		{
		"fieldname": "lightend_water",
		"fieldtype": "Data",
		"label": "Drained Water from lightend",	
		"width": 100
		}
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	
	endday=frappe.utils.getdate(filters.get("date_to"))
	dfrm=frappe.utils.getdate(filters.get("date_from"))
	cdate=frappe.utils.add_days(dfrm, -1)
	data=[]
	company="Dure Oil Middle East Factory - Sole Proprietorship LLC"
	while cdate < endday:
		cdate=frappe.utils.add_days(cdate, 1)
		manu={}
		manu.update({'posting_date':cdate})
		woref=frappe.db.sql(""" select d.item_code as item_code,sum(d.qty) as qty from `tabStock Entry Detail` d left join
		`tabStock Entry` s on s.name=d.parent left join `tabProcess Order` p on s.process_order=p.name 
		where s.posting_date='{0}' and s.process_order!='' and s.docstatus<2 and p.process_type='Waste Oil Re-refining' 
		and s.stock_entry_type='Manufacture' group by d.item_code ORDER BY FIELD(d.item_code,'WO001','WT1-WATER', 'LLB001','LI0001','AS0001') """.format(cdate),as_dict=1,debug=0)
		if woref:
			wt=1
			recovery=0
			for it in woref:				
				prd=0
				
				if it.item_code=='WO001':
					wt=it.qty				
					manu.update({'waste_oil_consumed':it.qty})
				if it.item_code=='WT1-WATER':
					prd=round((it.qty/wt)*100,2)				
					recovery+=prd
					manu.update({'waste_water_qty':it.qty,'waste_water_per':prd})
				if it.item_code=='LLB001':
					prd=round((it.qty/wt)*100,2)				
					recovery+=prd
					manu.update({'lightlube_qty':it.qty,'lightend_per':prd})
				if it.item_code=='LI0001':
					prd=round((it.qty/wt)*100,2)				
					recovery+=prd
					manu.update({'lightend_qty':it.qty,'lightlube_per':prd})
				if it.item_code=='AS0001':
					prd=round((it.qty/wt)*100,2)				
					recovery+=prd
					manu.update({'asphalt_qty':it.qty,'asphalt_per':prd})
				
			manu.update({'total_recovery':round(recovery)})
		else:
			manu.update({'waste_oil_consumed':0,})
			manu.update({'lightend_qty':0,'lightend_per':0})
			manu.update({'lightlube_qty':0,'lightlube_per':0})
			manu.update({'asphalt_qty':0,'asphalt_per':0})
			manu.update({'waste_water_qty':0,'waste_water_per':0})
			manu.update({'total_recovery':0})		
		#..................................................................
		litnt=frappe.db.sql(""" select d.item_code as item_code,sum(d.qty) as qty,d.expense_account from `tabStock Entry Detail` d left join
		`tabStock Entry` s on s.name=d.parent where s.posting_date='{0}' and d.item_code in ('LI0001','LLB001') and s.docstatus<2 
		and s.stock_entry_type='Material Issue' and 
		d.expense_account in ('501120 - Light Lube Issued to Vacum Pump - DURE','501119 - Lightend Issued to Internal Consumption - DURE') 
		group by d.item_code ORDER BY FIELD(d.item_code,'LI0001','LLB001')""".format(cdate),as_dict=1,debug=0)
		manu.update({'lightend_consumption':0})
		manu.update({'lightlube_pump':0})
		if litnt:
			for li in litnt:
				if li.item_code=='LI0001':
					manu.update({'lightend_consumption':li.qty})
				if li.item_code=='LLB001':
					manu.update({'lightlube_pump':li.qty})
		
		#...................................................................
		woref1=frappe.db.sql(""" select d.item_code as item_code,sum(d.qty) as qty from `tabStock Entry Detail` d left join
		`tabStock Entry` s on s.name=d.parent left join `tabProcess Order` p on s.process_order=p.name 
		where s.posting_date='{0}' and s.process_order!='' and s.docstatus<2 and p.process_type='VHBO Production' 
		and s.stock_entry_type='Manufacture' group by d.item_code ORDER BY FIELD(d.item_code,'AS0001','VHBO101') """.format(cdate),as_dict=1,debug=0)
		manu.update({'asphalt_issued':0})
		manu.update({'VHBO_production':0}) 
		if woref1:
			
			for it in woref1:
				if it.item_code=='AS0001':				
					manu.update({'asphalt_issued':it.qty})
				if it.item_code=='VHBO101':				
					manu.update({'VHBO_production':it.qty})
		
		#...................................................................
		woref2=frappe.db.sql(""" select d.item_code as item_code,sum(d.qty) as qty from `tabStock Entry Detail` d left join
		`tabStock Entry` s on s.name=d.parent left join `tabProcess Order` p on s.process_order=p.name 
		where s.posting_date='{0}' and s.process_order!='' and s.docstatus<2 and p.process_type='HBO Production' 
		and s.stock_entry_type='Manufacture' group by d.item_code ORDER BY FIELD(d.item_code,'VHBO101','LLB001','HBO101') """.format(cdate),as_dict=1,debug=0)
		manu.update({'VHBO_issued':0})
		manu.update({'lightlube_issued':0})
		manu.update({'hbo':0})		
		if woref2:
			
			for it in woref2:
				if it.item_code=='VHBO101':
					manu.update({'VHBO_issued':it.qty})
				if it.item_code=='LLB001':
					manu.update({'lightlube_issued':it.qty})
				if it.item_code=='HBO101':
					manu.update({'hbo':it.qty})
	
		#..................................................................
		litnt=frappe.db.sql(""" select d.item_code as item_code,sum(d.qty) as qty,d.expense_account from `tabStock Entry Detail` d left join
		`tabStock Entry` s on s.name=d.parent where s.posting_date='{0}' and d.item_code in ('LI0001') and s.docstatus<2 
		and s.stock_entry_type='Material Issue' and 
		d.expense_account in ('501614 - Temp-Water Drained Out From Lightened - DURE') 
		group by d.item_code """.format(cdate),as_dict=1,debug=0)
		manu.update({'lightend_water':0})
		if litnt:
			for li in litnt:
				if li.item_code=='LI0001':
					manu.update({'lightend_water':li.qty})
				

		#...................................................................	
		data.append(manu)
	#Dure Oil Middle East Factory - Sole Proprietorship LLC
	#frappe.msgprint(str(data))
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(s.posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(s.posting_date) <= '{0}'".format(date_to)

	return conditions

