# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaasBusinessTypeMaster(models.Model):
    _name = 'business.type'
    _rec_name = 'name'

    # Params values in thier variable
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Business Type', requred=True,
                       help="""Give A Business Type Name""")
