# -*- coding: utf-8 -*-
{
    'name': "Mint Partner Enhancement",
    'summary': """
        Customized View and fields for Customers""",
    'description': """
        This Module will Create a vat field in res.users view. On 
        registration of new client the vat field will be required to get VAT 
        no from Client
    """,
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        'views/mint_partner_enhancement_view.xml',
    ],
}
