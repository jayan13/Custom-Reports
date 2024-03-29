from . import __version__ as app_version

app_name = "custom_reports"
app_title = "custom reports"
app_publisher = "alantech"
app_description = "custom reports"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jayakumar@alantechnologies.net"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_reports/css/custom_reports.css"
# app_include_js = "/assets/custom_reports/js/custom_reports.js"

# include js, css files in header of web template
# web_include_css = "/assets/custom_reports/css/custom_reports.css"
# web_include_js = "/assets/custom_reports/js/custom_reports.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "custom_reports/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Payroll Entry" : "public/js/pentry.js","Employee" : "public/js/employee.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_reports.install.before_install"
# after_install = "custom_reports.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "custom_reports.uninstall.before_uninstall"
# after_uninstall = "custom_reports.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_reports.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
	'Leave Application':'custom_reports.leave.LeaveApplicationCustom',
	'Payroll Entry':'custom_reports.override.PayrollEntryCustom',
	'Compensatory Leave Request':'custom_reports.compensatory_leave.CompensatoryLeaveRequestCustom',
	'Attendance':'custom_reports.attendance.AttendanceCustom',
	'Salary Slip':'custom_reports.salary_slip.SalarySlipCustom',	
 }
# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	#"Employee Checkin":{
	#	"on_update": "custom_reports.custom_reports.employee.mailalert.send_mail",
	#},
	"Sales Invoice": {        
        "before_insert": "custom_reports.api.update_cost_acc",
    },
	"Delivery Note" : {        
        "before_insert": "custom_reports.api.update_cost_acc",
    },
	"Salary Slip":{		
		"on_submit": "custom_reports.api.update_additional_sal_narration_sb",
		"after_insert": "custom_reports.api.update_additional_sal_narration_sb",
		"before_insert": "custom_reports.api.update_additional_sal_narration",
	},
	"Journal Entry":{
		"on_submit": [
			"custom_reports.api.update_pro_pay",
			"custom_reports.api.update_material_transfer"
			],
		"on_cancel":[
			"custom_reports.api.update_pro_pay_cancel",
			"custom_reports.api.cancel_material_transfer"
			],
	},
	"Payment Entry":{
		"on_submit": "custom_reports.api.update_pro_pay",
		"on_cancel": "custom_reports.api.update_pro_pay_cancel",
	}	
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_reports.tasks.all"
# 	],
# 	"daily": [
# 		"custom_reports.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_reports.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_reports.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_reports.tasks.monthly"
# 	]
# }

# Testing
# -------
override_whitelisted_methods = {
	'erpnext.payroll.doctype.gratuity.gratuity.calculate_work_experience_and_amount':'custom_reports.gratuity.calculate_work_experience_and_amount',
	'erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on':'custom_reports.leave.get_leave_balance_on',
	'erpnext.hr.doctype.leave_application.leave_application.get_leave_details':'custom_reports.leave.get_leave_details'
 }
 
# before_tests = "custom_reports.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_reports.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "custom_reports.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

