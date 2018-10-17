# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import requests
import json
import base64
import smtplib

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    card_number = fields.Char('Card Number')
    reference_pnr = fields.Char('Flight Ref or PNR')
    addc_acc_no = fields.Char('ADDC Account Number')