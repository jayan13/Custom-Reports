# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import cint, cstr, flt, getdate

from erpnext.setup.utils import get_exchange_rate
from erpnext.stock.doctype.item.item import get_last_purchase_details

@frappe.whitelist()
def quotation_comparison(purchase_order):
	company=frappe.db.get_value("Purchase Order",purchase_order,'company')
	tems=frappe.db.get_all('Purchase Order Item',filters={'parent': purchase_order},fields=['item_code','uom','item_name','last_purchase_rate','qty','material_request','supplier_quotation','company_total_stock'],debug=0)
	itemar=[]
	matreq=''
	suppqto=''
	for pitem in tems:
		itemar.append(pitem.item_code)
		matreq=pitem.material_request
		suppqto=pitem.supplier_quotation

	request_for_quotation=frappe.db.get_value('Supplier Quotation Item', {'parent':suppqto}, ['request_for_quotation'])
	supplier_quotation_data = get_data_html(request_for_quotation,itemar,tems,suppqto,company,purchase_order)
	#data= prepare_data(supplier_quotation_data)
	return supplier_quotation_data

@frappe.whitelist()
def quotation_comparison_mt(material_request):
	company=frappe.db.get_value("Material Request",material_request,'company')
	tems=frappe.db.get_all('Supplier Quotation Item',filters={'material_request': material_request},fields=['item_code','uom','item_name','qty','material_request','parent'],group_by='item_code',debug=0)
	itemar=[]
	suppqto=[]
	qto=frappe.db.sql(""" select DISTINCT parent as quotation from `tabSupplier Quotation Item` where material_request='{0}' """.format(material_request),as_dict=1,debug=0)
	for qt in qto:
		suppqto.append(qt.quotation)

	request_for_quotation=''
	for pitem in tems:
		itemar.append(pitem.item_code)
		request_for_quotation=pitem.request_for_quotation

	supplier_quotation_data = get_data(request_for_quotation,itemar,tems,suppqto,company)
	#data= prepare_data(supplier_quotation_data)
	return supplier_quotation_data

@frappe.whitelist()
def getorderdetails(payment):
	ref=frappe.db.get_all('Payment Entry Reference',filters={'parent': payment,'reference_doctype':['in',['Purchase Invoice','Purchase Order']]},fields=['reference_name','reference_doctype'],debug=0)
	data=''
	
	if ref:
		data=[]
		
		for refe in ref:
			if refe.reference_doctype=='Purchase Invoice':			
				purchase_orders=frappe.db.sql(""" select DISTINCT purchase_order from `tabPurchase Invoice Item` where parent='{0}' """.format(refe.reference_name),as_dict=1,debug=0)
				for purchase_order in purchase_orders:
					name=''
					user=''
					status=''
					amount =frappe.db.get_value('Purchase Order', purchase_order.purchase_order, 'total')	
					workflow=frappe.db.sql(""" select content,modified_by from `tabComment` where reference_doctype='Purchase Order' and comment_type='Workflow' and reference_name='{0}' order by creation desc limit 0,1""".format(purchase_order.purchase_order),as_dict=1,debug=0)
					if workflow:
						user,name=frappe.db.get_value('User', {'user':workflow[0].modified_by}, ['name','full_name'])
						status=workflow[0].content
						data=status
					data.append({'order':purchase_order.purchase_order,'name':name,'user_name':user,'status':status,'amount':amount})
			else:
				name=''
				user=''
				status=''
				amount =frappe.db.get_value('Purchase Order', refe.reference_name, 'total')	
				workflow=frappe.db.sql(""" select content,modified_by from `tabComment` where reference_doctype='Purchase Order' and comment_type='Workflow' and reference_name='{0}' order by creation desc limit 0,1""".format(refe.reference_name),as_dict=1,debug=0)
				if workflow:
					user,name=frappe.db.get_value('User', {'user':workflow[0].modified_by}, ['name','full_name'])
					status=workflow[0].content
					data=status
				data.append({'order':refe.reference_name,'name':name,'user_name':user,'status':status,'amount':amount})

	return data



