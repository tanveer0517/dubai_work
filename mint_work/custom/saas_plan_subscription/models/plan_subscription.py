# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, Warning
import odoo.addons.decimal_precision as dp

import simplejson
import werkzeug

import requests
from odoo.addons.saas_base.exceptions import MaximumDBException, \
    MaximumTrialDBException
from odoo.http import request
from odoo.sql_db import db_connect
from odoo.api import Environment,SUPERUSER_ID
import ast

class saas_portal_plan(models.Model):
    _inherit = 'saas_portal.plan'

    @api.multi
    # @api.constrains('installed_module_ids', 'plan_type')
    def _module_ids(self):
        # Check the module list in plan.
        # Raise warning if there is no product added in package.
        # Raise warning if you add more than 1 trial record per plan
        for rec in self:
            if not rec.installed_module_ids:
                raise Warning(_('Please add product in package'))

            trial_plan_rec = rec.search_count([('plan_type', '=', 'trial'),
                                               ('server_id', '=', rec.server_id.id)])
            if rec.plan_type == 'trial':
                if trial_plan_rec > 1:
                    raise Warning(_('You Cannot Add More then 1 Trial Plan '
                                    'Record'))

    @api.model
    def _get_buy_route(self):
        # Adding some required module in Installed Module list.
        mod_ids = self.env['ir.module.module'].search(
            [('name', 'in', ['hr', 'saas_custom_mail_config','sale',
                             'mint_client_product_catelog',
                             'client_sync_category'])])
        if mod_ids:
            return mod_ids.ids
        return []

    active = fields.Boolean('Active', default=True)
    plan_features_ids = fields.One2many('plan.features.master',
                                        'plan_id',
                                        string='Plan Features',
                                        help="""Add your Features of the
                                        plan related to server and define
                                        what features will be available in
                                        this plan.""")
    plan_subscription_ids = fields.One2many('bista.plan.subscription',
                                            'subscription_id',
                                            string='Plan Subscription',
                                            required = True,
                                            )
    plan_description_ids = fields.One2many('plan.description',
                                           'plan_description_id',
                                           string='Plan Description')

    plan_price = fields.Float(
        compute='_compute_plan_cost', readonly=True, string='Plan Price',
        store=True,
        digits=dp.get_precision('Product Price'),
        help="Total Cost for the plan calculated from all the service products")
    sub_period = fields.Selection(
        [('monthly', 'Month(s)'),
         ('yearly', 'Year(s)')], default = 'monthly', string = 'Subscription',
        required = True,
        help = "Specify Interval for automatic invoice generation.")
    recurring_rule_type = fields.Selection(
        [('monthly', 'Month(s)'),
         ('yearly', 'Year(s)')], default='monthly', string='Recurrency',
        help="Specify Interval for automatic invoice generation.")
    plan_type = fields.Selection(
        [('subscription', 'Subscription'), ('trial', 'Trial')],
        string='Plan Type', default= 'subscription', required = True)
    required_module_ids = fields.Many2many('ir.module.module', 'req_mod_rel',
                                           'req_module_id', 'plan_id',
                                           string='Installed Module',
                                           default= lambda self:
                                           self._get_buy_route())
    installed_module_ids = fields.Many2many('ir.module.module', 'ext_mod_rel',
                                            'ext_module_id', 'plan_id',
                                            string='Extra Module')
    expiration = fields.Integer('Expiration (hours)', default = 730,
                                help = 'time to delete database. Use for demo')
    button_text = fields.Selection(
        [('select_plan', 'Select Plan'),
         ('select_free_trial', 'Select Free Trial')], default='select_plan',
        string='WP Button Text',
        help="Specify what text you want to show belw the feature list to "
             "customer as per plan type (free or paid).")

    # This function will change the expiration hours based on the
    # subscription period selection
    @api.onchange('sub_period')
    def _onchange_sub_period(self) :
        #
        if self.sub_period == 'monthly' :
            self.expiration = 730
        if self.sub_period == 'yearly' :
            self.expiration = 730 * 12

    # This method will integrate all the master list define in the
    # server into the plan feature list where it will create new record
    # related to individual plan.
    @api.multi
    def update_plan_feature_master(self) :
        if self.server_id :
            feature_list = []
            for rec in self.plan_features_ids:
                if rec:
                    rec.unlink()
            if self.server_id.feature_ids:
                for features in self.server_id.feature_ids :
                    feature_child_list = []
                    for featuer_list_id in features.feature_list_ids :
                        feature_child_list.append((0, 0,
                                                   {'name' : featuer_list_id.name,
                                                    'pfeature_list_id' : featuer_list_id.id
                                                    }))
                    feature_list.append((0, 0, {
                        'name' : features.name,
                        'pfeature_master_id' : features.id,
                        'feature_list_ids' : feature_child_list,
                    }))
                self.plan_features_ids = feature_list
                return True

    @api.multi
    def create_template(self, addons=None):
        # Inherite method for updating Installed Module list on creation of
        # plan.
        mod_lst = []
        if self.required_module_ids:
            for module_name in self.required_module_ids:
                mod_lst.append(module_name.name)
        if self.installed_module_ids:
            for ins_name in self.installed_module_ids:
                mod_lst.append(ins_name.name)
            addons = mod_lst
        return super(saas_portal_plan, self).create_template(addons=addons)

    @api.multi
    def _create_new_database(self, dbname=None, client_id=None,
                             partner_id=None, user_id=None, notify_user=True,
                             trial=False, support_team_id=None, async=None):
        # Inherit method for setting company data to the register user'd
        # company in client instance.
        self.ensure_one()
        server = self.server_id
        if not server:
            server = self.env['saas_portal.server'].get_saas_server()

        # server.action_sync_server()
        if not partner_id and user_id:
            user = self.env['res.users'].browse(user_id)
            partner_id = user.partner_id.id

        if not trial and self.maximum_allowed_dbs_per_partner != 0:
            db_count = self.env['saas_portal.client'].search_count(
                [('partner_id', '=', partner_id), ('state', '=', 'open'),
                 ('plan_id', '=', self.id), ('trial', '=', False)])
            if db_count >= self.maximum_allowed_dbs_per_partner:
                raise MaximumDBException("Limit of databases for this plan "
                                         "is %(maximum)s reached" % {
                                             'maximum': self.maximum_allowed_dbs_per_partner})
        if trial and self.maximum_allowed_trial_dbs_per_partner != 0:
            trial_db_count = self.env['saas_portal.client'].search_count(
                [('partner_id', '=', partner_id), ('state', '=', 'open'),
                 ('plan_id', '=', self.id), ('trial', '=', True)])
            if trial_db_count >= self.maximum_allowed_trial_dbs_per_partner:
                raise MaximumTrialDBException("Limit of trial databases for "
                                              "this plan is %(maximum)s "
                                              "reached" % {
                                                  'maximum': self.maximum_allowed_trial_dbs_per_partner})
        if trial:
            client_expiration = self._get_expiration(trial)
        else:
            client_expiration = self._get_expiration(trial=True)
        vals = {'name': dbname or self.generate_dbname(),
                'server_id': server.id,
                'plan_id': self.id,
                'partner_id': partner_id,
                'trial': trial,
                'support_team_id': support_team_id,
                'expiration_datetime': client_expiration,
                }
        client = None
        if client_id:
            vals['client_id'] = client_id
            client = self.env['saas_portal.client'].search(
                [('client_id', '=', client_id)])

        vals = self._new_database_vals(vals)

        if client:
            client.write(vals)
        else:
            client = self.env['saas_portal.client'].create(vals)
        client_id = client.client_id
        owner_user_data = self._prepare_owner_user_data(user_id)

        state = {
            'd': client.name,
            'public_url': client.public_url,
            'e': client_expiration,
            'r': client.public_url + 'web',
            'h': client.host,
            'owner_user': owner_user_data,
            't': client.trial,
        }
        if self.template_id:
            state.update({'db_template': self.template_id.name})
        scope = ['userinfo', 'force_login', 'trial', 'skiptheuse']
        req, req_kwargs = server._request_server(
            path='/saas_server/new_database', state=state, client_id=client_id,
            scope=scope, )
        res = requests.Session().send(req, **req_kwargs)
        if res.status_code != 200:
            raise Warning('Error on request: %s\nReason: %s \n Message: %s' %
                          (req.url, res.reason, res.content))
        data = simplejson.loads(res.text)
        if self._context.get('active_model') == 'saas_portal.plan':
            if data and data.get('state'):
                new_db_name = ast.literal_eval(data.get('state'))
                f_name = new_db_name.get('d')
                new_cr = db_connect(str(f_name)).cursor()
                new_env = Environment(new_cr, SUPERUSER_ID, {})
                new_comp = new_env['res.company'].search([], limit=1)
                new_user_company_vals = {
                    'logo': '',
                    'name': client.name,
                    'rml_header1': client.name,
                    'website': 'http://yourcomapny.com',
                    'phone': '',
                    'email': 'info@yourcompany.com',
                }
                new_comp.write(new_user_company_vals)
                new_cr.commit()
        params = {
            'state': data.get('state'),
            'access_token': client.oauth_application_id._get_access_token(
                user_id, create=True),
        }
        url = '{url}?{params}'.format(url=data.get('url'),
                                      params=werkzeug.url_encode(params))
        auth_url = url

        # send email if there is mail template record
        template = self.on_create_email_template
        if template and notify_user:
            # we have to have a user in this place(how to user without a user?)
            user = self.env['res.users'].browse(user_id)
            client.with_context(user=user).message_post_with_template(
                template.id, composition_mode='comment')

        client.send_params_to_client_db()
        # TODO make async call of action_sync_server here
        # client.server_id.action_sync_server()
        client.sync_client()

        return {'url': url, 'id': client.id, 'client_id': client_id,
                'auth_url': auth_url}

    @api.multi
    def write(self, vals):
        # Inherit write method for adding addons list from product.
        # Specailly used for package product and bundle product.
        product_obj = self.env['product.template']
        if self._context.get('from_create', False):
            updated_list =[]
            for data in vals.get('plan_subscription_ids'):
                product_data = product_obj.browse(data[2].get('product_id'))
                if product_data.module_ids:
                    updated_list += vals['installed_module_ids'][0][
                                        1] + product_data.module_ids.ids
            if updated_list:
                vals.update(
                    {'installed_module_ids': [(4, updated_list)]})
            if vals.get('plan_description_ids'):
                vals.pop('plan_description_ids')
            if vals.get('plan_features_ids'):
                vals.pop('plan_features_ids')
            res = super(saas_portal_plan, self).write(vals)
            self._module_ids()
            return res
        else:
            for rec in self:
                if vals.get('plan_subscription_ids'):
                    install_ids = []
                    for pla_sub in vals.get('plan_subscription_ids'):
                        if pla_sub[0] == 0:
                            product_data = product_obj.browse(pla_sub[2].get(
                                'product_id'))
                            if  product_data.module_ids:
                                install_ids += product_data.module_ids.ids
                            if product_data.bundled_product_ids:
                                for product in \
                                        product_data.bundled_product_ids:
                                    vals['plan_subscription_ids'].append((0, 0, {'product_id':
                                                                                     product.id,
                                                                                 'saas_prod_desc':
                                                                                     product.saas_prod_desc,
                                                                                 'subscritpion_price':
                                                                                     product.list_price}))
                                    install_ids += product.module_ids.ids
                        if install_ids:
                            vals.update({'installed_module_ids': [(4,install_ids)]})
                        if pla_sub[0] == 2:
                            updated_addons,updated_list,product_list, \
                            sub_unilink = [], [], [], []
                            sub_obj = self.env['bista.plan.subscription']
                            sub_data = sub_obj.search([('id','=',pla_sub[1])])
                            sub_unilink.append(sub_data.id)
                            product_data = product_obj.browse(
                                sub_data.product_id.id)
                            updated_list += product_data.module_ids.ids
                            if product_data.bundled_product_ids:
                                for product in product_data.bundled_product_ids:
                                    updated_list += product.module_ids.ids
                                    product_list.append(product.id)
                            sub_data = sub_obj.search([('product_id','in',
                                                        product_list),
                                                       ('subscription_id','=',rec.id)])
                            updated_addons =list(set(
                                rec.installed_module_ids.ids)
                                                 - \
                                                 set(updated_list))
                            vals.update({'installed_module_ids': [(6, 0,
                                                                   updated_addons)],
                                         'plan_subscription_ids' : [(2,
                                                                     sub_unilink + sub_data.ids)]})
            res = super(saas_portal_plan, self).write(vals)
            self._module_ids()
            return res

    @api.model
    def create(self, vals):
        # Inherit write method for adding addons list from product.
        # Specailly used for package product and bundle product.
        res = super(saas_portal_plan, self).create(vals)
        if res.plan_subscription_ids:
            updated_list = []
            for pla_sub in res.plan_subscription_ids:
                if pla_sub.product_id and pla_sub.product_id.module_ids:
                    updated_list += vals['installed_module_ids'] + \
                                    pla_sub.product_id.module_ids.ids
                bundled_vals = []
                if pla_sub.product_id.bundled_product_ids:
                    for product in pla_sub.product_id.bundled_product_ids:
                        bundled_vals.append((0,0,{'product_id':
                                                      product.id,
                                                  'saas_prod_desc':
                                                      product.saas_prod_desc,
                                                  'subscription_price':
                                                      product.list_price}))
                vals.update({'plan_subscription_ids':bundled_vals})
            if updated_list:
                vals.update(
                    {'installed_module_ids': [(4, updated_list)]})
        res.with_context({'from_create':True}).write(vals)
        self._module_ids()
        return res


    @api.depends(
        'plan_subscription_ids.subscription_price',
        'plan_subscription_ids.no_of_users')
    def _compute_plan_cost(self):
        component_cost = 0.0
        for plan in self:
            for line in plan.plan_subscription_ids:
                component_cost += line.subscription_price * line.no_of_users
            plan.plan_price = component_cost

    @api.multi
    def unlink(self):
        oauth_app_obj = self.env['oauth.application']
        plan_client_id = self.template_id.client_id
        if plan_client_id:
            result = super(saas_portal_plan, self).unlink()
            res = oauth_app_obj.search([('client_id','=', plan_client_id)])
            res.unlink()
        else:
            result = super(saas_portal_plan, self).unlink()
        return result


