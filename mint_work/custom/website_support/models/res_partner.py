# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ResPartnerTicket(models.Model):

    _inherit = "res.partner"
    
    display_quotes = fields.Boolean(string="Display Quotations")
    display_orders = fields.Boolean(string="Display Orders")
    display_invoices = fields.Boolean(string="Display Invoices")
    # only_my_ticket = fields.Boolean(string="Only My Ticket")
    all_ticket = fields.Boolean(string="All Ticket")
    ticket_grp = fields.Many2one('ticket.group', string='Ticket Group')
    ticket_group_ids = fields.Many2many('ticket.group', string="Ticket Group")