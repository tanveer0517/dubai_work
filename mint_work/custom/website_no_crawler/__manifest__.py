# -*- coding: utf-8 -*-
{
    'name': 'Alter robots.txt disallow indexing',
    'summary': 'Disables robots.txt for indexing by webcrawlers like Google',
    'license': 'AGPL-3',
    'version': '10.0.1.0.0',
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Website',
    'depends': [
        'website',
    ],
    'data': [
        'views/disable_robots.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
