# -*- coding: utf-8 -*-
{
    'name': 'Custom Apps',
    'summary': """Simplify Apps Interface""",
    'images': [],
    'version': '1.0.0',
    'application': False,
    'author': 'Bistas Solutions',
    'website': 'https://bistasolutions.com',
    'category': 'Access',
    'depends': [
        'access_apps',
    ],
    'data': [
        'views/apps_view.xml',
        'security.xml',
        'data/ir_config_parameter.xml',
    ],

    'post_load': None,
    'pre_init_hook': None,
    'post_init_hook': None,

    'auto_install': False,
    'installable': True
}
