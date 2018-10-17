# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    out_of_stock = fields.Boolean(compute='_is_out_stock', string='Out Of Stock', readonly=True, help="Marked Out Of Stock, if stock reaches zero." )

    @api.multi
    def _is_out_stock(self):
        for product in self:
            if product.qty_available <= 0:
                product.out_of_stock = True
