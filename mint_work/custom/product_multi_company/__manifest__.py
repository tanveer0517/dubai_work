# -*- coding: utf-8 -*-

{
    'name': "Product multi-company",
    'summary': "Select individually the product template visibility on each "
               "company",
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Product Management',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base_multi_company',
        'product',
    ],
    'data': [
        'views/product_template_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
