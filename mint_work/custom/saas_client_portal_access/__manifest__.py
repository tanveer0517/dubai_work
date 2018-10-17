# -*- coding: utf-8 -*-
{
    'name': 'SaaS Client Portal Access',
    'version': '1.0',
    'category': 'User Management',
    'sequence': 11,
    'summary': 'Allow client to login in to portal database for handling own account detials',
    'author': 'Bista Solutions',
    'description': """
    - Allow client to login in to portal database for handling own account detials
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['base','oauth_provider' ],
    'data': [
            'views/client_portal_access.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/client_portal_access_template.xml',
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
