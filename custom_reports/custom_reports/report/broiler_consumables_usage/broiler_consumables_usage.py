# Copyright (c) 2022, alantech and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe import _, msgprint
from erpnext.stock.utils import (get_incoming_rate)
from erpnext.stock.get_item_details import (get_conversion_factor)

def execute(filters=None):
	if not filters:
		filters = {}
	conditions=get_conditions(filters)
	return get_columns(), get_data_n(conditions,filters)

def get_columns():
	
	columns = [
		{
		"fieldname": "posting_date",
		"fieldtype": "Date",
		"label": "Date",
		"width": 100
		},		
		{
		"fieldname": "project",
		"fieldtype": "Link",
		"label": "Project",
		"options": "Project",		
		"width": 300
		},
		{
		"fieldname": "vaccine",
		"fieldtype": "Currency",
		"label": "Vaccine",	
		"width": 100
		},
		{
		"fieldname": "medicine",
		"fieldtype": "Currency",
		"label": "Medicine",	
		"width": 100
		},
		{
		"fieldname": "feed",
		"fieldtype": "Currency",
		"label": "Feed",	
		"width": 100
		},
		{
		"fieldname": "total",
		"fieldtype": "Currency",
		"label": "Total",	
		"width": 100
		}
 	 ]	
	    
	return columns

def get_data(conditions,filters):
	
	data=[]
	conc=frappe.db.sql(""" select GROUP_CONCAT(name) as name,project,posting_date from `tabStock Entry` where stock_entry_type ='Manufacture' 
		and manufacturing_type='Broiler Chicken' and docstatus=1 and %s group by project order by project"""% (conditions),as_dict=1,debug=0)
	for cosu in conc:
		names=cosu.name.replace(",", "','")
		manu={}
		manu.update({'posting_date':cosu.posting_date})
		manu.update({'project':cosu.project})

		vaccine=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabVaccine` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if vaccine:
			vac=vaccine[0].basic_amount
		else:
			vac=0
		manu.update({'vaccine':vac})

		medicine=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabMedicine` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if medicine:
			med=medicine[0].basic_amount
		else:
			med=0

		manu.update({'medicine':med})	
		feed=0
		starter_item=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT starter_item from `tabFeed` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if starter_item:
			starter=starter_item[0].basic_amount
		else:
			starter=0

		finisher_item=frappe.db.sql(""" select sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT finisher_item from `tabFeed` where parent='{1}') group by project""".format(names,cosu.project),as_dict=1,debug=0)
		if finisher_item:
			finisher=finisher_item[0].basic_amount
		else:
			finisher=0

		feed=starter+finisher
		manu.update({'feed':feed})
		total=vac+med+feed
		manu.update({'total':total})
		#...................................................................	
		data.append(manu)
	
	return data

