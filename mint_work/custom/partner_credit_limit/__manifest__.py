# -*- coding: utf-8 -*-
{
    'name': 'Partner Credit Limit',
    'version': '10.0.2.0.0',
    'category': 'Partner',
    'depends': ['account', 'sale'],
    'license': 'AGPL-3',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'summary': 'Set credit limit warning',
    'description': '''Partner Credit Limit'
        Checks for all over due payment and already paid amount
        if the difference is positive and acceptable then Salesman
        able to confirm SO
    ''',
    'data': [
        'views/partner_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
