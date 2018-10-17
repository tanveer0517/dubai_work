# -*- coding: utf-8 -*-
{
    'name': 'SaaS Client',
    'version': '1.0.0',
    'author': 'Bista Solutions',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'depends': [
        'auth_oauth',
        'auth_oauth_ip',
        'auth_oauth_check_client_id',
        'saas_utils',
        'mail',
        'web_settings_dashboard',
        'access_limit_records_number',
    ],
    'data': [
        'views/saas_client.xml',
        'views/res_config.xml',
        'security/rules.xml',
        'security/groups.xml',
        'data/ir_cron.xml',
        'data/auth_oauth_data.xml',
        'data/ir_config_parameter.xml',
        'data/ir_actions.xml',
    ],
    'installable': True,
    'qweb': [
        'static/src/xml/saas_dashboard.xml',
    ],
}
