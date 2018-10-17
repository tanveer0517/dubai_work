# -*- coding: utf-8 -*-

{
    "name": "Mint VAS",
    "version": "10.0.1.0.0",
    'author': "Mint Odoo",
    'website': 'http://www.themint.ae',
    "category": "Hidden",
    "license": "AGPL-3",
    "summary": "Mint VAS",
    "description": """Creates a model for Mint VAS.""",
    "depends": ["base",'point_of_sale'],
    "data": [
        "views/res_partner_view.xml",
        "views/pos_order_view.xml",
        'views/mint_vas_backend_theme_view.xml',
        ],
    "qweb": ["static/src/xml/pos.xml",],
    "installable": True,
    "auto_install": False,
}
