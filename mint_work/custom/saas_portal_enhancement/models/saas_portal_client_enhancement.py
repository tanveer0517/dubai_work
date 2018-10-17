# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaasPortalClientEnhancement(models.Model):
    _inherit = 'saas_portal.client'

    req_no = fields.Char('Request No', help="""Reference of the request 
    number generated""")
    plan_price = fields.Float(string = 'Plan Price', readonly=True)
    sub_period = fields.Selection(
        [('monthly', 'Month(s)'),
         ('yearly', 'Year(s)')], string = 'Subscription Type', readonly=True,
        help = "Specify Interval for automatic invoice generation.")
    plan_type = fields.Selection(
        [('subscription', 'Subscription'), ('trial', 'Trial'),
         ('cancel', 'Cancel')], string = 'Plan Type', readonly=True)
    merchant_id = fields.Many2one('merchant.master', string = "Merchant Type")
    # store_id = fields.Many2one('store.master', string = "Store Type",
    #                            readonly=True)
    store_type = fields.Selection([('single', 'Single'),
                                   ('multi', 'Chained')],
                                  string = "Store Type")
    subscription_id = fields.Many2one('account.analytic.account',
                                      string="Subscription")
    subscription_count = fields.Integer("Subscriptions",
                                       compute='_compute_subscription_count')


    @api.multi
    def _compute_subscription_count(self):
        for client in self:
            client.subscription_count = self.env[
                'account.analytic.account'].search_count([('client_id','=',
                                                           client.id),('client_id','!=',False)])

    @api.onchange('state', 'trial')
    def onchange(self):
        if self.state in ['cancelled','deleted']:
            self.plan_type = 'cancel'

        if self.trial:
            self.plan_type = 'trial'


class res_partner(models.Model):
    _inherit = 'res.partner'

    subscription_ids = fields.One2many('account.analytic.account',
                                       'partner_id',
                                      string="Subscription")
    subscription_count = fields.Integer("Subscriptions",
                                       compute='_compute_subscription_count')


    @api.multi
    def _compute_subscription_count(self):
        for partner in self:
            partner.subscription_count = self.env[
                'account.analytic.account'].search_count([('partner_id','=' , partner.id),])

class res_bank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char('IBAN', size=25)


