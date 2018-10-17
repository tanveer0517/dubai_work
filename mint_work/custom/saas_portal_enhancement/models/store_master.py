# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaasStoreMaster(models.Model):
    _name = 'store.master'
    _rec_name = 'store_name'

    # Params values in thier variable
    active = fields.Boolean('Active', default=True)
    store_name = fields.Char('Store Name', requred=True,
                       help="""Give A Store Type Name""")
