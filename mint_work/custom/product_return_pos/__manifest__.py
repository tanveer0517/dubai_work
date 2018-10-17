# -*- coding: utf-8 -*-
{
    'name': 'Product Return In POS',
    'version': '10.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'POS Order Return',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'images': ['static/description/banner.jpg'],
    'depends': ['point_of_sale'],
    'data': [
             'views/return.xml',
             'views/pos_template.xml',
            ],
    'qweb': ['static/src/xml/pos_return.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}
