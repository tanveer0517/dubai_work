# -*- coding: utf-8 -*-
{

    'name': 'Password Security',
    "summary": "Allow admin to set password security requirements.",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'auth_crypt',
        'auth_signup',
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
        'security/res_users_pass_history.xml',
    ],
    "demo": [
        'demo/res_users.xml',
    ],
    'installable': True,
}