def get_data_n(conditions,filters):
	
	if filters.get("company"):
		company=filters.get("company")
		
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		
	if filters.get("date_to"):
		date_to=filters.get("date_to")

	broiler_batchs=frappe.db.sql(""" select DISTINCT boil.broiler_batch from (select a.name as broiler_batch from `tabBroiler Batch` a left join `tabMedicine`
	 m on a.name=m.parent where m.item is not null and m.item!='' and a.company='{0}' and m.date >= '{1}' and m.date <= '{2}' group by a.name 
	 UNION 
	 select b.name as broiler_batch from `tabBroiler Batch` b left join `tabVaccine` f
	  on b.name=f.parent where f.item is not null and f.item!='' and b.company='{0}' and f.date >= '{1}' and f.date <= '{2}' group by b.name
	 UNION
	select c.name as broiler_batch from `tabBroiler Batch` c left join `tabFeed` g
	 on c.name=g.parent where g.starter_item is not null and g.starter_item!='' and c.company='{0}' and g.date >= '{1}' and g.date <= '{2}' group by c.name
	 UNION
	 select d.name as broiler_batch from `tabBroiler Batch` d left join `tabFeed` h
	  on d.name=h.parent where h.finisher_item is not null and h.finisher_item!='' and d.company='{0}' and h.date >= '{1}' and h.date <= '{2}' group by d.name) boil
	  order by boil.broiler_batch""".format(company,date_from,date_to),as_dict=1,debug=0)
	data=[]
	if broiler_batchs:
		for broilerbatch in broiler_batchs:
			vac=0
			med=0
			starter=0
			finisher=0
			broiler_batch=broilerbatch.broiler_batch
			bro_date=''
			medicines=frappe.db.sql("""select b.name,b.broiler_shed,m.item,m.qty,m.uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabMedicine`
	 			m on b.name=m.parent where m.item is not null and m.item!='' and b.company='{0}' and m.date >= '{1}' and m.date <= '{2}' and b.name='{3}' """.format(company,date_from,date_to,broiler_batch),as_dict=1,debug=0)
			if medicines:
				for medicine in medicines:
					sett = frappe.get_doc('Broiler Shed',medicine.broiler_shed)
					base_row_rate = get_incoming_rate({
								"item_code": medicine.item,
								"warehouse": sett.row_material_target_warehouse,
								"posting_date": medicine.date,
								"posting_time": medicine.itime,
								"qty": -1 * medicine.qty,
								'company':company
							})
					bro_date=medicine.date
					conversion_factor = get_conversion_factor(medicine.item, medicine.uom).get("conversion_factor")
					med+=base_row_rate * float(medicine.qty) * float(conversion_factor)

			vaccines=frappe.db.sql("""select b.name,b.broiler_shed,m.item,m.qty,m.uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabVaccine`
	 			m on b.name=m.parent where m.item is not null and m.item!='' and b.company='{0}' and m.date >= '{1}' and m.date <= '{2}' and b.name='{3}' """.format(company,date_from,date_to,broiler_batch),as_dict=1,debug=0)
			if vaccines:
				for medicine in vaccines:
					sett = frappe.get_doc('Broiler Shed',medicine.broiler_shed)
					base_row_rate = get_incoming_rate({
								"item_code": medicine.item,
								"warehouse": sett.row_material_target_warehouse,
								"posting_date": medicine.date,
								"posting_time": medicine.itime,
								"qty": -1 * medicine.qty,
								'company':company
							})
					bro_date=medicine.date
					conversion_factor = get_conversion_factor(medicine.item, medicine.uom).get("conversion_factor")
					vac+=base_row_rate * float(medicine.qty) * float(conversion_factor)

			starters=frappe.db.sql("""select b.name,b.broiler_shed,m.starter_item,m.starter_qty,m.starter_uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabFeed`
	 			m on b.name=m.parent where m.starter_item is not null and m.starter_item!='' and b.company='{0}' and m.date >= '{1}' and m.date <= '{2}' and b.name='{3}' """.format(company,date_from,date_to,broiler_batch),as_dict=1,debug=0)
			if starters:
				for medicine in starters:
					sett = frappe.get_doc('Broiler Shed',medicine.broiler_shed)
					base_row_rate = get_incoming_rate({
								"item_code": medicine.starter_item,
								"warehouse": sett.row_material_target_warehouse,
								"posting_date": medicine.date,
								"posting_time": medicine.itime,
								"qty": -1 * medicine.starter_qty,
								'company':company
							})
					bro_date=medicine.date
					conversion_factor = get_conversion_factor(medicine.starter_item, medicine.starter_uom).get("conversion_factor")
					starter+=base_row_rate * float(medicine.starter_qty) * float(conversion_factor)

			finishers=frappe.db.sql("""select b.name,b.broiler_shed,m.finisher_item,m.finisher_qty,m.finisher_uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabFeed`
			 	m on b.name=m.parent where m.finisher_item is not null and m.finisher_item!='' and b.company='{0}' and m.date >= '{1}' and m.date <= '{2}' and b.name='{3}' """.format(company,date_from,date_to,broiler_batch),as_dict=1,debug=0)
			if finishers:
				for medicine in finishers:
					sett = frappe.get_doc('Broiler Shed',medicine.broiler_shed)
					base_row_rate = get_incoming_rate({
								"item_code": medicine.finisher_item,
								"warehouse": sett.row_material_target_warehouse,
								"posting_date": medicine.date,
								"posting_time": medicine.itime,
								"qty": -1 * medicine.finisher_qty,
								'company':company
							})
					bro_date=medicine.date
					conversion_factor = get_conversion_factor(medicine.finisher_item, medicine.finisher_uom).get("conversion_factor")
					finisher+=base_row_rate * float(medicine.finisher_qty) * float(conversion_factor)

			manu={}
			manu.update({'posting_date':bro_date})
			manu.update({'project':broiler_batch})
			manu.update({'vaccine':vac})
			manu.update({'medicine':med})
			feed=starter+finisher
			manu.update({'feed':feed})
			total=vac+med+feed
			manu.update({'total':total})
			data.append(manu)
	
	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(posting_date) <= '{0}'".format(date_to)

	return conditions
