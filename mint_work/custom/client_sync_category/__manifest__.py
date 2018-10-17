# -*- coding: utf-8 -*-
{

    'name': 'Client Sync Pos category',
    "summary": "Client Sync Pos category",
    'version': '10.0.1',
    'author': "Bista Solutions",
    'category': 'POS',
    'depends': [
        'city',
        'point_of_sale',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
