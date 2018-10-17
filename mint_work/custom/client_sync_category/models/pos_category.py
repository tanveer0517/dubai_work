# -*- coding: utf-8 -*-

from odoo import fields, models, api

class PosCategory(models.Model):
    """Product Category"""
    _inherit = 'pos.category'

    category_id = fields.Char(string='Reference No')
    client_allow_product = fields.Boolean('Allow Product', default=True)
    active = fields.Boolean('Active')
