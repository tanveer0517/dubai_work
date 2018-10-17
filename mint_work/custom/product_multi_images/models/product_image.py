# -*- encoding: utf-8 -*-
from openerp import models, tools, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProductImages(models.Model):
    _name = "product.image"

    image = fields.Binary(string="Image")
    sequence = fields.Char(string="Sequence")
    name = fields.Char(string="Name")
    default = fields.Boolean(string="Main Product Image")

    product_id = fields.Many2one(comodel_name='product.template', string='Product')
