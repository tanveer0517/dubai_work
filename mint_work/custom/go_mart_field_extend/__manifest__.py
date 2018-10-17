# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Gomart Backend',
    'version': '1.0',
    'author': 'Bista Solutions',
    'sequence': 1,
    'category': 'gomart',
    'website': 'http://www.bistasolutions.com',
    'summary': ' Gomart extended fields',
    'description':  """
                    All the necessary field added
                    """,
    'depends': ['stock','point_of_sale'],
    "data": [
            'views/view_gomart_ext.xml',
            'views/view_pos_order.xml',
            'security/ir.model.access.csv',
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
