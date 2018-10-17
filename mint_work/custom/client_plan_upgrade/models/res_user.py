# -*- coding: utf-8 -*-
from odoo import api, models, fields

class Users(models.Model):
    _inherit = "res.users"

    client_module_ids = fields.Many2many('ir.module.module', 'client_mod_rel_new', 'module_id',
                                                   'client_id',
                                                   string='Client Modules')