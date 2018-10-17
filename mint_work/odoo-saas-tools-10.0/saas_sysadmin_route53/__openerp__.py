# -*- coding: utf-8 -*-
{
    'name': 'SaaS System Administration Route 53',
    'summary': "Aws Route 53 integration for SAAS Tools",
    'version': '1.0.0',
    'author': 'Bista Solutions',
    'license': 'LGPL-3',
    'support': 'support@bistasolutions.com',
    'website': 'http://www.bistasolutions.com',
    'external_dependencies': {
        'python': [
            'boto',
        ],
    },
    'depends': [
        'saas_sysadmin',
        'saas_sysadmin_aws',
        'saas_sysadmin_aws_route53',
    ],
    'data': [
    ],
    'installable': True,
}
