# -*- coding: utf-8 -*-
{
    'name': "Mint Product Price Update",

    'summary': """
        Update Multi Product Sale Price or Cost Price""",

    'description': """
        This module will provide a wizard in which you can add multiple 
        product and provide cost price or sale price into it and update at 
        once only to all product.
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/mint_product_prices_update_view.xml',
    ],
}
