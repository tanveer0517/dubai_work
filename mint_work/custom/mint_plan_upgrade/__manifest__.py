# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Plan Upgrade ',
    'version': '1.0',
    'category': 'User Management',
    'sequence': 11,
    'summary': 'Allow to upgrade the plans',
    'author': 'Bista Solutions',
    'description': """
    - Allow to upgrade the plan
    """,
    'website': 'www.bistasolutions.com',
    'depends': ['base','saas_portal'],
    'data': [
        'wizard/plan_upgrade_wiz_view.xml',
        'views/plan_upgrade_view.xml',

    ],
    'demo': [
    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
