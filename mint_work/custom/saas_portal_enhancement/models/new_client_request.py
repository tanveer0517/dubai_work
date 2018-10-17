# -*- coding: utf-8 -*-
import copy
import json


from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError
from odoo.sql_db import db_connect
from odoo.api import Environment, SUPERUSER_ID
from python_hosts import Hosts, HostsEntry
from odoo.tools import html2text, ustr
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    # This function will check the user in the res.users db is ecist then
    # raise warning or else create user
    @api.model
    def create(self, vals):
        login = vals.get('login')
        
        if login:
            rec_user = self.env['res.users'].search([('login','=', login)])
            rec_partner = self.env['res.partner'].search([('email', '=', 
                                                           login)])
            
            if rec_user or rec_partner:
                raise Warning(_("User Email or is already taken. "
                                "Already exist in New Request or Already an "
                                "Instance is running related to this "
                                "Email. Please Create new one"))
        
        return super(ResUsers, self).create(vals)


class SaasNewClientself(models.Model):
    _name = 'saas_portal.new.client'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'client_id'

    # Params values in thier variable
    request_no = fields.Char(string='Request No', required=True, copy=False,
                             readonly=True, states={'draft': [
            ('readonly', False)]}, index=True, default=lambda self: _('New'))
    state = fields.Selection([('new', 'New'),
                              ('document_pending', 'Asked For Documents'),
                              ('pending_approval', 'Pending Approval'),
                              ('document_rejected', 'Document Rejected'),
                              ('document_approval', 'Document Approval'),
                              ('confirmed', 'Approved'),
                              ('rejected', 'Rejected'),], default='new')
    client_id = fields.Many2one('res.users', string="Client Name")
    client_email = fields.Char(related='client_id.login',
                               string="Email", store=True)
    plan_id = fields.Many2one('saas_portal.plan', string="Selected Plan")
    contact_no = fields.Char(related='client_id.partner_id.mobile',
                             string='Contact No', store=True)
    landline_no = fields.Char(related = 'client_id.partner_id.phone',
                             string = 'Landline No', store=True)
    vat = fields.Char(related='client_id.vat', string='VAT No', store=True)
    company = fields.Char('Company Name')
    company_website = fields.Char('Website')
    company_reg_num = fields.Char('Company Registered Number')
    company_type = fields.Many2one('company.type', string="Company Type")
    database = fields.Char('Domain Name')
    plan_type = fields.Selection([('subscription', 'Subscription'),
                                  ('trial', 'Trial')],
                                 related='plan_id.plan_type', store=True)
    merchant_id = fields.Many2one('merchant.master',
                                  default = lambda self : self.env[
                                      'merchant.master'].search([], limit=1),
                                  string="Merchant Type")
    # store_id = fields.Many2one('store.master', string="Store Type")
    store_type = fields.Selection([('single', 'Single'),
                                  ('multi', 'Chained')],
                                  default='single',
                                  string = "Store Type")
    street1 = fields.Char(string = "Street1")
    street2 = fields.Char(string = "Street2")
    # zip = fields.Char(string = "Zip")
    city = fields.Char(related='client_id.partner_id.city', string='City',
                       store=True)
    state_id = fields.Many2one("res.country.state",
                               related = 'client_id.partner_id.state_id',
                               string = 'State',
                               ondelete = 'restrict', store=True)
    country_id = fields.Many2one('res.country',
                                 related =
                                 'client_id.partner_id.country_id',
                                 string = 'Country',
                                 ondelete = 'restrict', store=True)
    plan_price = fields.Float(related="plan_id.plan_price",
                              string = 'Plan Price', store=True)
    sub_period = fields.Selection(
        [('monthly', 'Month(s)'),
         ('yearly', 'Year(s)')], related='plan_id.sub_period',
        string = 'Subscription', store=True,
        help = "Specify Interval for automatic invoice generation.")
    num_of_outlets = fields.Integer(string='Number of Outlets', default=1,
                                    help="""Provide the number of outlets 
                                    for this Company""")
    # product_type = fields.Char('Product Type')
    brand_ids = fields.Many2many('product.brand', 'allowed_product_brand',
                                 'client_id', 'brand_id',
                                 string="Brands Allowed to Sell",
                                 help="""Brands Allowed to Sell""")
    business_type_ids = fields.Many2many('business.type',
                                         'your_business_types',
                                         'client_id', 'business_id',
                                         string = "Business Types",
                                         help = """Business Types""")
    avg_selling_price = fields.Float('Average Selling Price', )
    avg_monthly_sales = fields.Float('Average Monthly Sales')
    num_of_styles = fields.Integer('Number of Styles')
    ecommerce_platforms_ids = fields.Many2many('ecommerce.platform',
                                               'ecommerce_platform_table',
                                               'client_id', 'ecommerce_id',
                                               string= "Ecommerce Platforms")
    types_of_barcodes = fields.Selection([('any', 'ANY'),
                                          ('ean13', 'EAN13'),
                                          ('ean8', 'EAN8'),
                                          ('upca', 'UPC-A')],
                                         string='Type of Barcode Used')
    emirates_id_card = fields.Binary('Emirates ID Card',
                                     help="""Upload Emirates ID Card For 
                                     Proof""")
    emirates_id_card_name = fields.Char('File Name')
    emirates_id_card_rejected = fields.Boolean('Rejected', default=True)
    emirates_id_card_rejected_state = fields.Selection(
        [('rejected','Rejected'), ('updated', 'Updated')], string = "State")
    passport_and_poa = fields.Binary('Passport and POA',
                                     help = """Upload Passport and POA For 
                                         Proof""")
    passport_and_poa_name = fields.Char('File Name')
    passport_and_poa_rejected = fields.Boolean('Rejected', default = True)
    passport_and_poa_rejected_state = fields.Selection(
        [('rejected', 'Rejected'), ('updated', 'Updated')], string = "State")
    vat_num = fields.Binary('VAT Number',
                            help = """Upload VAT Number Paper For Proof""")
    vat_num_name = fields.Char('File Name')
    vat_num_rejected = fields.Boolean('Rejected', default = True)
    vat_num_rejected_state = fields.Selection([('rejected', 'Rejected'),
                                               ('updated', 'Updated')],
                                              string = "State")
    visa_and_poa = fields.Binary('VISA and POA',
                                 help = """Upload VISA and POA For Proof""")
    visa_and_poa_name = fields.Char('File Name')
    visa_and_poa_rejected = fields.Boolean('Rejected', default = True)
    visa_and_poa_rejected_state = fields.Selection([('rejected', 'Rejected'),
                                                    ('updated', 'Updated')],
                                                   string = "State")
    operating_address_uae = fields.Binary('Operating Address UAE',
                                          help = """Upload Operating Address 
                                          UAE For Proof""")
    operating_address_uae_name = fields.Char('File Name')
    operating_address_uae_rejected = fields.Boolean('Rejected',
                                                    default = True)
    operating_address_uae_rejected_state = fields.Selection(
        [('rejected', 'Rejected'), ('updated', 'Updated')], string = "State")
    trade_license = fields.Binary('Trade License',
                                  help = """Upload Trade License For 
                                  Proof""")
    trade_license_name = fields.Char('File Name')
    trade_license_rejected = fields.Boolean('Rejected', default = True)
    trade_license_rejected_state = fields.Selection([('rejected', 'Rejected'),
                                                     ('updated', 'Updated')],
                                                    string = "State")
    rejection = fields.One2many('new.client.rejection', 'client_id',
                                string='Rejection Reason')
    client_rejection_note = fields.Text('Client Rejection Reason')
    client_bank_id = fields.Many2one('res.bank', string='Bank Name')
    client_bank_acc = fields.Char('Bank Account Number', size=15)
    client_bank_iban = fields.Char('Bank IBAN', size=25)

    # On Create New Client Registration Request Number will be Generated
    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['request_no'] = self.env['ir.sequence'].next_by_code(
                'saas_portal.new.client') or _('New')

        client_id = vals.get('client_id')
        user_rec = self.env['res.users'].browse(client_id)
        database = (vals.get('database')).strip()

        if user_rec:
            self.check_user_exist(user_rec.login)

        if database:
            self.check_db_exist(database)

        user_rec.action_clear_access_rights()
        # ====================================================
        # ====== Dont Remove this Commented Code =============
        # ====================================================
        # grp_ids = user_rec.groups_id.ids
        # portal_id = self.env.ref('base.group_portal').id
        # if portal_id not in grp_ids:
        #     grp_ids.append((4, portal_id))
        # user_rec.write({'password': user_rec.login,
        #                 'groups_id': grp_ids})
        user_rec.write({'password' : user_rec.login})
        result = super(SaasNewClientself, self).create(vals)
        return result

    # This function will check the client name is changes or not same with
    # database name is changed or not if change and if exist then it will
    # raise the warninign or else it will update the existing
    @api.multi
    def write(self, vals):
        if vals.get('client_id'):
            client_id = vals.get('client_id')
            user_rec = self.env['res.users'].browse(client_id)
            if user_rec :
                self.check_user_exist(user_rec.login)

        if vals.get('database'):
            database = (vals.get('database')).strip()
            if database :
                self.check_db_exist(database)

        return super(SaasNewClientself, self).write(vals)

    # Mailing Function which will be called from Several other Function
    @api.multi
    def send_user_info_mail(self, template = False):
        mail_configured = self.check_outgoing_mail()
        if mail_configured and template:
            template.send_mail(self.id, force_send = True)
            return True
        else:
            raise Warning(_("Mail Template is Not Define or Not Found"))

    @api.onchange('company')
    def onchange_company(self):
        self.database = ''
        config = self.env['ir.config_parameter']
        saas_config = self.env['saas_portal.config.settings'].search(
                [], limit=1, order="id desc")
        alies_name = saas_config.base_saas_domain
        if alies_name == False :
            base_saas_rec = config.search([('key', '=',
                                            'saas_portal.base_saas_domain')],
                                          limit = 1)
            alies_name = base_saas_rec.value
        if len(alies_name) > 0:
            if self.company:
                company_name = (self.company).lower().strip()
                company = company_name.replace(" ", "-")
                database = (company.lower().strip()) + '.' + alies_name
                self.database = database

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('emirates_id_card')
    def onchange_emirates_id_card(self):
        vals = {}
        if self.emirates_id_card:
            emirates_id_card_found = self.check_file_dublicate(
                self.emirates_id_card_name)
            if emirates_id_card_found:
                return self.update_self_with_existing_documents(
                    'emirates_id_card')
            else:
                self.update_self_with_new_documents('emirates_id_card')

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('passport_and_poa')
    def onchange_passport_and_poa(self) :
        if self.passport_and_poa:
            passport_and_poa_found = self.check_file_dublicate(
                self.passport_and_poa_name)
            if passport_and_poa_found:
                return self.update_self_with_existing_documents(
                    'passport_and_poa')
            else:
                self.update_self_with_new_documents('passport_and_poa')

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('vat_num')
    def onchange_vat_num(self) :
        if self.vat_num:
            vat_num_found = self.check_file_dublicate(self.vat_num_name)
            if vat_num_found:
                return self.update_self_with_existing_documents('vat_num')
            else:
                self.update_self_with_new_documents('vat_num')

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('visa_and_poa')
    def onchange_visa_and_poa(self) :
        if self.visa_and_poa:
            visa_and_poa_found = self.check_file_dublicate(
                self.visa_and_poa_name)
            if visa_and_poa_found:
                return self.update_self_with_existing_documents('visa_and_poa')
            else:
                self.update_self_with_new_documents('visa_and_poa')

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('operating_address_uae')
    def onchange_operating_address_uae(self) :
        if self.operating_address_uae:
            operating_address_uae_found = self.check_file_dublicate(
                self.operating_address_uae_name)
            if operating_address_uae_found:
                return self.update_self_with_existing_documents(
                    'operating_address_uae')
            else:
                self.update_self_with_new_documents('operating_address_uae')

    # File Upload Onchange function to check if file is already uploaded
    @api.onchange('trade_license')
    def onchange_trade_license(self) :
        if self.trade_license:
            trade_license_found = self.check_file_dublicate(
                self.trade_license_name)
            if trade_license_found:
                return self.update_self_with_existing_documents(
                    'trade_license')
            else:
                self.update_self_with_new_documents('trade_license')

    # Function to Check Dubicate File is uploaded or not
    def check_file_dublicate(self, file = False):
        new_file_list = self.get_new_file_list(file)
        if file in new_file_list:
            return True
        return False

    # Function to get Updated File List to check dublicate file uploaded
    def get_new_file_list(self, file_name = False):
        file_list = [self.emirates_id_card_name, self.passport_and_poa_name,
                     self.vat_num_name, self.visa_and_poa_name,
                     self.operating_address_uae_name, self.trade_license_name]
        if file_name:
            new_file_list = copy.copy(file_list)
            new_file_list.remove(file_name)
            return new_file_list

    # function to update the vals on change or upload the documents if exist
    def update_self_with_existing_documents(self, file = False):
        if file:
            vals = {
                file : '',
                file + '_name' : '',
            }
            self.update(vals)
            return {'warning' : {
                'title' : _('Duplicate File Found!'),
                'message' : _("Dublicate File Uploaded, "
                            "Or File is already Uploaded in other Files.")
                }
            }
        else:
            raise Warning(_("No File Selected"))

    # function to update the vals on change or upload the documents if new
    def update_self_with_new_documents(self, file = False) :
        if file :
            vals = {
                file + '_rejected' : False,
                file + '_rejected_state' : 'updated',
            }
            self.update(vals)
        else :
            raise Warning(_("No File Selected"))

    # Function called when Client Request is to be Sent for Approval
    @api.multi
    def action_pending_approval(self) :
        if self.emirates_id_card_rejected or self.passport_and_poa_rejected \
                or self.vat_num_rejected or self.visa_and_poa_rejected or \
                self.operating_address_uae_rejected or \
                self.trade_license_rejected:
            raise Warning(_("Some Documents are still not Uploaded. "
                            "You cannot Proceed Ahead without "
                            "the Uploading the Documents"))

        template = self.env.ref(
            'saas_portal_enhancement.action_send_for_approval')
        if template:
            self.send_user_info_mail(template)
            return self.write({'state' : 'pending_approval'})
        else:
            raise Warning(_("No Mail Template Found For Approval"))

    # Function called when Client Documents are not uploaded
    @api.multi
    def action_document_pending(self):
        if self.emirates_id_card_rejected or self.passport_and_poa_rejected \
                or self.vat_num_rejected or self.visa_and_poa_rejected or \
                self.operating_address_uae_rejected or \
                self.trade_license_rejected :
            template = self.env.ref(
                'saas_portal_enhancement.action_client_document_pending')
            if template:
                self.send_user_info_mail(template)
                return self.write({'state': 'document_pending'})
            else :
                raise Warning(_("No Mail Template Found For Document Pending"))
        else:
            raise Warning(_("Documents are uploaded. Please Send it for "
                            "Approval Ahead."))

    # Function called when client Request is Accepted and Approved
    @api.multi
    def action_confirm_client(self):

        try:
            new_client_id = False
            res_partner_bank_vals = {}
            res_partner_bank_obj = self.env['res.partner.bank']
            mail_server_obj = self.env['ir.mail_server']
            res_company_obj = self.env['res.company']
            clients_obj = self.env['saas_portal.client']
            ProductUOM = self.env['product.uom']

            # for country and state to be created in client db
            country_name = self.country_id.name
            country_code = self.country_id.code
            # state_name = self.state_id.name
            # state_code = self.state_id.code

            mail_server_rec = mail_server_obj.search([], limit = 1)
            base_company = res_company_obj.sudo().search([], limit = 1)
            self.check_outgoing_mail()

            if self.plan_id.plan_subscription_ids:
                pass
            else :
                raise Warning(_('Sorry!!, Client will not be confirmed as no '
                                'Subscription is defined in the Plan '
                                'Subscription Page.'))

            res_partner_bank_obj = self.env['res.partner.bank']
            partner_iban_exist = res_partner_bank_obj.search(
                [('acc_number', '=', self.client_bank_acc),
                 ('iban', '=', self.client_bank_iban),
                 ('partner_id', '=', self.client_id.partner_id.id)],
                limit = 1)

            other_partner_iban_exist = res_partner_bank_obj.search(
                [('acc_number', '=', self.client_bank_acc),
                 ('iban', '=', self.client_bank_iban),
                 ('partner_id', '!=', self.client_id.partner_id.id)],
                limit = 1)

            if other_partner_iban_exist:
                raise Warning(_("Bank Account no or IBAN already exist. "
                                "Please verify it again."))

            # Create his/her bank account detail and link to its partner
            if not (partner_iban_exist or other_partner_iban_exist):
                res_partner_bank_vals.update({
                    'bank_id' : self.client_bank_id.id,
                    'acc_number' : self.client_bank_acc,
                    'partner_id' : self.client_id.partner_id.id,
                    'iban': self.client_bank_iban,
                })

                res_partner_bank_obj.sudo().create(res_partner_bank_vals)

            client_rec = clients_obj.sudo().search([('partner_id','=',self.client_id.partner_id.id),
                                                    ('name','=',self.database),
                                                    ('state','=','draft')])

            # if alread the client is created by process stop due to server
            # disconnection or other sevrer related things then this will
            # delete the existing db and create another one
            if client_rec:
                client_rec._delete_database_server(force_delete=True)

            # ====== Keep this code for future use =================
            # if client_rec:
            #     new_client_id = self.plan_id.create_new_database(
            #         dbname = self.database,
            #         client_id = client_rec.client_id,
            #         partner_id = self.client_id.partner_id.id,
            #         user_id = self.client_id.id,
            #         notify_user = True,
            #         trial = False,
            #     )

            # Create New Databse with Subscription plan recordset
            trial = False
            if self.plan_type == 'trial':
                trial = True
            new_client_id = self.plan_id.create_new_database(
                dbname = self.database,
                partner_id = self.client_id.partner_id.id,
                user_id = self.client_id.id,
                notify_user = True,
                trial = trial,
            )

            new_client_rec = self.env['saas_portal.client'].browse(
                    new_client_id['id'])
            vals = {
                'plan_price': self.plan_price,
                'sub_period': self.sub_period,
                'plan_type': self.plan_type,
                'merchant_id': self.merchant_id.id,
                'store_type': self.store_type,
                'req_no': self.request_no
                # 'store_id' : self.store_id.id,
            }
            new_client_rec.write(vals)

            line_dict = []
            analytic_account = self.env['account.analytic.account']
            account_invoice = self.env['account.invoice']

            ana_vals = {}
            if self.client_id.partner_id:
                ana_vals.update({'partner_id': self.client_id.partner_id.id,
                                 'name': 'Subscription for ' +
                                         self.client_id.partner_id.name,
                                 'recurring_rule_type' :
                                     self.plan_id.sub_period,
                                 'recurring_invoices': 'True',
                                 'client_id' : new_client_rec.id
                                 })

                quantity = 1
                if self.num_of_outlets > 0:
                    quantity = self.num_of_outlets

                for data in self.plan_id.plan_subscription_ids:
                    ana_vals_line = {}
                    ana_vals_line.update({
                        'product_id' : data.product_id.id,
                        'uom_id': data.product_id.uom_id.id,
                        'name' : data.saas_prod_desc or data.product_id.name,
                        'price_unit' : data.subscription_price,
                        'quantity': (data.no_of_users * quantity) or 1})
                    line_dict.append((0, 0, ana_vals_line))
                    ana_vals.update({'recurring_invoice_line_ids': line_dict})
                analytic_id = analytic_account.create(ana_vals)
                analytic_id.recurring_create_invoice()
                invoices = account_invoice.search([('contract_id','=',
                                                    analytic_id.id)])
                invoices.action_invoice_open()
                new_client_rec.write({'subscription_id': analytic_id.id })

            res_user_vals = {
                'name' : self.client_id.name,
                'login' : self.client_id.login,
            }

            res_partner_vals = {
                'email' : self.client_id.login,
                'website': self.company_website,
                'vat' : self.vat,
                'mobile' : self.contact_no,
                'phone': self.landline_no,
                'city': self.city,
                'street' : self.street1,
                'street2' : self.street2,
                'state_id': self.state_id.id or ''
                # 'zip' : self.zip,
            }

            # Host entry is done for the ip address and database name
            hosts = Hosts(path = '/etc/hosts')
            new_entry = HostsEntry(entry_type = 'ipv4', address = '127.0.0.1',
                                   names = [self.database])
            hosts.add([new_entry])
            hosts.write()

            # Cursor is being created of the new database created for the
            # User so that a reset password mail can be send to that user
            # of his database only
            new_cr = db_connect(self.database).cursor()
            old_vals = {'smtp_host' : 'localhost', 'smtp_port' : 25,
                        'smtp_encryption' : 'none', 'smtp_user' : '',
                        'smtp_pass' : ''}

            # Outgoing mail server to be set in the users database as we
            # need to send the mail from users database
            new_vals = {'name' : mail_server_rec.name,
                        'sequence' : mail_server_rec.sequence,
                        'smtp_host' : mail_server_rec.smtp_host,
                        'smtp_port' : mail_server_rec.smtp_port,
                        'smtp_encryption' : mail_server_rec.smtp_encryption,
                        'smtp_user' : mail_server_rec.smtp_user,
                        'smtp_pass' : mail_server_rec.smtp_pass}

            # Environment variable for the new db created by user
            new_env = Environment(new_cr, SUPERUSER_ID, {})
            # Get country, state and updated vals
            # country_rec, state_rec, res_partner_vals = \
            #     self.get_country_state_rec(new_env, country_name, country_code,
            #                                state_name, state_code,
            #                                res_partner_vals)
            country_rec, res_partner_vals = \
                self.get_country_state_rec(new_env, country_name, country_code,
                                           res_partner_vals)


            local_mail = new_env['ir.mail_server'].browse([1])
            # update the existing default outgoing mail server with main portal
            # outgoing mail server config
            local_mail.write(new_vals)

            # Base company vals to send base company email info in \
            # reset password mail template
            base_company_user_vals = {
                'logo' : base_company.logo,
                'name' : base_company.name,
                'rml_header1' : base_company.rml_header1,
                'website' : base_company.website,
                'phone' : base_company.phone,
                'email' : base_company.email,
            }

            # New user company name given by user at time of registration
            new_user_company_vals = {
                'logo' : '',
                'name' : self.company,
                'rml_header1' : self.company,
                'website' : self.company_website,
                'mobile' : self.contact_no,
                'phone':self.landline_no,
                'email' : self.client_id.partner_id.email,
                'vat' : self.vat,
                'country_id': country_rec.id,
            }

            # finds the company in user database
            new_user_company = new_env['res.company'].search([], limit = 1)
            # update the existing default company with the base company details
            new_user_company.write(base_company_user_vals)
            ir_config_obj = self.env['ir.config_parameter']
            client_url = new_env['ir.config_parameter'].get_param(
                'web.base.url')

            auth_vals = {
                'name' : 'Auth Provider for ' + self.client_id.name,
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

            self.client_id.write({
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
                [('login', '=', self.client_id.partner_id.email)], limit = 1)
            new_res_partner = new_user.partner_id
            new_user.write(res_user_vals)
            new_res_partner.write(res_partner_vals)

            # Reset password action is called to send mail to the user
            new_user.action_reset_password_custom()
            new_cr.commit()
            # again replaces the old outgoing mail server in user db
            local_mail.write(old_vals)

            # again replace the company to the users company define
            new_user_company.write(new_user_company_vals)

            if self.store_type == 'multi':
                if self.num_of_outlets >= 0:
                    new_user_company.write({'store_type': self.store_type,
                                            'number_of_outlets': self.num_of_outlets})
                    group_multi_company = new_env.ref('base.group_multi_company', False)
                    group_multi_company.write({'users': [(4, new_user.id),
                                                         (4,1)]})
            elif self.store_type == 'single':
                new_user_company.write({'store_type': self.store_type,
                                        'number_of_outlets': self.num_of_outlets})

            group_store_master = new_env.ref(
                'mint_client_multi_store.saas_store_manager')
            group_store_master.write({'users' :  [(4, new_user.id)]})
            new_cr.commit()
            new_cr.close()

            return self.write({'state' : 'confirmed'})
        except Exception as e :
            raise UserError(_("Something Went Wrong while Creating the "
                              "Database. Instead We Got:\n%s") % ustr(e))

    # To get the country and state recordset or else create new and update vals
    # def get_country_state_rec(self, new_env = None, country_name = None,
    #                           country_code = None, state_name = None,
    #                           state_code = None, res_partner_vals = None):

    def get_country_state_rec(self, new_env = None, country_name = None,
                              country_code = None, res_partner_vals = None) :

        if new_env :
            country_obj = new_env['res.country']
            # state_obj = new_env['res.country.state']
        else :
            country_obj = self.env['res.country']
            # state_obj = self.env['res.country.state']

        # Fetch Country Data
        country_rec = country_obj.sudo().search(
            [('name', '=', country_name), ('code', '=', country_code)])
        if country_rec :
            for country_rec in country_rec :
                res_partner_vals.update({'country_id' : country_rec.id})
        else :
            country_rec = country_obj.sudo().create({
                'name' : country_name,
                'code' : country_code,
            })
            res_partner_vals.update({'country_id' : country_rec.id})

        # ====== Keep this code for future use ================
        # # Fetch State Data
        # state_rec = state_obj.sudo().search(
        #     [('code', '=', state_code),
        #      ('country_id', '=', country_rec.id)])
        #
        # if state_rec :
        #     for state_rec in state_rec :
        #         if state_rec.country_id.name == country_rec.name and \
        #                         state_rec.code == state_code and \
        #                         state_rec.country_id.code == country_rec.code:
        #             res_partner_vals.update({'state_id' : state_rec.id})
        #         else :
        #             state_rec.sudo().write({'country_id' : country_rec.id})
        #             res_partner_vals.update({'state_id' : state_rec.id})
        # else :
        #     state_rec = state_obj.sudo().create({
        #         'name' : state_name,
        #         'code' : state_code,
        #         'country_id' : country_rec.id,
        #     })
        #     res_partner_vals.update({'state_id' : state_rec.id})
        # return country_rec, state_rec, res_partner_vals
        return country_rec, res_partner_vals

    # Function called by other functions to check that outgoing mail is
    # configured or not
    @api.multi
    def check_outgoing_mail(self):
        mail_server_obj = self.env['ir.mail_server']
        mail_server_rec = mail_server_obj.search([], limit = 1)

        if mail_server_rec:
            for server in mail_server_rec:
                smtp = False
                try :
                    smtp = mail_server_obj.connect(
                        server.smtp_host,
                        server.smtp_port,
                        user = server.smtp_user,
                        password = server.smtp_pass,
                        encryption = server.smtp_encryption,
                        smtp_debug = server.smtp_debug)
                except Exception as e :
                    raise UserError(_("Outgoing Mail Server Not configured "
                                      "Properly. "
                                      "Connection Test Failed! Here is what "
                                      "we got instead:\n %s") % ustr(e))
                finally :
                    try :
                        if smtp :
                            smtp.quit()
                    except Exception :
                        # ignored, just a consequence of the previous exception
                        pass
            pass

            return True
        else:
            raise UserError(_("Outgoing Mail Server Not configured "))

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
    def get_user_email_rec(self, login = False):
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

        return user_exist,new_client_exist

    # Function to check if database written in new client request exist in
    # client database or in pending state in new client request or not
    def get_database_rec(self, database = False):
        # objects variables
        client_database_obj = self.env['saas_portal.client']
        res_new_client_obj = self.env['saas_portal.new.client']

        user_db_exist = client_database_obj.sudo().search(
            ['|','|',('name', '=', database),
             ('name', '=', 'http://'+database),
             ('name', '=', 'https://'+database)], limit = 1)

        new_client_db_exist = res_new_client_obj.sudo().search(
            ['|','|',('database', '=', database),
             ('database', '=', 'http://' + database),
             ('database', '=', 'https://' + database)
             ], limit = 1)

        return user_db_exist, new_client_db_exist

    # Wordpress registration page create method to create the database and
    # the new client request record that will be created when user click on
    # submit button on online registration form.....
    @api.model
    def wp_create(self, vals=False) :
        _logger.warning("Values Received in the registration ------------'%s'",vals)
        if not vals:
            _logger.warning("Values Not Received in the registration -------------'%s'",vals)
            blank_vals = {}
            error = _("ERROR (No Value Received): Something Went Wrong please "
                      "try agian later!")
            blank_vals.update({
                'error' : error,
            })
            _logger.warning("Bank Values Received in the registration:::'%s'",blank_vals)
            return json.dumps(blank_vals)

        saas_new_client_vals = {}
        error_email = False
        error_domain = False
        error_plan = False
        error_user_iban = False
        error_user_acc = False

        # objects variables
        res_user_obj = self.env['res.users']
        plan_obj = self.env['saas_portal.plan']
        mail_server_obj = self.env['ir.mail_server']
        client_database_obj = self.env['saas_portal.client']
        res_company_obj = self.env['res.company']
        res_partner_bank_obj = self.env['res.partner.bank']

        # Params values in thier variable
        name = (vals.get('full_name', False)).title().strip()
        login = vals.get('email', False)
        street1 = vals.get('street1')
        street2 = vals.get('street2')
        city = vals.get('city')
        country_code = vals.get('country')
        contact_no = vals.get('contact_no')
        landline_no = vals.get('landline_no')
        plan_id = vals.get('plan_id')
        company = (vals.get('company_name')).title()
        company_website = vals.get('company_website')
        business_type_ids = map(int, vals.get('business_type'))
        database = vals.get('base_saas_domain_name') + '.' + \
                   vals.get('base_saas_domain')
        database = database.lower().strip()
        # uid = 1
        plan_type_rec = vals.get('plan_type_rec')
        portal_company = vals.get('portal_company')
        country_name = vals.get('country_name')
        bank_id = vals.get('bank_rec_id')
        account_num = vals.get('account_num')
        bank_iban = vals.get('bank_iban')

        # search method for the requirement values
        plan_rec = plan_obj.sudo().search([('id', '=', plan_id)],
                                          limit = 1)
        user_exist, new_client_exist = self.get_user_email_rec(login)
        user_db_exist, new_client_db_exist = self.get_database_rec(
            database)
        partner_iban_exist = res_partner_bank_obj.search(
            [('iban', '=', bank_iban)], limit = 1)
        partner_account_exist = res_partner_bank_obj.search(
            [('acc_number', '=', account_num)], limit = 1)
        rec = res_user_obj.sudo().search([('login', '=', login)],
                                         limit = 1)
        mail_server_rec = mail_server_obj.sudo().search([], limit = 1)
        base_company = res_company_obj.sudo().search([], limit = 1)
        # bank_rec = self.env['res.bank'].sudo().search([])
        bank_query = """
                select id, name from res_bank """
        self.env.cr.execute(bank_query)
        bank_rec = self._cr.dictfetchall()
        business_rec = self.env['business.type'].sudo().search([])
        business_query = """
                select id, name from business_type """
        self.env.cr.execute(business_query)
        business_rec = self._cr.dictfetchall()

        # vals to return to registration page if any error---
        values_with_error_code = {
            'full_name' : name,
            'street1' : street1,
            'street2' : street2,
            'company_name' : company,
            'company_website' : company_website,
            'plan_id' : plan_id,
            'base_saas_domain_name' : vals.get('base_saas_domain_name').strip(),
            'base_saas_domain' : vals.get('base_saas_domain'),
            'plan_type' : plan_type_rec,
            'portal_company' : portal_company,
            'email' : login,
            'city' : city,
            # 'bank_rec' : bank_rec,
            # 'business_rec' : business_rec,
            'bank_rec' : bank_id,
            'business_rec' : business_type_ids,
        }
        if mail_server_rec :
            for server in mail_server_rec :
                smtp = False
                try :
                    smtp = mail_server_obj.connect(server.smtp_host,
                                                   server.smtp_port,
                                                   user = server.smtp_user,
                                                   password = server.smtp_pass,
                                                   encryption = server.smtp_encryption,
                                                   smtp_debug = server.smtp_debug)
                except Exception as e :
                    error = _("Server Is Temparary Down!, "
                              "Please check after some time")
                    values_with_error_code.update({
                        'error' : error,
                    })
                    return json.dumps(values_with_error_code)
                finally :
                    try :
                        if smtp :
                            smtp.quit()
                    except Exception :
                        # ignored, just a consequence of the previous exception
                        pass
            pass

        if user_exist or new_client_exist or rec :
            error_user = _("User/ Email ID is already registered")
            values_with_error_code.update({
                'error_user' : error_user,
                'error_email': True,
            })
            error_email = True
        if user_db_exist or new_client_db_exist :
            error_db = _("Database Exists")
            values_with_error_code.update({
                'error_db' : error_db,
                'error_domain': True,
            })
            error_domain = True
        if not plan_rec :
            error_plan_rec = _(
                "You have not Selected any Plans. Please select plan.")
            values_with_error_code.update({
                'error_plan_rec' : error_plan_rec,
                'error_plan': True,
            })
            error_plan = True
        if partner_iban_exist:
            error_iban = _("User Bank IBAN no already Exist")
            values_with_error_code.update({
                'error_iban' : error_iban,
                'error_user_iban': True
            })
            error_user_iban = True
        if partner_account_exist:
            error_acc = _("User Bank Account no already Exist")
            values_with_error_code.update({
                'error_acc' : error_acc,
                'error_user_acc': True,
            })
            error_user_acc = True
        if error_email or error_domain or error_plan or \
                error_user_iban or error_user_acc:
            error = _("ERROR")
            values_with_error_code.update({
                'error' : error,
            })
            return json.dumps(values_with_error_code)
        else :
            # try:
            # dictionary value for res.users
            res_user_vals = {
                'name' : name,
                'login' : login,
                'password' : login,
            }

            # Partner vals in self db
            res_partner_vals = {
                'email' : login,
                'mobile' : contact_no,
                'phone' : landline_no,
                'street' : street1,
                'street2' : street2,
                'website' : company_website,
                'city' : city,
            }

            # Get country, state and vals updated
            country_rec, res_partner_vals = \
                self.get_country_state_rec(None, country_name,
                                           country_code,
                                           res_partner_vals)

            # User is created in main Database
            user_id = res_user_obj.sudo().create(res_user_vals)

            # related partner is being search
            res_partner = user_id.partner_id

            # related partner email id is being updated
            res_partner.sudo().write(res_partner_vals)

            # Create New Client and make it in pending state
            saas_new_client_vals.update({
                'database' : database,
                'client_id' : user_id.id,
                'client_email' : user_id.login,
                'state' : 'new',
                'plan_id' : plan_rec.id,
                'contact_no' : contact_no,
                'landline_no' : landline_no,
                'company' : company,
                'company_website' : company_website,
                'business_type_ids' : [(6, 0, business_type_ids)],
                'plan_type' : plan_type_rec,
                'plan_price' : plan_rec.plan_price,
                'sub_period' : plan_rec.sub_period,
                'city' : city,
                'country_id' : country_rec.id,
                'street1' : street1,
                'street2' : street2,
                'client_bank_id' : bank_id,
                'client_bank_acc' : account_num,
                'client_bank_iban' : bank_iban
            })

            self.env['saas_portal.new.client'].sudo().create(
                saas_new_client_vals)
            # Find the e-mail template
            template = self.env.ref(
                'saas_login_registration.action_user_request_registered')
            # Send out the e-mail template to the user
            template.sudo().send_mail(
                user_id.id, force_send = True)
            return 1
