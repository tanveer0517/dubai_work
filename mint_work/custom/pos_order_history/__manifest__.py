# -*- coding: utf-8 -*-
{
    'name': 'POS Order History',
    "summary": "This module for the POS order history",
    'description':  """This module for the POS order historyn
                    """,
    'version': '10.0.1',
    'author': "Bista Solutions",
    'category': 'POS',
    'depends': [
        'base',
        'point_of_sale',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/view_pos_order.xml',
        'reports/report_order_history.xml',
        'reports/report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
