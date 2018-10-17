# -*- coding: utf-8 -*-

{
    "name": "Mint Marakez API",
    "version": "10.0.1.0.0",
    'author': "Mint Odoo",
    'website': 'http://www.themint.ae',
    "category": "Hidden",
    "license": "AGPL-3",
    "summary": "Mint Marakez API",
    "description": """Mint Marakez API to sync data.""",
    "depends": ["base","city","product_enhancement","saas_portal_enhancement"],
    "data": [
        "views/jwt_authentication_view.xml",
        "views/res_lang_view.xml",
        "views/res_country_view.xml",
        "views/product_brand_view.xml",
        "views/new_client_registration_view.xml",
        "views/marakez_schedular.xml"
        ],
    "installable": True,
    "auto_install": False,
}
