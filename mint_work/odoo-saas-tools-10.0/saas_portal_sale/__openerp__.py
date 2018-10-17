# -*- coding: utf-8 -*-
{
    'name': "Saas Portal Sale",
    'author': "Bista Solutions",
    'license': 'LGPL-3',
    'category': 'SaaS',
    "support": "support@bistasolutions.com",
    'website': 'http://www.bistasolutions.com',
    'version': '1.0.0',
    'depends': [
        'sale',
        'saas_portal',
        'product_price_factor',
        'saas_portal_start',
        'contract',
    ],
    'data': [
        'views/product_views.xml',
        'views/saas_portal.xml',
        'data/mail_template_data.xml',
        'data/ir_config_parameter.xml',
    ],
}
