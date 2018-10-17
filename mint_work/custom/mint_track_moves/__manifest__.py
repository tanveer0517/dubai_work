# -*- coding: utf-8 -*-
{
    'name': "Mint Track Moves",

    'summary': """
        Track Stock Moves by different requirements""",

    'description': """
        As there are many features given in normal stock moves to search by 
        name and other details but not by Barcode, lots, serial number. 
        
        So this module provide this feature as to track the stock moves of a 
        particular product by its barcode(through scanning the barcode from 
        machine), through Lot number, or through Unique Serial Number 
        provided on the Product.
        
        Just click on the Track Moves, It will open a wizard. enter the 
        barcode or the lot number or the serial number of the product of 
        which you want the moves. Thenn click on Track button. It will display 
        all the possible result it will get
    """,

    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'wizard/track_move_wizard_view.xml'
    ],
}
