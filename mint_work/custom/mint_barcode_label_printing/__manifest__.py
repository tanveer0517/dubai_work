# -*- coding: utf-8 -*-
{
    'name': "Mint Product Multi Barcode Label Printing ",

    'summary': """
        Prints Barcode on Sheet to be used on Product""",

    'description': """
        Print Barocde of the same product multiple times to stick it on the 
        product used in the grocery shop, or in fashion store for selling 
        the product by scanning the barccode only
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'barcode',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/print_label_wizard_view.xml',
        'views/views.xml',
        'views/print_label_report_view.xml',

    ],
}
