# -*- coding: utf-8 -*-
{
    'name': 'Saas Portal login and Registration',
    'version': '1.0',
    'category': '',
    'sequence': 9, ""
                   'summary': 'Login, Registration, Email Created',
    'description': """

    """,
    'author': 'Bista Solutions',
    'website': 'https://www.bistasolutions.com',
    'depends': [
        'web',
        'website',
        'saas_portal_templates',
        'auth_oauth',
        'auth_signup',
        'mail',
        'clear_user_access_rights',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'data/saas_client_registration_mail.xml',
        'views/css_js_links.xml',
        'views/error_handling_template.xml',
        'views/login_template.xml',
        'views/registration_template.xml',
        'views/customer_create_template.xml',
        'views/reset_password_template.xml',
        'views/auth_provider_template.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
