# -*- coding: utf-8 -*-
{
    'name': 'SaaS Server Backup S3',
    'version': '1.0.0',
    'author': 'Bista Solutions',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': ['saas_server'],
    'data': [
        'views/res_config.xml',
    ],
    'installable': True,
}
