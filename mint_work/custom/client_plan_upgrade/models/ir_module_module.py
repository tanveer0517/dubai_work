# -*- coding: utf-8 -*-
from odoo import api, models, fields

# class ir_model(models.Model):
#     _inherit = 'ir.model'
#
#     ir_module_id = fields.Many2one('ir.module.module', string="Module")

class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    model_ids = fields.Many2many('ir.model','ir_module_model_rel',
                                 'ir_module_id', 'ir_model_id',
                                 string='Models')
    # client_id = fields.Many2one('res.users', string="User")