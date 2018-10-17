# -*- coding: utf-8 -*-
{
    'name': 'SaaS Portal',
    'version': '1.0.0',
    'author': 'Bista Solutions',
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'depends': ['oauth_provider', 'website', 'auth_signup', 'saas_base', 'saas_utils'],
    'data': [
        'data/mail_template_data.xml',
        'data/plan_sequence.xml',
        'data/cron.xml',
        'wizard/config_wizard.xml',
        'wizard/batch_delete.xml',
        'views/saas_portal.xml',
        'views/res_config.xml',
        'data/ir_config_parameter.xml',
        'data/subtype.xml',
        'data/support_team.xml',
        'views/res_users.xml',
        'data/res_users.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}