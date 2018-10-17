# -*- coding: utf-8 -*-
{
    'name': "Import Product Image",
    'version': '10.0.1.0.0',
    'summary': """Import Product Image from CSV File""",
    'description': """Import Product Image from CSV File(Web URL/File Path)""",
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Sales',
    'depends': ['sale','product_multi_images'],
    'data': [
        'security/ir.model.access.csv',
        'views/import_product_image_view.xml'],
    'license': 'AGPL-3',
    'images': ['static/description/banner.jpg'],
    'application': False,
    'installable': True,
    'auto_install': False,
}
