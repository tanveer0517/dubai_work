# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Mint Wastage Report',
    'version': '1.0.0',
    'summary': 'Store Wastage',
    'sequence': 30,
    'description': """

    """,
    'category': 'MRP',
    'website': 'https://www.bistasolutions.com/',
    "author": "Bista Solutions",
    'images': [],
    'depends': ['stock'],
    'data': [
        'data/stock_location.xml',
        'views/wastage_report_wizard_view.xml',
        'views/report.xml',
        'views/wastage_report_template_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
