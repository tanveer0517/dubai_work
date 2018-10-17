# -*- coding: utf-8 -*-

{
    'name': 'SaaS User Logs Server',
    'version': '1.0',
    'category': 'SaaS',
    'sequence': 10,
    'summary': 'Will log users login',
    'author': 'Bista Solutions',
    'description': """
    - Enable login users
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['saas_server',],
    'data': [
            'views/saas_view.xml',
    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
