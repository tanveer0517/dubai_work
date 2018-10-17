# -*- coding: utf-8 -*-
{

    'name': 'Mint POS Client Enhancement',
    "summary": "Mint POS Client Enhancement",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'point of sale',
    'depends': [
        'mint_pos',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/templates.xml',
        'views/res_partner_view.xml'
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
