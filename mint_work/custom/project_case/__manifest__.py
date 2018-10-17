# -*- encoding: utf-8 -*-
{
    'name': 'Case Tracking',
    'version': '1.0',
    'category': 'Project Management',
    'sequence': 9,""
    'summary': 'Support, Bug Tracker, Helpdesk',
    'description': """
Track Cases/Bugs Management for Projects
=========================================
This application allows you to manage the cases you might face in a project like bugs in a system, client complaints or material breakdowns. 

It allows the manager to quickly check the case, assign them and decide on their status quickly as they evolve.
    """,
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'depends': [
        'sales_team',
        'project',
        'mail',
        'account',
        'account_analytic_default',
        'analytic',
        'hr',
        'hr_timesheet_sheet',
    ],
    'data': [
            'security/helpdesk_security_view.xml',
            'security/ir.model.access.csv',             
            'project_case_view.xml',
            'project_case_menu.xml',
            'case_report_layout.xml',
            'report/case_report.xml',
            'report/support_call_report.xml',
            'report/reports.xml',
            'email_template.xml',
            'data.xml',

     ],
    'demo': [],
    'test': [ ],
    'installable': True,
    'auto_install': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
