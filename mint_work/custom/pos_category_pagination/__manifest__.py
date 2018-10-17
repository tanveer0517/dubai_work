# -*- coding: utf-8 -*-
{

    'name': 'POS Product Category Pagination',
    "summary": "POS Product Category Pagination",
    'description':  """POS Product Category Pagination
                    """,
    'version': '10.0.1',
    'author': "Bista Solutions",
    'category': 'POS',
    'depends': [
        'point_of_sale',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'security/ir.model.access.csv',
    	'views/pos_config_view.xml',
    	'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
}
