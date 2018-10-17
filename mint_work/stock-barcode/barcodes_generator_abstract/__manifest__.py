# -*- coding: utf-8 -*-

{
    'name': 'Generate Barcodes (Abstract)',
    'summary': 'Generate Barcodes for Any Models',
    'version': '10.0.1.0.2',
    'category': 'Tools',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'license': 'AGPL-3',
    'depends': [
        'barcodes',
    ],
    'data': [
        'security/res_groups.xml',
        'views/view_barcode_rule.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_users.xml',
    ],
    'external_dependencies': {'python': ['barcode']},
}
