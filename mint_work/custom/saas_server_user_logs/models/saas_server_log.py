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

class SaasServerClient(models.Model):

    _inherit = 'saas_server.client'

    user_log_ids = fields.One2many('saas_server.client.log','client_id', string='Server Log')
    client_type = fields.Selection(
        [('client', 'Client'),
         ('plan', 'Plan')], string='Client Type')

    @api.multi
    def write(self, vals):
        self.user_log_ids.unlink()
        return super(SaasServerClient, self).write(vals)

    @api.one
    def _prepare_database(self, client_env, owner_user=None, is_template_db=False, addons=[], access_token=None, tz=None, server_requests_scheme='http'):
        # Inherit this method for updating client type in server instance
        # for synchronization purpose.
        if is_template_db:
            self.client_type = 'plan'
        else:
            self.client_type = 'client'
        return super(SaasServerClient, self)._prepare_database(client_env=client_env, owner_user=owner_user, is_template_db=is_template_db, addons=addons, access_token=access_token, tz=tz, server_requests_scheme=server_requests_scheme)


    @api.one
    def _get_data(self, client_env, check_client_id):
        # Inherit method for updating user log date.
        client_id = client_env['ir.config_parameter'].get_param('database.uuid')
        if check_client_id != client_id:
            return {'state': 'deleted'}
        users = client_env['res.users'].search([('share', '=', False), ('id', '!=', SUPERUSER_ID)])
        param_obj = client_env['ir.config_parameter']
        max_users = param_obj.get_param('saas_client.max_users', '0').strip()
        suspended = param_obj.get_param('saas_client.suspended', '0').strip()
        total_storage_limit = param_obj.get_param('saas_client.total_storage_limit', '0').strip()

        user_dict =[]
        for i in users:
            user_dict.append((0,0,{'name':i.name,'login_date':i.login_date}))
        users_len = len(users)
        data_dir = odoo.tools.config['data_dir']

        file_storage = get_size('%s/filestore/%s' % (data_dir, self.name))
        file_storage = int(file_storage / (1024 * 1024))

        client_env.cr.execute("select pg_database_size('%s')" % self.name)
        db_storage = client_env.cr.fetchone()[0]
        db_storage = int(db_storage / (1024 * 1024))

        data = {
            'client_id': client_id,
            'users_len': users_len,
            'max_users': max_users,
            'file_storage': file_storage,
            'db_storage': db_storage,
            'total_storage_limit': total_storage_limit,
            'user_log_ids':  user_dict,
        }
        if suspended == '0' and self.state == 'pending':
            data.update({'state': 'open'})
        if suspended == '1' and self.state == 'open':
            data.update({'state': 'pending'})
        return data

class SaasServerClientLog(models.Model):
    _name = 'saas_server.client.log'
    client_id = fields.Many2one('saas_server.client', string='Client Details')
    name = fields.Char('Name')
    login_date = fields.Datetime( string='Latest connection')
