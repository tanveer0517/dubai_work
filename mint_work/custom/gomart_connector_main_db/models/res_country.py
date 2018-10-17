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


class ResCountry(models.Model):
    _inherit = 'res.country'

    server_id = fields.Many2one('saas_portal.server', string='Server name')
