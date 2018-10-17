# -*- coding: utf-8 -*-
{
    'name': 'Mint Client Multi Store',
    'version': '10.0',
    'category': 'Sale and POS',
    'sequence': 14,
    'summary': '',
    'author': 'Bista Solutions',
    'website': 'www.bistasolutions.com',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'point_of_sale',
        'product_multi_company',
        'mint_client_product_catelog',
        'city'
    ],
    'data': [
        'security/multi_store_security.xml',
        'security/ir.model.access.csv',
        # 'views/store_data.xml',
        'views/company_view.xml',

        # 'views/pos_mutli_store_template.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
