# -*- encoding: utf-8 -*-
{
    'name': 'Product Multi Images',
    'version': '0.1',
    'category': 'Product',
    'description':  """Add Multiple images into product
                    """,
    'author': 'Bista Solutions Pvt Ltd.',
    'website': 'http://bistasolutions.com',
    'depends': [
                'base',
                'product'
                ],
    'data': [
            'security/ir.model.access.csv',
            'views/product_image_view.xml'
            ],
}
