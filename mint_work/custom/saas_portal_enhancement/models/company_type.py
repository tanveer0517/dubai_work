# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaasCompanyTypeMaster(models.Model):
    _name = 'company.type'
    _rec_name = 'name'

    # Params values in thier variable
    active = fields.Boolean('Active', default=True)
    name = fields.Char('Company Type', requred=True,
                       help="""Give A Company Type Name""")
