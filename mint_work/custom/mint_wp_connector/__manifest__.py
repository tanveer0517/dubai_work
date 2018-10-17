# -*- coding: utf-8 -*-
{
    'name': "Wordpress MySQLdb Connector",

    'summary': """
        Wordpress MySQL db Connection and Syncing data""",

    'description': """
        Wordpress MySQL db Connection and Syncing data
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Connector',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'saas_portal',
                'saas_portal_enhancement',
                'saas_plan_subscription'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wp_config.xml',
        'views/saas_portal_config_settings.xml',
    ],
}
