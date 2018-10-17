# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    client_id = fields.Many2one('saas_portal.client', string="Client")
    instance_count = fields.Integer("Subscriptions",
                                       compute='_compute_subscription_count')


    @api.multi
    def _compute_subscription_count(self):
        for account in self:
            account.instance_count = self.env['saas_portal.client'].search_count([('id','=' ,
                                                     account.client_id.id),('subscription_id','!=',False)])

class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_code = fields.Char(string='Tax code')
    server_id = fields.Many2one('saas_portal.server', 'Server name')

    @api.model
    def create(self, vals):
        vals['tax_code'] = self.env['ir.sequence'].next_by_code('account.tax')
        result = super(AccountTax, self).create(vals)
        return result

    _sql_constraints = [
        ('category_uniq', 'unique(tax_code)', _("A Tax code can only be assigned to one Tax !")),
    ]