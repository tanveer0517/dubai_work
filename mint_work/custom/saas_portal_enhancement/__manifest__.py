# -*- coding: utf-8 -*-
{
    'name': "Saas Portal Enhancement",

    'summary': """
        Servie menu, New Client Registration, Merchant configuration""",

    'description': """
        1) Will Create Service menu as a Parent Menu and in Servers menu as 
        submenu of Service Menu
        
        2) Allow The Client to Register for subscription plan and wait till 
        admin confirms it
        
        3) Merchant configuration according to the Servers define
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    'category': 'website',
    'version': '0.1',

    # any module necessary for this one to work correctly

    'depends': ['base',
                'website',
                'saas_portal',
                'contract',
                'product',
                'product_enhancement',
                'website_portal_sale',
                'mail',
                'saas_plan_subscription',
                'clear_user_access_rights',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/initial_dashboard_data.xml',
        'data/business_types_data.xml',
        'data/ir_sequence_data.xml',
        'data/req_send_for_approval_mail.xml',
        'data/client_req_rejected.xml',
        'data/document_pending_mail.xml',
        'data/client_document_rejected.xml',
        'wizard/client_document_rejection_wizard_view.xml',
        'wizard/client_rejection_wizard_view.xml',
        'wizard/config_wizard.xml',
        'views/css_js_links.xml',
        'views/merchant_master.xml',
        'views/saas_portal_enhancement.xml',
        'views/new_client_registration_view.xml',
        'views/store_master.xml',
        'views/company_type.xml',
        'views/feature_master_view.xml',
        'views/business_type.xml',
        'views/ecommerce_platform_master.xml',
        'views/saas_portal_client_enhancement.xml',
        'views/subscription_view.xml',
        'views/client_rejection.xml',
        'views/mint_new_client_registration_status_template.xml',
        'views/forbidden_error_template.xml',
    ],
}
