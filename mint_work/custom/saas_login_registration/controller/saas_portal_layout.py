# -*- coding: utf-8 -*-
import logging
import odoo
import json
import base64

from odoo.sql_db import db_connect
from odoo.http import request
from odoo import http, SUPERUSER_ID
from odoo.api import Environment
from odoo.tools.translate import _
from python_hosts import Hosts, HostsEntry
from odoo.addons.saas_portal.controllers.main import SaasPortal
# from odoo.addons.web.controllers.main import ensure_db

_logger = logging.getLogger(__name__)

class AuthSignupHome_first_user(odoo.addons.web.controllers.main.Home,
                                SaasPortal):

    # This controller will be called from the Server/Industry page from website
    @http.route(['/registration'], type='http', auth='public', website=True)
    def new_database(self, **post):

        uid = request.params.get('uid', '')
        plan_id = request.params.get('plan_id')
        plan_type = request.params.get('plan_type')
        base_saas_domain = self.get_config_parameter('base_saas_domain')
        company = request.env['res.company'].search([], limit=1)
        business_rec = request.env['business.type'].sudo().search([])
        bank_rec  = request.env['res.bank'].sudo().search([])
        values = \
            {
                'plan_id': plan_id,
                'base_saas_domain': base_saas_domain,
                'uid': uid,
                'business_rec': business_rec or '',
                'plan_type': plan_type or '',
                'portal_company': company.name,
                'bank_rec': bank_rec or '',
            }
        return request.render("saas_login_registration.registration_form",
                              values)

    # This function is called from the registration page to create the
    # client db in new registration backend and if trial then it will
    # directly create client instance with the trial period define in the
    # server he has selected.
    @http.route('/process', type='http', auth='public', website=True)
    def web_user_login(self, redirect=None, **kw):
        try:
            saas_new_client_vals = {}
            # objects variables
            res_user_obj = request.env['res.users']
            plan_obj = request.env['saas_portal.plan']
            client_database_obj = request.env['saas_portal.client']
            mail_server_obj = request.env['ir.mail_server']
            res_company_obj = request.env['res.company']
            # res_partner_bank_obj = request.env['res.partner.bank']
            # res_new_client_obj = request.env['saas_portal.new.client']

            # Params values in thier variable
            full_name = (request.params['full_name']).strip()
            login = (request.params['email']).strip()
            street1 = request.params['street1']
            street2 = request.params['street2']
            city = request.params['city']
            country_code = request.params['country']
            # state_code = request.params['state']
            # zip = request.params['zip']
            contact_no = request.params['contact_no']
            landline_no = request.params['landline_no']
            plan_id = request.params['plan_id']
            company = (request.params['company_name']).title()
            company_website = request.params['company_website']
            business_type_ids = \
                [int(rec) for rec in request.httprequest.form.getlist(
                    'business_type')]
            database = request.params['base_saas_domain_name'] + '.' + \
                       request.params['base_saas_domain']
            uid = request.params['uid']
            plan_type_rec = request.params['plan_type_rec']
            portal_company = request.params['portal_company']
            country_name = request.params['country_name']
            # state_name = request.params['state_name']
            bank_id = request.params['bank_rec_id']
            account_num = request.params['account_num']
            bank_iban = request.params['bank_iban']

            # search method for the requirement values
            plan_rec = plan_obj.sudo().search([('id', '=', plan_id)], limit=1)

            # get the rec if email aready exist in db
            user_exist, new_client_exist, partner_exist = self.get_user_email_rec(
                login)

            # get the rec if domain name already exist in db
            database_exist, new_client_db_exist = self.get_database_rec(database)

            # get the bank details if user account no or iban no already exist
            partner_iban_exist = self.get_partner_by_bank(account_num, bank_iban)

            mail_server_rec = mail_server_obj.sudo().search([], limit=1)
            base_company = res_company_obj.sudo().search([], limit=1)
            bank_rec = request.env['res.bank'].sudo().search([])
            business_rec = request.env['business.type'].sudo().search([])
            # vals to return to registration page if any error---
            values_with_error_code = {
                'full_name': full_name,
                'street1': street1,
                'street2' : street2,
                'company_name': company,
                'company_website':company_website,
                'plan_id': plan_id,
                'base_saas_domain_name': request.params['base_saas_domain_name'],
                'base_saas_domain': request.params['base_saas_domain'],
                'uid': uid,
                'plan_type': plan_type_rec,
                'portal_company': portal_company,
                'email': login,
                'city': city,
                # 'zip_code': zip,
                'bank_rec': bank_rec,
                'business_rec': business_rec,
                'bank_iban': bank_iban,
                'account_num': account_num
            }

            if mail_server_rec:
                for server in mail_server_rec:
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
                        return request.render(
                            "saas_login_registration.registration_form",
                            values_with_error_code)
                    finally :
                        try :
                            if smtp :
                                smtp.quit()
                        except Exception :
                            # ignored, just a consequence of the previous exception
                            pass
                pass

            if user_exist or new_client_exist or partner_exist:
                error = _("User/ Email ID is already registered")
                values_with_error_code.update({
                    'error': error,
                })
                return request.render("saas_login_registration.registration_form",
                                      values_with_error_code)
            elif database_exist or new_client_db_exist:
                error = _("Database Exists")
                values_with_error_code.update({
                    'error': error,
                })
                return request.render("saas_login_registration.registration_form",
                                      values_with_error_code)
            elif partner_iban_exist:
                error = _("Your Bank IBAN already exist. Please verify it "
                          "again")
                values_with_error_code.update({
                    'error' : error,
                })
                return request.render(
                    "saas_login_registration.registration_form",
                    values_with_error_code)
            else:
                # dictionary value for res.users
                res_user_vals = {
                    'name': full_name,
                    'login': login,
                    'password': login,
                }

                # Partner vals in self db
                res_partner_vals = {
                    'email' : login,
                    'mobile' : contact_no,
                    'phone': landline_no,
                    'street': street1,
                    'street2': street2,
                    'website':company_website,
                    # 'zip': zip,
                    'city': city,
                }

                # Get country, state and vals updated
                # country_rec, state_rec, res_partner_vals= \
                #     self.get_country_state_rec(None, country_name, country_code,
                #                                state_name, state_code,
                #                                res_partner_vals)

                # Get country, state and vals updated
                country_rec, res_partner_vals = \
                    self.get_country_state_rec(None, country_name,
                                               country_code,
                                               res_partner_vals)

                # User is created in main Database
                user_id = res_user_obj.sudo().create(res_user_vals)

                # ====================================================
                # ====== Dont Remove this Commented Code =============
                # ====================================================
                # user_id.action_clear_access_rights()
                # grp_ids = user_id.groups_id.ids
                # portal_id = request.env.ref('base.group_portal').id
                # if portal_id in grp_ids :
                #     pass
                # else :
                #     grp_ids.append((4, portal_id))
                # user_id.sudo().write({'groups_id' : grp_ids})

                # related partner is being search
                res_partner = user_id.partner_id

                # related partner email id is being updated
                res_partner.sudo().write(res_partner_vals)

                # # Create his/her bank account detail and link to its partner
                # res_partner_bank_vals = {}
                # res_partner_bank_vals.update({
                #     'bank_id' : bank_id,
                #     'acc_number' : account_num,
                #     'partner_id' :res_partner.id,
                # })

                # res_partner_bank_obj.sudo().create(res_partner_bank_vals)

                # Create New Client and make it in pending state
                saas_new_client_vals.update({
                    'database' : database,
                    'client_id' : user_id.id,
                    'client_email': user_id.login,
                    'state' : 'new',
                    'plan_id' : plan_rec.id,
                    'contact_no' : contact_no,
                    'landline_no': landline_no,
                    'company' : company,
                    'company_website': company_website,
                    'business_type_ids': [(6, 0, business_type_ids)],
                    'plan_type' : plan_type_rec,
                    'plan_price' : plan_rec.plan_price,
                    'sub_period' : plan_rec.sub_period,
                    'city' : city,
                    # 'state_id' : state_rec.id,
                    'country_id' : country_rec.id,
                    'street1' : street1,
                    'street2' : street2,
                    # 'zip' : zip,
                    'client_bank_id':bank_id,
                    'client_bank_acc': account_num,
                    'client_bank_iban': bank_iban
                })
                if plan_type_rec == 'subscription':
                    request.env['saas_portal.new.client'].sudo().create(saas_new_client_vals)
                    # Find the e-mail template
                    template = request.env.ref(
                        'saas_login_registration.action_user_request_registered')
                    # Send out the e-mail template to the user
                    template.sudo().send_mail(
                        user_id.id, force_send = True)

                    return request.render(
                        "saas_login_registration.client_create_template")

                if plan_type_rec == 'trial':
                    # Create new entry in Registration Request as Trial client
                    request.env['saas_portal.new.client'].sudo().create(
                        saas_new_client_vals)
                    # Find the e-mail template
                    template = request.env.ref(
                        'saas_login_registration.action_user_request_registered')
                    # Send out the e-mail template to the user
                    template.sudo().send_mail(
                        user_id.id, force_send = True)

                    return request.render(
                        "saas_login_registration.client_create_template")

                #     saas_new_client_vals.update({
                #         'state': 'confirmed'
                #     })
                #     client_rec = client_database_obj.sudo().search(
                #         [('partner_id', '=', res_partner.id),
                #          ('name', '=', database),
                #          ('state', '=', 'draft')],
                #         limit = 1)
                #
                #     if client_rec :
                #         client_rec._delete_database_server(force_delete = True)
                #
                #
                #     request.env['saas_portal.new.client'].sudo().create(
                #         saas_new_client_vals)
                #
                #     # Create New Databse with trial plan recordset
                #     new_client_id = plan_rec.create_new_database(
                #         dbname=database,
                #         partner_id=user_id.partner_id.id,
                #         user_id=user_id.id,
                #         notify_user=True,
                #         trial=True,
                #     )
                #     new_client_rec = request.env['saas_portal.client'].sudo() \
                #         .browse(new_client_id['id'])
                #     if new_client_rec :
                #         vals = {
                #             'plan_price' : plan_rec.plan_price,
                #             'sub_period' : plan_rec.sub_period,
                #             'plan_type' : plan_rec.plan_type,
                #         }
                #         new_client_rec.sudo().write(vals)
                #
                # # Host entry is done for the ip address and database name
                # hosts = Hosts(path='/etc/hosts')
                # new_entry = HostsEntry(entry_type='ipv4', address='127.0.0.1',
                #                        names=[database])
                # hosts.add([new_entry])
                # hosts.write()
                #
                # # Cursor is being created of the new database created for the
                # # User so that a reset password mail can be send to that user
                # # of his database only
                # new_cr = db_connect(database).cursor()
                # old_vals = {'smtp_host': 'localhost', 'smtp_port': 25,
                #             'smtp_encryption': 'none', 'smtp_user': '',
                #             'smtp_pass': ''}
                #
                # # Outgoing mail server to be set in the users database as we
                # # need to send the mail from users database
                # new_vals = {'name': mail_server_rec.name,
                #             'sequence': mail_server_rec.sequence,
                #             'smtp_host': mail_server_rec.smtp_host,
                #             'smtp_port': mail_server_rec.smtp_port,
                #             'smtp_encryption': mail_server_rec.smtp_encryption,
                #             'smtp_user': mail_server_rec.smtp_user,
                #             'smtp_pass': mail_server_rec.smtp_pass}
                #
                # # Environment variable for the new db created by user
                # new_env = Environment(new_cr, SUPERUSER_ID, {})
                #
                # #  partner vals in new db
                # new_res_partner_vals = {
                #     'email' : login,
                #     'mobile' : contact_no,
                #     'phone': landline_no,
                #     'street' : street1,
                #     'street2' : street2,
                #     # 'zip' : zip,
                #     'city' : city,
                #     'website':company_website,
                # }
                # # country_rec, state_rec, new_res_partner_vals = \
                # #     self.get_country_state_rec(new_env, country_name, country_code,
                # #                                state_name, state_code,
                # #                                new_res_partner_vals)
                #
                # country_rec, new_res_partner_vals = \
                #     self.get_country_state_rec(new_env, country_name,
                #                                country_code,
                #                                new_res_partner_vals)
                #
                # local_mail = new_env['ir.mail_server'].browse([1])
                # # update the existing default outgoing mail server with main portal
                # # outgoing mail server config
                # local_mail.write(new_vals)
                #
                # # Base company vals to send base company email info in \
                # # reset password mail template
                # base_company_user_vals = {
                #     'logo': base_company.logo,
                #     'name': base_company.name,
                #     'rml_header1': base_company.rml_header1,
                #     'website': base_company.website,
                #     'phone': base_company.phone,
                #     'email': base_company.email,
                # }
                #
                # # New user company name given by user at time of registration
                # new_user_company_vals = {
                #     'logo': '',
                #     'name': company,
                #     'rml_header1': company,
                #     'website': company_website,
                #     'phone': '',
                #     'email': 'info@yourcompany.com',
                #     'country_id' : country_rec.id,
                # }
                #
                # # finds the company in user database
                # new_user_company = new_env['res.company'].sudo().search([],
                #                                                         limit=1)
                # # update the existing default company with the base company details
                # new_user_company.write(base_company_user_vals)
                # ir_config_obj = request.env['ir.config_parameter']
                # client_url = new_env['ir.config_parameter'].get_param(
                #     'web.base.url')
                #
                # auth_vals = {
                #     'name': 'Auth Provider for ' + full_name,
                #     'client_id' : new_env['ir.config_parameter'].get_param(
                #         'database.uuid'),
                #     'enabled' : True,
                #     'body' : 'Login with Auth provider',
                #     'auth_endpoint'  : client_url + '/oauth2/auth',
                #     'scope' : 'userinfo',
                #     'validation_endpoint' : client_url + '/oauth2/tokeninfo'
                # }
                # portal_provider = request.env['auth.oauth.provider'].sudo().create(
                #     auth_vals)
                #
                # # new_env['res.users'].search([('login','=',login)])
                #
                # user_id.sudo().write({
                #     'oauth_provider_id': portal_provider.id,
                #     'oauth_uid' : 1
                # })
                #
                # new_env['ir.config_parameter'].set_param('portal.database',
                #                                          request.env.cr.dbname)
                # new_env['ir.config_parameter'].set_param('portal.url',
                #                                          ir_config_obj.get_param(
                #                                              'web.base.url'))
                # new_env['ir.config_parameter'].set_param('portal.provider',
                #                                          portal_provider.id)
                # new_cr.commit()
                #
                # # Search for the user in the new database for updating \
                # # his related partner fields
                # new_user = new_env['res.users'].search([('login', '=', login)],
                #                                        limit=1)
                # new_res_partner = new_user.partner_id
                # new_user.write(res_user_vals)
                # new_res_partner.write(new_res_partner_vals)
                #
                # # Reset password action is called to send mail to the user
                # # new_user.action_reset_password()
                # new_user.action_reset_password_custom()
                # new_cr.commit()
                # # again replaces the old outgoing mail server in user db
                # local_mail.write(old_vals)
                #
                # # again replace the company to the users company define
                # new_user_company.write(new_user_company_vals)
                #
                # new_cr.commit()
                # new_cr.close()
                # return request.render(
                #     "saas_login_registration.password_reset_msg_template")
        except Exception as e:
            return request.render(
                "saas_login_registration.custom_error_handling")

    # To get the country and state recordset or else create new and update vals
    # def get_country_state_rec(self, new_env = None, country_name = None,
    #                           country_code = None, state_name = None,
    #                           state_code = None, res_partner_vals = None):

    def get_country_state_rec(self, new_env = None, country_name = None,
                              country_code = None, res_partner_vals = None) :

        if new_env:
            country_obj = new_env['res.country']
            # state_obj = new_env['res.country.state']
        else:
            country_obj = request.env['res.country']
            # state_obj = request.env['res.country.state']

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

        # # Fetch State Data
        # state_rec = state_obj.sudo().search(
        #     [('code', '=', state_code),
        #      ('country_id', '=', country_rec.id)])
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


    # Get the Email ID from res.partner, client
    @http.route(['/get_email_rec'], type='http', auth='public', website=True)
    def check_user_email_exist(self, **kwargs):
        params = dict(request.params)
        login = params.get('email')
        response = {}
        user_exist, new_client_exist, partner_exist = self.get_user_email_rec(login)

        if user_exist or new_client_exist or partner_exist:
            response.update({'error' : 'Email Already Exists. Please choose '
                                       'another Email ID.'})
            # response.update({'valid':False})
            return json.dumps(response)
        else:
            response.update({'available': True})
            # response.update({'valid' : True})
            return json.dumps(response)

    # Function to check if user or client or partner exist with this email id
    def get_user_email_rec(self, login = None):
        # objects variables
        client_database_obj = request.env['saas_portal.client']
        res_partner_obj = request.env['res.partner']
        res_new_client_obj = request.env['saas_portal.new.client']

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

        partner_exist = res_partner_obj.sudo().search([('email', '=', login)],
                                                      limit = 1)

        return user_exist,new_client_exist,partner_exist

        # ===================================================================
        # =========== Code is commented as it not required temp =============
        # =========== Donot remove this code. may be required later =========
        # ===================================================================
        # # Get the Bank Rec for the IBN Number associate with it
        # @http.route(['/get_bank_rec'], type = 'http', auth = 'public',
        #             website = True)
        # def get_bank_iban_details(self, **kwargs) :
        #     params = dict(request.params)
        #     bank_id = params.get('bank_rec_id')
        #     response = {}
        #     reb_bank_obj = request.env['res.bank']
        #     res_bank_rec = reb_bank_obj.sudo().browse(int(bank_id))
        #     if res_bank_rec:
        #         res_bank_iban_num = res_bank_rec.bic
        #         response.update({'bank_iban' : res_bank_iban_num})
        #         return json.dumps(response)
        #     else :
        #         response.update(
        #             {'error' : 'Bank IBAN Number does not Exist.'})
        #         return json.dumps(response)


    # To get the Plan Feature List and display it on website
    @http.route(['/get_server_term_conditions'], type = 'http',
                auth = "public", website = True)
    def server_term_conditions(self, **post) :
        plan_id = request.params['id']
        plan = request.env['saas_portal.plan'].sudo().search(
            [('id', '=', plan_id)])
        terms_condition = plan.server_id.terms_conditons

        if len(terms_condition) == 0 :
            server_term_condition = 'No Terms and Conditions Define.'
        else:
            server_term_condition = terms_condition

        return json.dumps(server_term_condition)

    # Get the Domain name from new request or client id exist
    @http.route(['/get_domain_rec'], type = 'http', auth = 'public',
                website = True)
    def check_domain_exist(self, **kwargs) :
        params = dict(request.params)
        domain = str(params.get('base_saas_domain_name'))
        server = str(params.get('base_saas_domain'))
        domain = domain + '.' + server
        response = {}
        database_exist, new_client_db_exist = self.get_database_rec(domain)

        if database_exist or new_client_db_exist :
            response.update(
                {'error' : 'Domain Name already Exists. Please give '
                           'another Domain name.'})
            return json.dumps(response)
        else :
            response.update({'available' : True})
            return json.dumps(response)

    # Get the rec if domain (database) exist in new request or
    # saas_portal.client
    def get_database_rec(self, database=False):
        if database:
            client_database_obj = request.env['saas_portal.client']
            res_new_client_obj = request.env['saas_portal.new.client']
            database_exist = client_database_obj.sudo().search(
                ['|', '|', ('name', '=', database),
                 ('name', '=', 'http://' + database),
                 ('name', '=', 'https://' + database)],
                limit = 1)
            new_client_db_exist = res_new_client_obj.sudo().search(
                ['|', '|', ('database', '=', database),
                 ('database', '=', 'http://' + database),
                 ('database', '=', 'https://' + database)], limit = 1)

            return database_exist, new_client_db_exist
        else:
            return False, False

    # Get the partner rec if iban or acc no exist
    def get_partner_by_bank(self, account_num = False, bank_iban = False):
        if account_num and bank_iban:
            res_partner_bank_obj = request.env['res.partner.bank']
            partner_iban_exist = res_partner_bank_obj.sudo().search(
                ['|', ('acc_number', '=', account_num),
                 ('iban', '=', bank_iban)], limit = 1)
            return partner_iban_exist
        else:
            return False

    # ===================================================================
    # =========== Code is commented as it not required temp =============
    # =========== Donot remove this code. may be required later =========
    # ===================================================================
    # # Get the Bank Rec for the IBN Number associate with it
    # @http.route(['/get_bank_rec'], type = 'http', auth = 'public',
    #             website = True)
    # def get_bank_iban_details(self, **kwargs) :
    #     params = dict(request.params)
    #     bank_id = params.get('bank_rec_id')
    #     response = {}
    #     reb_bank_obj = request.env['res.bank']
    #     res_bank_rec = reb_bank_obj.sudo().browse(int(bank_id))
    #     if res_bank_rec:
    #         res_bank_iban_num = res_bank_rec.bic
    #         response.update({'bank_iban' : res_bank_iban_num})
    #         return json.dumps(response)
    #     else :
    #         response.update(
    #             {'error' : 'Bank IBAN Number does not Exist.'})
    #         return json.dumps(response)
