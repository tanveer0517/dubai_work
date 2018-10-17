# -*- coding: utf-8 -*-
{
    'name': 'Control access to Apps',
    'version': '1.0.1',
    'author': 'Bistas Solutions',
    'category': 'Access',
    'website': 'https://bistasolutions.com',
    'depends': [
        'web_settings_dashboard',
        'access_restricted'
    ],
    'data': [
        'views/access_apps.xml',
        'security/access_apps_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True
}
