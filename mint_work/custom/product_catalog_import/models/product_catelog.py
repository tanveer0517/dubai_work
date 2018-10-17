# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp


class Productcatelog(models.Model):
    _inherit = "product.catelog"

    @api.model
    def import_catalog(self):
        dummy,view_id = self.env['ir.model.data'].get_object_reference('product_catalog_import',
                                                                        'catalog_import_view_form')
        return {
            'name': _("Catalog Import"),
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'view_type': 'form',
            'res_model': 'catelog.import',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {}
        }
