# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


# class ProductProduct(models.Model):
#     _inherit = "product.product"
#
#     image_ids = fields.One2many(
#                                 comodel_name='product.image',
#                                 inverse_name='product_id',
#                                 string='Product Images'
#                                 )


class ProductTemplate(models.Model):
    _inherit = "product.template"

    image_ids = fields.One2many('product.image','product_id', string='Product Images')
