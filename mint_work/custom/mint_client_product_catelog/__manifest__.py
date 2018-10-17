# -*- coding: utf-8 -*-
{

    'name': 'Mint Client Product Catelog',
    "summary": "Product Catelog",
    'version': '10.0.1.0.1',
    'author': "Bista Solutions",
    'category': 'Base',
    'depends': [
        'product','sales_team','sale','point_of_sale','base_multi_company'
    ],
    "website": "https://www.bistasolutions.com",
    "data": [
        'security/product_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/product_catelog_view.xml',
        'views/product_request_view.xml',
        'views/product_brand_view.xml',
        'views/account_tax_view.xml',
        'wizard/add_catalog.xml',
        'views/create_edit_readonly_view.xml',
        'views/pos_category_inherit_view.xml',
    ],
    "demo": [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': '_update_product_category_client',

}
