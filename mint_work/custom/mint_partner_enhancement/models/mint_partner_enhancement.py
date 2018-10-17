    # -*- coding: utf-8 -*-

from odoo import models, fields, api

class Customer_Vat(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char(string='Vat No')
