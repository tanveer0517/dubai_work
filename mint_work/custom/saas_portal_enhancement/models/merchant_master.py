# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaasMerchantMaster(models.Model):
    _name = 'merchant.master'

    # Params values in thier variable
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Name', requred=True,
                       help="""Give A Merchant Type Name""")