fixtures = [
	{
		"doctype": "Salary Component",
		"filters": [
            [
                "name",
                "in",
                (   
					"Basic",               
					"Leave Salary",
					"Previous Month Balance",
					"Salary Advance Paid",
					"Salary Advance",
					"Holiday Over Time",
					"Over time",
                ),
            ]
        ],
	},
	{
		"doctype": "Gratuity Rule",
		"filters": [
            [
                "name",
                "in",
                (                  
					"Rule Under Limited Contract (UAE)",
					"Rule Under Unlimited Contract on termination (UAE)",
					"Rule Under Unlimited Contract on resignation (UAE)",
                ),
            ]
        ],
	},
	{
		"doctype": "Leave Type",
		"filters": [
            [
                "name",
                "in",
                (                  
					"Compensatory Off",
					"Annual Leave",
                ),
            ]
        ],
	},	
	{
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (                  
					"Company-payroll_jv_naming_series",
					"Employee-weekly_off_2",
					"Employee-weekly_off",
					"Employee-leave_provision_date",
					"Employee-ticket_provision_date",
					"Employee-used_tickets",
					"Employee-opening_ticket_amount_used",
					"Employee-opening_ticket_balance",
					"Employee-opening_ticket_balance_amount",
					"Employee-opening_leaves_accrued",
					"Employee-opening_balance_amount",
					"Employee-openning_entry_date",
					"Employee-no_of_tickets_eligible",
					"Employee-leaves_per_year",
					"Employee-ticket_price",
					"Employee-ticket_period",
					"Employee-opening_used_leaves",
					"Employee-opening_absent",
					"Employee-routing_number",
					"Employee-passport_copy_front_and_back",
					"Employee-eid_number",
					"Employee-eid_expiry",
					"Employee-eid_card_front_and_back",
					"Employee-visa",
					"Employee-visa_expiry",
					"Employee-visa_number",
					"Leave Application-duty_handover_to",
					"Leave Application-salary_paid_in_advance",
					"Leave Application-leave_category",
					"Payroll Entry-salary_comparison",
					"Payroll Entry-col_comp",
					"Payroll Entry-col_bk2",
					"Payroll Entry-over_time_sheet",
					"Payroll Entry-salary_sheet_without_over_time",
					"Payroll Entry-col_bk1",
					"Payroll Entry-employee_salary_sheet",
					"Payroll Entry-sec_brk",
					"Salary Slip-final_settlement_request",
					"Salary Slip-holiday_over_time",
					"Salary Slip-over_time",
					"Salary Slip-annual_leave_advanced_paid",
					"Salary Slip-annual_leave",
					"Compensatory Leave Request-shift_roster",
					"Leave Period-abbr",
					"Salary Detail-narration",
					"Additional Salary-narration",
					"Attendance-shift_roster",
					"Attendance-description",
					"Payment Entry-view_reference_details",
					"Journal Entry-payment_type",
					"Payment Entry-expense_request",
					"Material Request-journal_entry_issue",
					"Material Request-journal_entry",
					"Journal Entry-expense_request",
					"Journal Entry-customer_group_outstanding_invoices",
					"Company-payment_journal_entry_naming_series",
					"Company-journal_entry_ret_naming_series",
					"Company-journal_entry_naming_series",
					"Company-ministry_of_labor_employer_ids",
					"Company-ministry_of_labor_employer_id",
					"Bank-routing_number",
					"Employee-ministry_of_labor_employer_id",
					"Employee-employee_labor_card_number"
                ),
            ]
        ],
    },
	{ "doctype": "Report", "filters": [ ["name", "in", 
		( 
			"Shift Report",
			"Shift Roster",
			"Employee Salary Structure",
			"Salary Sheet Without Over Time",
			"Employee Salary Sheet",
			"Over Time Sheet",
			"Department Wise Attendance Sheet",
			"Monthly Ticket Provision",
			"Monthly Annual Leave Provision",
			"Monthly Gratuity Provision",
			"Employee Head Count",
			"Provision Leave",
			"Provision Ticket",
			"Provision Gratuity",
			"This month Annual Leave Report",
			"Department Wise Payroll Jv",
			"Gratuity Provisions",
			"Provision Air Ticket",
			"Provision Annual Leave",
			"PRO REQUEST", 
			"Employee Checkin Report",
			"Monthly Attendance Report",
		)
		
	] ] },
	{ "doctype": "Page", "filters": [ ["name", "in", ( "sif-file","salary-comparison","salary-sheet-without","over-time-sheet","employee-salary-shee" )] ] },
	{ "doctype": "Client Script", "filters": [ ["name", "in", ( "Leave Allocation-Form","Payroll Entry-Form","Company-Form","Material Request-Form","Annual Leave Payslip-Form","Leave Application-Form","Purchase Order-Form","Payment Entry-Form","Sales Order-Form" )] ] },
]
# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"custom_reports.auth.validate"
# ]

