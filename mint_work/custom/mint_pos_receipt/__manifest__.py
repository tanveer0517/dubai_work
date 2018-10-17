# -*- coding: utf-8 -*-
{

    'name': 'Mint POS Receipt',
    "summary": "Mint POS Receipt",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'point_of_sale', 'point_of_sale_logo'
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/point_of_sale_template.xml',
        'views/point_of_sale.xml',
    ],
    "demo": [
    ],
    'qweb': ['static/src/xml/pos_receipt_view.xml',],
    'installable': True,
    'auto_install': False,
    'application': True,
}
