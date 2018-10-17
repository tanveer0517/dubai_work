# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class POSCategory(models.Model):
    _inherit = 'pos.category'

    master_db_pos_cat_id = fields.Integer('Master db POS Category ID')
