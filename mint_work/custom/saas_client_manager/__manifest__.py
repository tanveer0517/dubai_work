# -*- coding: utf-8 -*-

{
    'name': 'SaaS Client Manager',
    'version': '1.0',
    'category': 'User Management',
    'sequence': 11,
    'summary': 'Allow client to create users',
    'author': 'Bista Solutions',
    'description': """
    - Allow client to create users
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['base'],
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/client_user_manager.xml',
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
