{
    'name': "Website Help Desk / Support Ticket",
    'version': "1.4",
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    'category': "Tools",
    'summary': "A helpdesk / support ticket system for your website",
    'description': "A helpdesk / support ticket system for your website",
    'license':'LGPL-3',
    'data': [
        'views/load_css_js_file.xml',
        # 'views/project_case_view.xml',
        'views/website_support_ticket_templates.xml',
        'views/res_partner_view.xml',
        # 'data/website.menu.csv',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': ['mail','web', 'crm', 'website','document','project_case',
                'website_portal_sale', 'saas_plan_subscription'],
    'images':[
        'static/description/3.jpg',
        'static/description/1.jpg',
        'static/description/2.jpg',
        'static/description/4.jpg',
        'static/description/5.jpg',
    ],
    'installable': True,
}