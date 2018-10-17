# -*- coding: utf-8 -*-
{
    'name': "Mint Helpdesk",
    'summary': """
      Extends helpdesk functionality for mint.
        """,
    'description': """
        Extends helpdesk functionality for mint.
    """,
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['website_support','website_mail'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/helpdesk_groups.xml',
        'security/security.xml',
        'wizard/open_case_wizard_view.xml',
        'views/helpdesk_view.xml',
        'views/website_support_ticket_template_ext.xml',
        'views/ticket_category.xml',
        'views/ticket_deadline.xml',
        'views/menus.xml',
        'report/helpdesk_report_view.xml'
    ],
}
