# -*- coding: utf-8 -*-
{
    'name': 'Product Enhancement',
    'version': '1.0',
    'category': 'product',
    'sequence': 11,
    'summary': 'Product Enhancement module for the product brand',
    'author': 'Bista Solutions',
    'description': 
    """
    - Maintain the product using the brand
    - Using Group info
    """,
    'website': 'www.bistasolutions.com',
    'depends': [
                'base',
                'sale',
                'point_of_sale'
               ],
    'data': [
            'security/ir.model.access.csv',
            'data/ir_sequence_data.xml',
            'views/product_enhancement.xml',
            'views/product_request_view.xml',
            'views/product_variant_menu_hide.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': '_update_product_category',
}
