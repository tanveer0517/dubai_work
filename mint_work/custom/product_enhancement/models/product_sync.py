# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import logging


_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_updated_on_clients_ids = fields.Many2many('saas_portal.client')

    @api.multi
    def write(self, vals):
        if 'product_updated_on_clients_ids' in vals and len(vals) == 1:
            return super(ProductTemplate, self).write(vals)
        else:
            self.product_updated_on_clients_ids = [(5, False, False)]

            return super(ProductTemplate, self).write(vals)
