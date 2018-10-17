# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.sql_db import db_connect
from odoo.api import Environment, SUPERUSER_ID
from python_hosts import Hosts, HostsEntry
from odoo.tools import html2text, ustr


class SaasPortalCreateClient(models.TransientModel):
    _inherit = 'saas_portal.create_client'

    merchant_id = fields.Many2one('merchant.master',
                                  default = lambda self : self.env[
                                      'merchant.master'].search([], limit=1),
                                  string = "Merchant Type")
    store_type = fields.Selection([('single', 'Single'),
                                   ('multi', 'Chained')],
                                  default = 'single',
                                  string = "Store Type")
    num_of_outlets = fields.Integer(string = 'Number of Outlets', default = 1,
                                    help = """Provide the number of outlets 
                                        for this Company""")

    @api.multi
    def apply(self):
        try :
            clients_obj = self.env['saas_portal.client']
            new_client_obj = self.env['saas_portal.new.client']
            wizard = self[0]
            login = self.user_id.login
            self.user_id.action_clear_access_rights()
            self.user_id.write({'password' : self.user_id.login})
            database = wizard.name

            if login:
                self.check_user_exist(login)

            if database :
                self.check_db_exist(database)

            if self.plan_id.plan_subscription_ids:
                pass
            else :
                raise Warning(_('Sorry!!, Client will not be confirmed as no '
                                'Subscription is defined in the Plan '
                                'Subscription Page.'))

            client_rec = clients_obj.sudo().search(
                [('partner_id', '=', self.client_id.partner_id.id),
                 ('name', '=', database),
                 ('state', '=', 'draft')])

            new_client_rec = new_client_obj.sudo().search(
                [('database', '=', database),
                 ('state', 'not in', ['confirmed', 'rejected'])])

            # if alread the client is created by process stop due to server
            # disconnection or other sevrer related things then this will
            # delete the existing db and create another one
            if new_client_rec:
                raise Warning(_('Same Database found in "New '
                                'Registration request".'))

            if client_rec:
                client_rec._delete_database_server(force_delete = True)

            res = wizard.plan_id.create_new_database(dbname=wizard.name, partner_id=wizard.partner_id.id, user_id=self.user_id.id,
                                                     notify_user=self.notify_user,
                                                     support_team_id=self.support_team_id.id,
                                                     async=self.async_creation,
                                                     trial=self.trial)
            if self.async_creation:
                return True

            client = self.env['saas_portal.client'].browse(res.get('id'))
            if client :
                vals = {
                    'plan_price' : self.plan_id.plan_price,
                    'sub_period' : self.plan_id.sub_period,
                    'plan_type' : self.plan_id.plan_type,
                    'merchant_id' : self.merchant_id.id,
                    'store_type' : self.store_type,
                }
                client.write(vals)
            line_dict = []
            analytic_account = self.env['account.analytic.account']
            account_invoice = self.env['account.invoice']

            ana_vals = {}
            if self.user_id.partner_id :
                ana_vals.update({'partner_id' : self.user_id.partner_id.id,
                                 'name' : 'Subscription for ' +
                                          self.user_id.partner_id.name,
                                 'recurring_rule_type' :
                                     self.plan_id.sub_period,
                                 'recurring_invoices' : 'True',
                                 'client_id' : client.id
                                 })

                quantity = 1
                if self.num_of_outlets > 0 :
                    quantity = self.num_of_outlets

                for data in self.plan_id.plan_subscription_ids :
                    ana_vals_line = {}
                    ana_vals_line.update({
                        'product_id' : data.product_id.id,
                        'uom_id' : data.no_of_users or 1,
                        'name' : data.saas_prod_desc or data.product_id.name,
                        'price_unit' : data.subscription_price,
                        'quantity' : (data.no_of_users * quantity) or 1})
                    line_dict.append((0, 0, ana_vals_line))
                    ana_vals.update({'recurring_invoice_line_ids' : line_dict})
                analytic_id = analytic_account.create(ana_vals)
                analytic_id.recurring_create_invoice()
                invoices = account_invoice.search([('contract_id', '=',
                                                    analytic_id.id)])
                invoices.action_invoice_open()
                client.write({'subscription_id' : analytic_id.id})

            # Host entry is done for the ip address and database name
            hosts = Hosts(path = '/etc/hosts')
            new_entry = HostsEntry(entry_type = 'ipv4',
                                   address = '127.0.0.1',
                                   names = [database])
            hosts.add([new_entry])
            hosts.write()

            new_cr = db_connect(database).cursor()
            new_env = Environment(new_cr, SUPERUSER_ID, {})

            ir_config_obj = self.env['ir.config_parameter']
            client_url = new_env['ir.config_parameter'].get_param(
                'web.base.url')

            auth_vals = {
                'name' : 'Auth Provider for ' + self.user_id.name,
                'client_id' : new_env['ir.config_parameter'].get_param(
                    'database.uuid'),
                'enabled' : True,
                'body' : 'Login with Auth provider',
                'auth_endpoint' : client_url + '/oauth2/auth',
                'scope' : 'userinfo',
                'validation_endpoint' : client_url + '/oauth2/tokeninfo'
            }
            portal_provider = self.env['auth.oauth.provider'].create(
                auth_vals)
            self.user_id.write({
                'oauth_provider_id' : portal_provider.id,
                'oauth_uid' : 1
            })
            new_env['ir.config_parameter'].set_param('portal.database',
                                                     self.env.cr.dbname)
            new_env['ir.config_parameter'].set_param('portal.url',
                                                     ir_config_obj.get_param(
                                                         'web.base.url'))
            new_env['ir.config_parameter'].set_param('portal.provider',
                                                     portal_provider.id)
            new_env['ir.config_parameter'].set_param('server.url',
                                                     self.plan_id.server_id.name)
            new_cr.commit()

            # Search for the user in the new database for updating \
            # his related partner fields
            new_user = new_env['res.users'].search(
                [('login', '=', self.user_id.partner_id.email)], limit = 1)

            new_user_company = new_env['res.company'].search([], limit = 1)

            if self.store_type == 'multi' :
                if self.num_of_outlets >= 0 :
                    new_user_company.write({'store_type' : self.store_type,
                                            'number_of_outlets' :
                                                self.num_of_outlets})
                    group_multi_company = new_env.ref('base.group_multi_company',
                                                      False)
                    group_multi_company.write({'users' : [(4, new_user.id),
                                                          (4, 1)]})
            elif self.store_type == 'single' :
                new_user_company.write({'store_type' : self.store_type,
                                        'number_of_outlets' :
                                            self.num_of_outlets})

            group_store_master = new_env.ref(
                'mint_client_multi_store.saas_store_manager')
            group_store_master.write({'users' : [(4, new_user.id)]})
            new_cr.commit()
            new_cr.close()

            # client.server_id.action_sync_server(
            #     updating_client_ID=client.client_id)
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'saas_portal.client',
                'res_id': client.id,
                'target': 'current',
            }
        except Exception as e :
            raise UserError(_("ERROR ! :\n%s") % ustr(e))

    # Get the user if already exist
    @api.multi
    def check_user_exist(self, login = False) :
        if login :
            user_exist, new_client_exist = self.get_user_email_rec(
                login)

            if user_exist or new_client_exist :
                raise Warning(_("User Email is already taken. Already "
                                "exist in New Request or Already an "
                                "Instance is running related to this "
                                "Email. Please Create new one"))

    # Get the Database if already exist
    @api.multi
    def check_db_exist(self, database = False) :
        user_db_exist, new_client_db_exist = self.get_database_rec(
            database)

        if user_db_exist or new_client_db_exist :
            raise Warning(_("Database name already Exist, "
                            "Please provide another unique "
                            "database name."))

    # Function to check if user selected in New CLient request already exist
    #  in Client DB or in any pending state in new request
    def get_user_email_rec(self, login = False) :
        # objects variables
        client_database_obj = self.env['saas_portal.client']
        res_new_client_obj = self.env['saas_portal.new.client']

        user_exist = client_database_obj.sudo().search(
            [
                ('partner_id.email', '=', login),
                ('state', 'in', ['open', 'draft', 'pending', 'template'])
            ], limit = 1)

        new_client_exist = res_new_client_obj.sudo().search(
            [
                ('client_id.partner_id.email', '=', login),
                ('state', 'not in', ['rejected'])
            ], limit = 1)

        return user_exist, new_client_exist

    # Function to check if database written in new client request exist in
    # client database or in pending state in new client request or not
    def get_database_rec(self, database = False) :
        # objects variables
        client_database_obj = self.env['saas_portal.client']
        res_new_client_obj = self.env['saas_portal.new.client']

        user_db_exist = client_database_obj.sudo().search(
            ['|', '|', ('name', '=', database),
             ('name', '=', 'http://' + database),
             ('name', '=', 'https://' + database)], limit = 1)

        new_client_db_exist = res_new_client_obj.sudo().search(
            ['|', '|', ('database', '=', database),
             ('database', '=', 'http://' + database),
             ('database', '=', 'https://' + database)
             ], limit = 1)

        return user_db_exist, new_client_db_exist