def get_data(request_for_quotation,itemar,tems,suppqto,company):
	itemssql="','".join(itemar)
	qtosql="','".join(suppqto)
	spli=[]
	if request_for_quotation:
		

		supplier_list = frappe.db.sql(
			"""
			SELECT			
				DISTINCT sq.supplier as supplier_name,sq.name as quotation,sq.company,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes,sum(sqi.net_amount) as total
			FROM
				`tabSupplier Quotation Item` sqi,
				`tabSupplier Quotation` sq
			WHERE
				sqi.parent = sq.name
				AND sq.docstatus < 2
				AND sqi.request_for_quotation='{0}'
				AND sqi.item_code in('{1}')
				AND sq.status<>'Expired'				
				group by sq.supplier order by sq.supplier""".format(
				request_for_quotation,itemssql
			),
			as_dict=1,debug=0
			)
	else:
		supplier_list = frappe.db.sql(
			"""
			SELECT			
				DISTINCT sq.supplier as supplier_name,sq.name as quotation,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes,sum(sqi.net_amount) as total
			FROM
				`tabSupplier Quotation Item` sqi,
				`tabSupplier Quotation` sq
			WHERE
				sqi.parent = sq.name
				AND sq.docstatus < 2
				AND sq.name in('{0}')
				AND sqi.item_code in('{1}')
				AND sq.status<>'Expired'
				group by sq.supplier order by sq.supplier""".format(
				qtosql,itemssql
			),
			as_dict=1,debug=0
			)
	

	dta=[]
	for pitem in tems:
		dati={}

		last_purchase_details = get_last_purchase_details(pitem.item_code)
		lastpur=0
		if last_purchase_details:
			lastpur = last_purchase_details["base_net_rate"]

		company_total_stock=0
		ac_qty=frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}' 
		and warehouse in (select name from `tabWarehouse` where company='{1}') group by item_code""".format(pitem.item_code,company),as_dict=1,debug=0)
		if ac_qty:
			company_total_stock=ac_qty[0].actual_qty if ac_qty[0].actual_qty > 0 else 0
		orditmcnt=getitemordercount(pitem.item_code)	
		dati.update({'item_code':pitem.item_code+'-'+pitem.item_name,'uom':pitem.uom,'qty':pitem.qty,'last_purchase_rate':lastpur,'company_total_stock':company_total_stock,'orditmcnt':orditmcnt})
		spi=[]
		for s in supplier_list:
			#spli.append(s.supplier_name)
			
			if request_for_quotation:
				supplier_quotation_item = frappe.db.sql(
				"""
				SELECT			
					sqi.rate, sq.supplier as supplier_name,sqi.net_amount,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes
				FROM
					`tabSupplier Quotation Item` sqi,
					`tabSupplier Quotation` sq
				WHERE
					sqi.parent = sq.name
					AND sq.docstatus < 2
					AND sqi.item_code ='{0}'
					AND sqi.request_for_quotation='{1}'
					AND sq.supplier='{2}'
					AND sq.status<>'Expired'
					order by sq.supplier limit 0,1""".format(
					pitem.item_code,request_for_quotation,s.supplier_name
				),
				as_dict=1,debug=0
				)
			else:
				supplier_quotation_item = frappe.db.sql(
				"""
				SELECT			
					sqi.rate, sq.supplier as supplier_name,sqi.net_amount,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes,sq.total
				FROM
					`tabSupplier Quotation Item` sqi,
					`tabSupplier Quotation` sq
				WHERE
					sqi.parent = sq.name
					AND sq.docstatus < 2
					AND sqi.item_code ='{0}'
					AND sq.name='{1}'
					AND sq.supplier='{2}'
					AND sq.status<>'Expired'
					order by sq.supplier limit 0,1""".format(
					pitem.item_code,s.quotation,s.supplier_name
				),
				as_dict=1,debug=0
				)

			if supplier_quotation_item:
				for si in supplier_quotation_item:
					#amt=pitem.qty*si.rate
					amt=si.net_amount					
					sp={}
					sp.update({'rate':si.rate,'amount':amt,'supplier':s.supplier_name})
					spi.append(sp)
			else:			
					sp={}
					sp.update({'rate':0,'amount':0,'supplier':s.supplier_name})
					spi.append(sp)
			
		dati.update({'sup':spi})
		dta.append(dati)

	#frappe.msgprint(str(dta))
	data={'items':dta,'suplier':supplier_list}
	return data


def get_data_html(request_for_quotation,itemar,tems,suppqto,company,purchase_order):
	itemssql="','".join(itemar)
	spli=[]
	if request_for_quotation:
		
		supplier_list = frappe.db.sql(
			"""
			SELECT			
				DISTINCT sq.supplier as supplier_name,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes,sum(sqi.net_amount) as total
			FROM
				`tabSupplier Quotation Item` sqi,
				`tabSupplier Quotation` sq
			WHERE
				sqi.parent = sq.name
				AND sq.docstatus < 2
				AND sqi.request_for_quotation='{0}'
				AND sqi.item_code in('{1}')
				AND sq.status<>'Expired'
				group by sq.supplier order by sq.supplier """.format(
				request_for_quotation,itemssql
			),
			as_dict=1,debug=0
			)
	else:
		supplier_list = frappe.db.sql(
			"""
			SELECT			
				DISTINCT sq.supplier as supplier_name,sq.discount_amount,sq.warranty,sq.payment_terms,sq.other_notes,sum(sqi.net_amount) as total
			FROM
				`tabSupplier Quotation Item` sqi,
				`tabSupplier Quotation` sq
			WHERE
				sqi.parent = sq.name
				AND sq.docstatus < 2
				AND sq.name='{0}'
				AND sq.status<>'Expired'
				AND sqi.item_code in('{1}')
				group by sq.supplier order by sq.supplier """.format(
				suppqto,itemssql
			),
			as_dict=1,debug=0
			)
	
	dta=[]
	for pitem in tems:
		dati={}

		company_total_stock=0
		ac_qty=frappe.db.sql(""" select sum(actual_qty) as actual_qty from `tabBin` where item_code='{0}' 
		and warehouse in (select name from `tabWarehouse` where company='{1}') group by item_code""".format(pitem.item_code,company),as_dict=1,debug=0)
		if ac_qty:
			company_total_stock=ac_qty[0].actual_qty if ac_qty[0].actual_qty > 0 else 0
		orditmcnt=getitemordercount(pitem.item_code,purchase_order)
		dati.update({'item_code':pitem.item_code+'-'+pitem.item_name,'uom':pitem.uom,'qty':pitem.qty,'last_purchase_rate':pitem.last_purchase_rate,'company_total_stock':company_total_stock,'orditmcnt':orditmcnt})
		spi=[]
		for s in supplier_list:
			#spli.append(s.supplier_name)
			
			if request_for_quotation:
				
				supplier_quotation_item = frappe.db.sql(
				"""
				SELECT			
					sqi.rate, sq.supplier as supplier_name,sqi.net_amount
				FROM
					`tabSupplier Quotation Item` sqi,
					`tabSupplier Quotation` sq
				WHERE
					sqi.parent = sq.name
					AND sq.docstatus < 2
					AND sqi.item_code ='{0}'
					AND sqi.request_for_quotation='{1}'
					AND sq.supplier='{2}'
					AND sq.status<>'Expired'
					order by sq.supplier limit 0,1""".format(
					pitem.item_code,request_for_quotation,s.supplier_name
				),
				as_dict=1,debug=0
				)
			else:
				supplier_quotation_item = frappe.db.sql(
				"""
				SELECT			
					sqi.rate, sq.supplier as supplier_name,sqi.net_amount
				FROM
					`tabSupplier Quotation Item` sqi,
					`tabSupplier Quotation` sq
				WHERE
					sqi.parent = sq.name
					AND sq.docstatus < 2
					AND sqi.item_code ='{0}'
					AND sq.name='{1}'
					AND sq.supplier='{2}'
					AND sq.status<>'Expired'
					order by sq.supplier limit 0,1""".format(
					pitem.item_code,suppqto,s.supplier_name
				),
				as_dict=1,debug=0
				)

			if supplier_quotation_item:
				for si in supplier_quotation_item:
					#amt=pitem.qty*si.rate					
					amt=si.net_amount					
					sp={}
					sp.update({'rate':si.rate,'amount':amt,'supplier':s.supplier_name})
					spi.append(sp)
			else:			
					sp={}
					sp.update({'rate':0,'amount':0,'supplier':s.supplier_name})
					spi.append(sp)
			
		dati.update({'sup':spi})
		dta.append(dati)

	#frappe.msgprint(str(dta))
	data={'items':dta,'suplier':supplier_list}
	return data

def prepare_data(supplier_quotation_data):
	out, groups, qty_list, suppliers=  [], [], [], []
	group_wise_map = defaultdict(list)
	supplier_qty_price_map = {}

	group_by_field = (
		"item_code"
	)
	company_currency = frappe.db.get_default("currency")
	float_precision = cint(frappe.db.get_default("float_precision")) or 2

	for data in supplier_quotation_data:
		group = data.get(group_by_field)  # get item or supplier value for this row

		supplier_currency = frappe.db.get_value(
			"Supplier", data.get("supplier_name"), "default_currency"
		)

		if supplier_currency:
			exchange_rate = get_exchange_rate(supplier_currency, company_currency)
		else:
			exchange_rate = 1

		row = {
			"item_code": data.get("item_code"),
			"supplier_name": data.get("supplier_name"),
			"quotation": data.get("parent"),
			"qty": data.get("qty"),
			"price": flt(data.get("amount") * exchange_rate, float_precision),
			"uom": data.get("uom"),
			"stock_uom": data.get("stock_uom"),
			"request_for_quotation": data.get("request_for_quotation"),
			"valid_till": data.get("valid_till"),
			"lead_time_days": data.get("lead_time_days"),
		}
		row["price_per_unit"] = flt(row["price"]) / (flt(data.get("stock_qty")) or 1)

		# map for report view of form {'supplier1'/'item1':[{},{},...]}
		group_wise_map[group].append(row)

		# map for chart preparation of the form {'supplier1': {'qty': 'price'}}
		supplier = data.get("supplier_name")
		
		groups.append(group)
		suppliers.append(supplier)
		qty_list.append(data.get("qty"))

	groups = list(set(groups))
	suppliers = list(set(suppliers))
	qty_list = list(set(qty_list))

	highlight_min_price = group_by_field = "item_code"

	# final data format for report view
	for group in groups:
		group_entries = group_wise_map[group]  # all entries pertaining to item/supplier
		group_entries[0].update({group_by_field: group})  # Add item/supplier name in first group row

		if highlight_min_price:
			prices = [group_entry["price_per_unit"] for group_entry in group_entries]
			min_price = min(prices)

		for entry in group_entries:
			if highlight_min_price and entry["price_per_unit"] == min_price:
				entry["min"] = 1
			out.append(entry)



	return out

def getitemordercount(itm,purchase_order=""):
	cont=''
	if purchase_order:
		itmc=frappe.db.sql(""" select i.qty-i.received_qty as qty,p.name from `tabPurchase Order` p left join `tabPurchase Order Item` i on p.name=i.parent
	where i.item_code='{0}' and p.status not in ('Closed','Hold') and p.docstatus=1 and p.name<>'{1}' and (i.qty-i.received_qty)>0 group by p.name""".format(itm,purchase_order),as_dict=1,debug=0)
	else:
		itmc=frappe.db.sql(""" select i.qty-i.received_qty as qty,p.name from `tabPurchase Order` p left join `tabPurchase Order Item` i on p.name=i.parent
	where i.item_code='{0}' and p.status not in ('Closed','Hold') and p.docstatus=1 and (i.qty-i.received_qty)>0 group by p.name""".format(itm),as_dict=1,debug=0)
	
	if itmc:
		for it in itmc:
			url=frappe.utils.get_url("app/purchase-order/{0}".format(it.name))
			cont+='<a href="'+url+'" target="_blank">'+it.name+'</a> (<b>'+str(it.qty)+'</b>), '

	return cont
