# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'SaaS User Auto Create',
    'version': '1.0',
    'category': 'User Management',
    'sequence': 11,
    'summary': 'Create user automatic when create employee',
    'author': 'Bista Solutions',
    'description': """
    - Create user automatic when create employee
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['base','hr','service_management','hr_employee_customization',
                'hr_holidays'],
    'data': [
        'security/user_security.xml',
        'views/hr_employee_view.xml',
        'views/res_group_view.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
