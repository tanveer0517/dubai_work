# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains('order_line')
    def _check_order_line(self):
        #Add constraint for not allow to sale product lower than cost price.
        for rec in self:
            for so_line in rec.order_line:
                if so_line.product_id.standard_price > so_line.price_unit:
                    raise ValidationError(_('Product sale price is lower than cost price'))


