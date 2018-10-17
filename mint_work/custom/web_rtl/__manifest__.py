# -*- coding: utf-8 -*-
{
    'name': 'Web RTL',
    'version': '1.2',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'sequence': 4,
    'category': 'Usability',
    'summary': 'Web RTL (Right to Left) layout',
    'description':
        """
Adding RTL (Right to Left) Support for Odoo.
===========================================

This module provides a propper RTL support for Odoo.
        """,
    'depends': ['web'],
    'auto_install': False,
    'data': [
        'views/templates.xml',
    ],
}
