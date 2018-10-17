# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.onchange('company_id')
    def company_id_change(self):
        if self.company_id:
            self.journal_ids = [(6, 0 ,self.company_id.payment_option.ids)]