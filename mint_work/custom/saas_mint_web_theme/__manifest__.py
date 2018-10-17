# -*- coding: utf-8 -*-
{
    'name': "Saas Mint Web Theme",
    'summary': """Website theme for Mint cloud""",
    'description': """ """,
    'author': "Bista solutions",
    'website': "http://www.bistasolutions.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/
    # module_data.xml
    # for the full list
    'category': 'Theme',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'website', 'mint_partner_enhancement',
                # 'saas_login_registration',
                'saas_plan_subscription',
                #'saas_mint_backend_theme',
                ],
    # always loaded
    'data': [
        'views/website_menu_inherit_view.xml',
        # 'data/pages.xml',
        'views/mint_header_link.xml',
        'views/menu_page.xml',
        'views/mint_homepage.xml',
        'views/mint_services.xml',
        'views/mint_server_plan.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
