# -*- coding: utf-8 -*-
{

    'name': 'Client Product Catelog Import',
    "summary": "Product Catelog",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'mint_client_product_catelog'
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/product_catelog_view.xml',
        'views/assets.xml',
        'wizard/catelog_import_view.xml'
    ],
    "demo": [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
