# -*- coding: utf-8 -*-
{
    'name': 'Authentification - Brute-force Attack',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'summary': "Tracks Authentication Attempts and Prevents Brute-force"
               " Attacks module",
    'author': "Bista Solutions ",
    'website': 'http://www.bistasolutions.com',
    'depends': [
        'web',
        ],
    'data': [
        'security/ir_model_access.yml',
        'data/ir_config_parameter.xml',
        'views/view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
