# -*- coding: utf-8 -*-
from odoo import _, api, models, fields, SUPERUSER_ID, exceptions
from odoo.exceptions import Warning
# import psycopg2

import logging
_logger = logging.getLogger(__name__)

class saas_portal_plan(models.Model):
    _inherit = 'saas_portal.plan'

    plan_wages = fields.Integer('Sequence')

class SaasPortalClient(models.Model):
    _inherit = 'saas_portal.client'

    installed_client_module_ids = fields.Many2many('ir.module.module', 'client_mod_rel', 'client_module_id',
                                                  'client_id',
                                                  string='Installed Module')

    @api.multi
    def open_upgrade(self):
        return {
               'name': _('Plan Upgrade'),
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'view_mode': 'form',
               'res_model': 'saas.plan.upgrade',
               'target': 'new',
           }


