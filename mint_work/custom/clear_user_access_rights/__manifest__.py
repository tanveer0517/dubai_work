# -*- coding: utf-8 -*-
{
    'name': "Clear User Access Right",

    'summary': """
        This module is used to clear users access rights.""",

    'description': """
        This module is used to clear all the access rights of a user created 
        externally and only provide Portal access to him except the Admin 
        will have some Access rights which other users will not have.
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
}
