# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class New_Client_Rejection(models.Model):
    _name = 'new.client.rejection'
    _rec_name = 'name'

    # Params values in thier variable
    client_id = fields.Many2one('saas_portal.new.client', string="Client ID")
    name = fields.Text('Rejection Reason', requred=True,
                       help="""Rejection Reason""")
    file_name = fields.Char('File Name')
    state = fields.Selection([('rejected', 'Rejected'),
                              ('updated', 'Updated')], string="State")
    document = fields.Char('Document')
