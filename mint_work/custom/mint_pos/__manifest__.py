# -*- coding: utf-8 -*-
{

    'name': 'Mint POS Enhancement',
    "summary": "Mint POS Enhancement",
    'description':  """Mint POS Enhancement
                    """,
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'sale', 'point_of_sale',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/ir_sequence_data.xml',
        'views/mint_pos_order_view.xml',
        'views/mint_pos_backend_theme_view.xml',
    ],
    "demo": [
    ],
    'qweb': ['static/src/xml/pos.xml',],
    'installable': True,
    'auto_install': False,
    'application': True,
}
