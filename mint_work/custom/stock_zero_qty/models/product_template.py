from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_qty_zero = fields.Boolean(compute='_is_qty_zero', string='Out Of Stock', help="Check if product quentity is zero.")

    @api.multi
    def _is_qty_zero(self):
        for each in self:
            if each.qty_available <= 0:
                each.is_qty_zero = True
