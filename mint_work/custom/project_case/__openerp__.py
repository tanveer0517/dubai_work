# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
    'author': 'OpenERP SA',
    'website': 'https://www.odoo.com/page/project-management',
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