class saas_plan_subscription(models.Model):
    _name = 'bista.plan.subscription'

    subscription_id = fields.Many2one('saas_portal.plan')
    # subscription_title = fields.Char('Subscription Description')
    saas_prod_desc = fields.Text('Product Description')
    subscription_period = fields.Integer('Period (Months)')
    no_of_users = fields.Integer('Number of Users', default=1)
    size_limit = fields.Float('Size Limit')
    subscription_price = fields.Float('Price')
    product_id = fields.Many2one('product.product', string="SAAS Products")
    reference_prod_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', string="SAAS Product Template")
    date_start = fields.Date(default=fields.Date.context_today)
    recurring_next_date = fields.Date(
        copy=False,
        string='Date of Next Invoice')

    _sql_constraints = [('product_uniq', 'unique (subscription_id,product_id)',
                         'Duplicate products in Subscription line are not '
                         'allowed !')]

    @api.onchange('product_id')
    def _onchange_product_id(self, context=False):
        # Set the list price and product description on selection of product
        #  on plan.
        if self.product_id:
            self.subscription_price = self.product_id.list_price
            self.saas_prod_desc = self.product_id.saas_prod_desc


class bista_plan_features(models.Model):
    _name = 'plan.description'

    plan_description_id = fields.Many2one('saas_portal.plan')
    plan_description_details = fields.Char('Plan Description Details')


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    recurring_rule_type = fields.Selection(
        [
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)'),
        ],
        default='monthly',
        string='Recurrency',
        help="Specify Interval for automatic invoice generation.")


