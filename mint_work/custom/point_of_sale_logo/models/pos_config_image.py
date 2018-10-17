# -*- coding: utf-8 -*-
from odoo import models, fields


class PosConfigImage(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary(string='Image')
    enable_receipt_image = fields.Boolean('Enable Receipt Image')
    receipt_image = fields.Binary(string='Receipt Image')
