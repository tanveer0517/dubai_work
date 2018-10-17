# -*- coding: utf-8 -*-
{
'name': 'GoMart Client DB Connector',
'version': '1.0',
'author' : 'Bista Solutions Inc.',
'category': 'Connector',
'depends': [
           'base',
           'sale',
           'mint_client_multi_store',
           'mint_client_product_catelog'
           ],
'data':[
       'security/ir.model.access.csv',
       'views/view_sale_order.xml',
       'views/view_res_company.xml',
       'views/view_product_template.xml',
       'views/view_res_partner.xml',
       'views/view_res_company.xml',
       'views/view_res_users.xml',
       'wizard/product_catelog_wizard.xml',
       'wizard/res_customer_wizard.xml',
       'views/view_ir_sequence.xml',
       'views/view_gomart_server.xml',
        ],
'description':
                """
                GoMart Connector for the Client DB.
                """,
'python' : ['geopy']
}
