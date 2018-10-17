# -*- coding: utf-8 -*-
{
    'name': "Saas Plan Configuration",
    'summary': """
        saas_plan_subscription
        """,
    'description': """
        1) Describe in short what the plan offers
        2) List out Different plan subscription for the plan
    """,
    'author': "Bista solutions",
    'website': "http://www.bistasolutions.com",
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'web', 'saas_portal', 'website_portal',
                'website_portal_sale','stock','procurement'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/css_js_links.xml',
        'views/plan_feature_master_view.xml',
        'views/saas_plan_config_view.xml',
        'views/default_webiste_portal_change_layout.xml',
        'views/saas_plan_subscription_template.xml',
        'views/product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
