# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Bista SAAS user restrict',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """This module is restrict user after subscription expired
    """,
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'depends': [
        'web', 'saas_client', 'website'
    ],
    'data': [
        'views/templates.xml',
        'data/ir_config_parameter.xml'
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
