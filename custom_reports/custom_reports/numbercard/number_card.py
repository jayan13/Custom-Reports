import frappe

@frappe.whitelist()
def ac_balance_cs_sharjha():
    data = {}
    data['value']=0
    balance= frappe.db.sql("""SELECT SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit) as "account_Balance"
FROM `tabGL Entry`
WHERE
`tabGL Entry`.is_cancelled=0
AND `tabGL Entry`.company = 'ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.'
AND `tabGL Entry`.account = '114201 - CASH SALES - SHJ - APF' """,as_dict=1)[0]
   
    if balance:
        data['value']=round(balance.account_Balance,2)
    data['fieldtype']='Float'
    return data

@frappe.whitelist()
def ac_balance_cs_abudhabi():
    data = {}
    data['value']=0
    balance= frappe.db.sql("""SELECT SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit) as "account_Balance"
FROM `tabGL Entry`
WHERE
`tabGL Entry`.is_cancelled=0
AND `tabGL Entry`.company = 'ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.'
AND `tabGL Entry`.account = '114202 - CASH SALES - AUH - APF' """,as_dict=1)[0]
   
    if balance:
        data['value']=round(balance.account_Balance,2)
    data['fieldtype']='Float'
    return data

@frappe.whitelist()
def ac_balance_cs_alain():
    data = {}
    data['value']=0
    balance= frappe.db.sql("""SELECT SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit) as "account_Balance"
FROM `tabGL Entry`
WHERE
`tabGL Entry`.is_cancelled=0
AND `tabGL Entry`.company = 'ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.'
AND `tabGL Entry`.account = '114203 - CASH SALES - AL AIN - APF' """,as_dict=1)[0]
   
    if balance:
        data['value']=round(balance.account_Balance,2)
    data['fieldtype']='Float'
    return data

@frappe.whitelist()
def ac_balance_cs_farm():
    data = {}
    data['value']=0
    balance= frappe.db.sql("""SELECT SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit) as "account_Balance"
FROM `tabGL Entry`
WHERE
`tabGL Entry`.is_cancelled=0
AND `tabGL Entry`.company = 'ABU DHABI POULTRY FARM - SOLE PROPRIETORSHIP L.L.C.'
AND `tabGL Entry`.account = '114205 - EGG CASH SALE - FARM - APF' """,as_dict=1)[0]
   
    if balance:
        data['value']=round(balance.account_Balance,2)
    data['fieldtype']='Float'
    return data
