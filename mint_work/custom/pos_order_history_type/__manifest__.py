# -*- coding: utf-8 -*-
{
    'name': 'POS Order History by Product Type',
    "summary": "This module for the POS order history on Basis of Product "
               "Type Selection",
    'description':  """This module for the POS order history on Basis of Product "
               "Type Selection
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
        'views/pos_sales_multi_report_wizard_view.xml',
        'reports/report_sale_orders.xml',
        'reports/report.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
