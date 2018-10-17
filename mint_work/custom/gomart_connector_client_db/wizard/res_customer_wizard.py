# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class ResPartnerWizard(models.TransientModel):
    _name = 'res.partner.wizard'

    @api.multi
    def add_customer_gomart(self):
        if self._context and self._context.get('active_ids'):
            for pro in self._context.get('active_ids'):
                catalog_rec = self.env['res.partner'].browse(pro)
                catalog_rec.createCustomer()
