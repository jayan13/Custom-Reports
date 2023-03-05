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
	return get_columns_n(), get_data_n(conditions,filters)

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
		"width": 200
		},
		{
		"fieldname": "item",
		"fieldtype": "Data",
		"label": "Item",	
		"width": 200
		},
		{
		"fieldname": "transfer_qty",
		"fieldtype": "Float",
		"label": "Qty",	
		"width": 100
		},
		{
		"fieldname": "stock_uom",
		"fieldtype": "Data",
		"label": "Uom",	
		"width": 100
		},
		{
		"fieldname": "basic_rate",
		"fieldtype": "Currency",
		"label": "Rate",	
		"width": 100
		},
		{
		"fieldname": "basic_amount",
		"fieldtype": "Currency",
		"label": "Amount",	
		"width": 100
		}
 	 ]	
	    
	return columns

def get_columns_n():
	
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
		"width": 200
		},
		{
		"fieldname": "item",
		"fieldtype": "Data",
		"label": "Item",	
		"width": 150
		},		
		{
		"fieldname": "stock_uom",
		"fieldtype": "Data",
		"label": "Stock Uom",	
		"width": 80
		},
		{
		"fieldname": "basic_rate",
		"fieldtype": "Float",
		"label": "Stock Rate",	
		"width": 100
		},
		{
		"fieldname": "conversion_factor",
		"fieldtype": "Data",
		"label": "Convertion Factor",	
		"width": 80
		},
		{
		"fieldname": "transfer_uom",
		"fieldtype": "Data",
		"label": "Uom",	
		"width": 80
		},
		{
		"fieldname": "transfer_qty",
		"fieldtype": "Float",
		"label": "Qty",	
		"width": 80
		},
		
		{
		"fieldname": "transfer_rate",
		"fieldtype": "Float",
		"label": "Rate",	
		"width": 100
		},
		{
		"fieldname": "transfer_amount",
		"fieldtype": "Currency",
		"label": "Amount",	
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

		vaccine=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabVaccine` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in vaccine:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		medicine=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT item from `tabMedicine` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in medicine:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		starter_item=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT starter_item from `tabFeed` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in starter_item:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)

		finisher_item=frappe.db.sql(""" select CONCAT(item_code,' - ',item_name) as item,sum(transfer_qty) as transfer_qty,stock_uom,basic_rate,sum(basic_amount) as basic_amount  from `tabStock Entry Detail` 
		where parent in('{0}') and item_code in(select DISTINCT finisher_item from `tabFeed` where parent='{1}') group by item_code""".format(names,cosu.project),as_dict=1,debug=0)
		for vac in finisher_item:
			manu={}
			manu.update({'posting_date':cosu.posting_date})
			manu.update({'project':cosu.project})
			manu.update({'item':vac.item})
			manu.update({'transfer_qty':vac.transfer_qty})
			manu.update({'stock_uom':vac.stock_uom})
			manu.update({'basic_rate':vac.basic_rate})
			manu.update({'basic_amount':vac.basic_amount})
		
		data.append(manu)
	
	return data

def get_data_n(conditions,filters):
	
	conditions1=' 1=1 '
	conditions2=' 1=1 '
	conditions3=' 1=1 '
	conditions4=' 1=1 '
	companys=''
	broiler_batchs=''
	datefrom=''
	dateto=''

	if filters.get("company"):
		company=filters.get("company")
		conditions1 += " and a.company= '{0}' ".format(company)
		conditions2 += " and b.company= '{0}' ".format(company)
		conditions3 += " and c.company= '{0}' ".format(company)
		conditions4 += " and d.company= '{0}' ".format(company)
		companys=" and b.company='{0}' ".format(company)
		company=filters.get("company")
	if filters.get("project"):
		project=filters.get("project")
		conditions1 += " and a.name= '{0}' ".format(project)
		conditions2 += " and b.name= '{0}' ".format(project)
		conditions3 += " and c.name= '{0}' ".format(project)
		conditions4 += " and d.name= '{0}' ".format(project)
		broiler_batchs=" and b.name='{0}' ".format(project)
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions1 += " and m.date >= '{0}' ".format(date_from)
		conditions2 += " and f.date >= '{0}' ".format(date_from)
		conditions3 += " and g.date >= '{0}' ".format(date_from)
		conditions4 += " and h.date >= '{0}' ".format(date_from)
		datefrom=" and m.date >= '{0}' ".format(date_from)
		date_from=filters.get("date_from")
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions1 += "  and m.date <= '{0}'".format(date_to)
		conditions2 += "  and f.date <= '{0}'".format(date_to)
		conditions3 += "  and g.date <= '{0}'".format(date_to)
		conditions4 += "  and h.date <= '{0}'".format(date_to)
		dateto=" and m.date <= '{0}' ".format(date_to)
		date_to=filters.get("date_to")

	broilerbatchs=frappe.db.sql(""" select DISTINCT boil.broiler_batch,boil.start_date from (select a.name as broiler_batch,a.start_date as start_date from `tabBroiler Batch` a left join `tabMedicine`
	 m on a.name=m.parent where m.item is not null and m.item!='' and {0} group by a.name 
	 UNION 
	 select b.name as broiler_batch,b.start_date as start_date from `tabBroiler Batch` b left join `tabVaccine` f
	  on b.name=f.parent where f.item is not null and f.item!='' and {1} group by b.name
	 UNION
	select c.name as broiler_batch,c.start_date as start_date from `tabBroiler Batch` c left join `tabFeed` g
	 on c.name=g.parent where g.starter_item is not null and g.starter_item!='' and {2} group by c.name
	 UNION
	 select d.name as broiler_batch,d.start_date as start_date from `tabBroiler Batch` d left join `tabFeed` h
	  on d.name=h.parent where h.finisher_item is not null and h.finisher_item!='' and {3} group by d.name) boil
	  order by boil.broiler_batch""".format(conditions1,conditions2,conditions3,conditions4),as_dict=1,debug=0)

	data=[]
	for cosu in broilerbatchs:
		broiler_batch=cosu.broiler_batch
		broiler_date=cosu.start_date

		medicines=frappe.db.sql("""select b.name,b.broiler_shed,m.item,m.item_name,m.qty,m.uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabMedicine`
	 			m on b.name=m.parent where m.item is not null and m.item!='' {0} {1} {2} {3} group by m.item""".format(companys,datefrom,dateto,broiler_batchs),as_dict=1,debug=0)
		if medicines:
			sett = frappe.get_doc('Broiler Shed',medicines[0].broiler_shed)
			for vac in medicines:
				manu={}
				conversion_factor = get_conversion_factor(vac.item, vac.uom).get("conversion_factor")
				base_row_rate = get_incoming_rate({
									"item_code": vac.item,
									"warehouse": sett.row_material_target_warehouse,
									"posting_date": date_to,
									"posting_time": vac.itime,
									"qty": -1 * vac.qty,
									'company':company
								})
				stock_uom = frappe.db.get_value("Item", vac.item, "stock_uom")
				act_rate=float(conversion_factor)*float(base_row_rate)
				act_amount=base_row_rate * float(vac.qty) * float(conversion_factor)
				manu.update({'posting_date':broiler_date})
				manu.update({'project':broiler_batch})
				manu.update({'item':vac.item})
				manu.update({'stock_uom':stock_uom})
				manu.update({'basic_rate':base_row_rate})
				manu.update({'conversion_factor':conversion_factor})

				manu.update({'transfer_uom':vac.uom})
				manu.update({'transfer_qty':vac.qty})
				manu.update({'transfer_rate':act_rate})
				manu.update({'transfer_amount':act_amount})
			data.append(manu)

		vaccines=frappe.db.sql("""select b.name,b.broiler_shed,m.item,m.item_name,m.qty,m.uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabVaccine`
	 			m on b.name=m.parent where m.item is not null and m.item!='' {0} {1} {2} {3} group by m.item""".format(companys,datefrom,dateto,broiler_batchs),as_dict=1,debug=0)
		
		for vac in vaccines:
			if vaccines:
				manu={}
				conversion_factor = get_conversion_factor(vac.item, vac.uom).get("conversion_factor")
				base_row_rate = get_incoming_rate({
									"item_code": vac.item,
									"warehouse": sett.row_material_target_warehouse,
									"posting_date": date_to,
									"posting_time": vac.itime,
									"qty": -1 * vac.qty,
									'company':company
								})
				stock_uom = frappe.db.get_value("Item", vac.item, "stock_uom")
				act_rate=float(conversion_factor)*float(base_row_rate)
				act_amount=base_row_rate * float(vac.qty) * float(conversion_factor)
				manu.update({'posting_date':broiler_date})
				manu.update({'project':broiler_batch})
				manu.update({'item':vac.item})
				manu.update({'stock_uom':stock_uom})
				manu.update({'basic_rate':base_row_rate})
				manu.update({'conversion_factor':conversion_factor})

				manu.update({'transfer_uom':vac.uom})
				manu.update({'transfer_qty':vac.qty})
				manu.update({'transfer_rate':act_rate})
				manu.update({'transfer_amount':act_amount})
			data.append(manu)

		starters=frappe.db.sql("""select b.name,b.broiler_shed,m.starter_item as item,m.starter_qty as qty,m.starter_uom as uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabFeed`
	 			m on b.name=m.parent where m.starter_item is not null and m.starter_item!='' {0} {1} {2} {3} group by m.starter_item""".format(companys,datefrom,dateto,broiler_batchs),as_dict=1,debug=0)

		for vac in starters:
			if starters:
				manu={}
				conversion_factor = get_conversion_factor(vac.item, vac.uom).get("conversion_factor")
				base_row_rate = get_incoming_rate({
									"item_code": vac.item,
									"warehouse": sett.row_material_target_warehouse,
									"posting_date": date_to,
									"posting_time": vac.itime,
									"qty": -1 * vac.qty,
									'company':company
								})
				stock_uom = frappe.db.get_value("Item", vac.item, "stock_uom")
				act_rate=float(conversion_factor)*float(base_row_rate)
				act_amount=base_row_rate * float(vac.qty) * float(conversion_factor)
				manu.update({'posting_date':broiler_date})
				manu.update({'project':broiler_batch})
				manu.update({'item':vac.item})
				manu.update({'stock_uom':stock_uom})
				manu.update({'basic_rate':base_row_rate})
				manu.update({'conversion_factor':conversion_factor})

				manu.update({'transfer_uom':vac.uom})
				manu.update({'transfer_qty':vac.qty})
				manu.update({'transfer_rate':act_rate})
				manu.update({'transfer_amount':act_amount})
			data.append(manu)

		finishers=frappe.db.sql("""select b.name,b.broiler_shed,m.finisher_item as item,m.finisher_qty as qty,m.finisher_uom as uom,m.date,TIME(m.creation) as itime from `tabBroiler Batch` b left join `tabFeed`
			 	m on b.name=m.parent where m.finisher_item is not null and m.finisher_item!='' {0} {1} {2} {3} group by m.finisher_item""".format(companys,datefrom,dateto,broiler_batchs),as_dict=1,debug=0)

		for vac in finishers:
			if finishers:
				manu={}
				conversion_factor = get_conversion_factor(vac.item, vac.uom).get("conversion_factor")
				base_row_rate = get_incoming_rate({
									"item_code": vac.item,
									"warehouse": sett.row_material_target_warehouse,
									"posting_date": date_to,
									"posting_time": vac.itime,
									"qty": -1 * vac.qty,
									'company':company
								})
				stock_uom = frappe.db.get_value("Item", vac.item, "stock_uom")
				act_rate=float(conversion_factor)*float(base_row_rate)
				act_amount=base_row_rate * float(vac.qty) * float(conversion_factor)
				manu.update({'posting_date':broiler_date})
				manu.update({'project':broiler_batch})
				manu.update({'item':vac.item})
				manu.update({'stock_uom':stock_uom})
				manu.update({'basic_rate':base_row_rate})
				manu.update({'conversion_factor':conversion_factor})

				manu.update({'transfer_uom':vac.uom})
				manu.update({'transfer_qty':vac.qty})
				manu.update({'transfer_rate':act_rate})
				manu.update({'transfer_amount':act_amount})
			data.append(manu)
		

	return data

def get_conditions(filters):
	
	conditions =" 1=1 "
	if filters.get("company"):
		company=filters.get("company")
		conditions += " and company= '{0}' ".format(company)
	if filters.get("project"):
		project=filters.get("project")
		conditions += " and project= '{0}' ".format(project)
	if filters.get("date_from"):
		date_from=filters.get("date_from")
		conditions += " and DATE(posting_date) >= '{0}' ".format(date_from)
	if filters.get("date_to"):
		date_to=filters.get("date_to")
		conditions += "  and DATE(posting_date) <= '{0}'".format(date_to)

	return conditions

