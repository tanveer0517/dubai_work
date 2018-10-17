# -*- coding: utf-8 -*-
{
    'name': 'Multi Company Base',
    'summary': 'Provides a base for adding multi-company support to models.',
    'version': '10.0.1.0.1',
    'author': "Bista Solutions ",
    'website': 'http://www.bistasolutions.com',
    'category': 'base',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'pre_init_hook': 'create_company_assignment_view',
    'data': [
        'security/ir.model.access.csv',
    ],
}
