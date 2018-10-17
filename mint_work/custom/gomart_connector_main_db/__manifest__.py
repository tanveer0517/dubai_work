# -*- coding: utf-8 -*-
{
'name': 'GoMart Main DB Connector',
'version': '1.0',
'author' : 'Bista Solutions Inc.',
'category': 'Connector',
'depends': [
           'base',
           'stock',
           'point_of_sale',
           'sale',
           'account',
           'product_enhancement',
           'city',
           'mint_pos',
           'product',
           'saas_portal_enhancement'
           ],
'data':[
        'security/ir.model.access.csv',
        'views/view_city_city.xml',
        'views/view_account_tax.xml',
        'views/view_product_category.xml',
        'views/view_product_brand.xml',
        'views/view_product_group.xml',
        'views/view_product_template.xml',
        'views/view_product_uom.xml',
        'views/view_res_partner.xml',
        'wizard/add_product.xml',
        'wizard/res_customer_wizard.xml',
        'views/view_ir_sequence.xml',
        'views/view_gomart_server.xml',
        'views/view_gomart_sync.xml'
        ],
'description':
                """
                GoMart Connector for the Main(Portal) DB.
                """,
'python' : ['geopy']
}
