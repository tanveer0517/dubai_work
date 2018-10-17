# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class product_template(models.Model):

    _inherit = 'product.template'

    # price_update_id = fields.Many2one('mint.price.update.wizard')
