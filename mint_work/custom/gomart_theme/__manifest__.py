# -*- coding: utf-8 -*-
{

    'name': 'Gomart Theme',
    "summary": "Gomart Theme",
    'description':  """Gomart Theme
                    """,
    'version': '10.0.1',
    'author': "Bista Solutions",
    'category': '',
    'depends': [
        'sale', 'point_of_sale', 'pos_category_pagination'
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': True,
    'auto_install': True,
}