class PlanFeaturesMaster(models.Model):
    _name = 'plan.features.master'

    plan_id = fields.Many2one('saas_portal.plan', string="Plan Id")
    # pfeature_master_id = fields.Many2one('saas_portal.server.features',
    #                                     string = 'Feature', readonly=True,
    #                                     help="""Field is related to Main
    #                                     Feature Master id""")
    pfeature_master_id = fields.Integer('Feature id', readonly = True,
                                        help = """Field is related to Main 
                                            Feature Master id""")
    name = fields.Char('Name',
                       help = """Define the Feature for which the
                       server is Define.""")
    # server_feature_id = fields.Many2one('')
    feature_list_ids = fields.One2many('plan.feature.list',
                                       'plan_feature_id',
                                       ondelete = 'cascade',
                                       string = "Feature Name",
                                       required = True,
                                       help = """List down the Feature list
                                               related to this Server Feature.
                                               """)


class PlanFeatureList(models.Model):
    _name = 'plan.feature.list'

    plan_feature_id = fields.Many2one('plan.features.master',
                                      ondelete='cascade')
    # pfeature_list_id = fields.Many2one('server.feature.list',
    #                                    string="Feature List",
    #                                    readonly = True,
    #                                    help="""Field is related to feature
    #                                    list master""")
    pfeature_list_id = fields.Integer("Feature List id",
                                      readonly = True,
                                      help = """Field is related to feature 
                                           list master""")
    name = fields.Char('Child Feature Name', help = """Define the
        Child Feature name for which this Feature is related to.""")
    checked = fields.Boolean('Check if True/False')
    is_there = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Yes/No")
    description = fields.Char('Value')
