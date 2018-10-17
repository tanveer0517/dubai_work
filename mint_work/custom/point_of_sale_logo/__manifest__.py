# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Logo Change',
    'version': '10.0',
    'summary': """Logo change in Point of Sale (Screen & Receipt)""",
    'description': """"This module helps you to change a logo in every 
    point of sale. This will help you to identify the point of sale easily. 
    You can also see this logo in pos screen and pos receipt.""",
    'category': 'Point Of Sale',
    'author': 'Bista Solutions',
    'company': 'Bista Solutions',
    'website': "http://www.bistasolutions.com",
    'depends': ['base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_image_view.xml',
        'views/pos_image_view.xml',
    ],
    'qweb': ['static/src/xml/pos_ticket_view.xml',
             'static/src/xml/pos_screen_image_view.xml'],
    'license': '',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
