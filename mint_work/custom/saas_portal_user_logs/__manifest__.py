# -*- coding: utf-8 -*-

{
    'name': 'SaaS Portal User Logs',
    'version': '1.0',
    'category': 'SaaS',
    'sequence': 11,
    'summary': 'Will log users login',
    'author': 'Bista Solutions',
    'description': """
    - Enable log users
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['base','saas_portal'],
    'data': [
            'security/ir.model.access.csv',
            'views/saas_view.xml',
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
