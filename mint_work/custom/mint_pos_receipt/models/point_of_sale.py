# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_multi_lang_receipt = fields.Boolean(
        'Allow Multi Lang Receipt', default=False)
    print_wise = fields.Selection([
        ('line_wise', 'Line Wise'),
        ('section_wise', 'Section Wise')],
        string='Receipt Policy')
    first_lang = fields.Selection([
        ('en_US', 'English'),
        ('ar_SY', 'Arabic')],
        string='First Language')
    second_lang = fields.Selection([
        ('en_US', 'English'),
        ('ar_SY', 'Arabic')],
        string='Second Language')

    #If allow_multi_lang_receipt False set it dependent field to False.
    @api.onchange('allow_multi_lang_receipt')
    def onchange_allow_multi_lang_receipt(self):
        if not self.allow_multi_lang_receipt:
            self.second_lang = False
            self.first_lang = False
            self.print_wise = False

    #Set the second lang based on first lang.
    #So if first lang is arabic second lang will assign to english and vice versa.
    @api.onchange('first_lang')
    def onchange_lang(self):
        self.second_lang = self.first_lang and self.first_lang == 'en_US' \
                           and 'ar_SY' or self.first_lang == 'ar_SY' and \
                                          'en_US' or False

