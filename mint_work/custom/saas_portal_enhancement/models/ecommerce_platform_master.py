# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaasEcommercePlatformMaster(models.Model):
    _name = 'ecommerce.platform'
    _rec_name = 'name'

    # Params values in thier variable
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Ecommerce Name', requred=True,
                       help="""Give A Ecommerce Name""")
