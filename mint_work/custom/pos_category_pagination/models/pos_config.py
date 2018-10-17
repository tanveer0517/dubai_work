# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    default_show_no_of_category = fields.Integer(
        string='Default Show No. of Product Category', default=1000)
    is_category_button = fields.Boolean(
        string='Display subcategory button', default=True)
