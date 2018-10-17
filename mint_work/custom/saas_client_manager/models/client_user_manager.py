# -*- coding: utf-8 -*-
from odoo.addons.saas_base.tools import get_size
import time
import odoo
from datetime import datetime
from odoo.service import db
from odoo import api, models, fields, SUPERUSER_ID, exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2
import random
import string

import logging
_logger = logging.getLogger(__name__)


class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    user_log_ids = fields.One2many('saas_portal.client.log','client_id', string='Server Log')

    @api.multi
    def write(self, vals):
        # self.user_log_ids.unlink()
        return super(SaasPortalClient, self).write(vals)

class SaasPortalClientLog(models.Model):
    _name = 'saas_portal.client.log'
    client_id = fields.Many2one('saas_server.client', string='Client Details')
    name = fields.Char('Name')
    login_date = fields.Datetime( string='Latest connection')
