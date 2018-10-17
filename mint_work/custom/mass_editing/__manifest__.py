# -*- coding: utf-8 -*-
{
    'name': 'Mass Editing',
    'version': '10.0.1.1.0',
    'author': 'Bista Solutions',
    'category': 'Tools',
    'website': 'http://www.bistasolutions.com',
    'license': 'GPL-3 or any later version',
    'summary': 'Mass Editing',
    'uninstall_hook': 'uninstall_hook',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
