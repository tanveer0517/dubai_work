# -*- coding: utf-8 -*-

{
    'name': 'Contracts Management recurring',
    'version': '10.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'depends': ['base', 'account', 'analytic', 'contract_show_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'data/contract_cron.xml',
        'views/contract.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
}
