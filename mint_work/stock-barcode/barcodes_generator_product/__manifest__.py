# -*- coding: utf-8 -*-

{
    'name': 'Generate Barcodes for Products',
    'summary': 'Generate Barcodes for Products (Templates and Variants)',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'license': 'AGPL-3',
    'depends': [
        'barcodes_generator_abstract',
        'product',
    ],
    'data': [
        'views/view_product_product.xml',
        'views/view_product_template.xml',
    ],
    'demo': [
        'demo/res_users.xml',
        'demo/barcode_rule.xml',
        'demo/product.xml',
        'demo/function.xml',
    ],
}
