# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Bista Out Of Stock',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """This module is calculate zero on the stock of product
    """,
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'depends': [
        'base', 'stock'
    ],
    'data':['views/product_template.xml'],
    'installable': True,
    'active': False,
}