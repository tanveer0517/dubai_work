# -*- coding: utf-8 -*-
{

    'name': 'Mint POS Multi Barcode',
    "summary": "Mint POS Multi Barcode",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'purchase',
        'mint_pos',
        'barcodes_generator_product',
        'barcodes_generator_package',
        'barcodes_generator_lot',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'security/ir.model.access.csv',
        'wizard/product_multi_barcode_import_views.xml',
        'views/templates.xml',
        'views/mint_barcode_rule_view.xml',
        'views/mint_pos_multi_barcode_product.xml',
    ],
    'installable': True,
}
