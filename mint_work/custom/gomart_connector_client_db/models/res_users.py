# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
from gomartapi import *
from datetime import datetime
import logging
import re
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    gomart_admin_id = fields.Integer("GoMart Admin ID",
                                     readonly=True,
                                     help="This field will be generated from GoMart API.")
    _ADMIN_TYPE = [
#                     ('1', 'Main Admin'),
                     ('2', 'Super Admin'),
                     ('3', 'General Admin')
                  ]
    admin_type = fields.Selection(selection=_ADMIN_TYPE, string="Admin Type")

    @api.one
    @api.constrains("email")
    def _check_email(self):
        result = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
        if result == None:
            raise exceptions.Warning("Please enter valid Email id")

    @api.multi
    def createStoreAdmin(self):
        _super_admin = 0
        _chain_super_admin = {'2':1, '3':0}
        _gender = {'1':1, '2':2}
        _admin_type = {'2':2, '3':3}
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        auth_token = self.env["auth.oauth.provider"].search([('name', '=', 'SaaS'),
                                                             ('enabled', '=', 'True')], limit=1)

        store_chain_id = 0
        if self.company_id.parent_id:
            store_chain_id = self.company_id.parent_id.id

        try:
            if gomart_server and gomart_server.name: 
                if auth_token and auth_token.client_id:
                    # setStoreAdmin API
                    admin_API = setStoreAdmin(
                                              gomart_server.name,
                                              self.company_id.id,  # erp_store_id
                                              store_chain_id,  # erp_store_chain_id
                                              self.id,  # erp_admin_id
                                              self.name or '',  # erp_admin_name
                                              self.email or  '',  # erp_login
                                              self.email ,  # erp_password
                                              self.email or '',  # erp_email
                                              self.partner_id.mobile or '814079162',  # erp_mobile
                                              self.partner_id.dob or '1989-07-15',  # str(datetime.now().date()),  # erp_dob
                                              _admin_type.get(self.admin_type),  # [1-Main Admin,2-Super Admin,3-General Admin]
                                              _super_admin,  # erp_super_admin
                                              _chain_super_admin.get(self.admin_type),  # erp_chain_super_admin
                                              _gender.get(self.partner_id.gender) or 1,  # erp_gender
                                              auth_token.client_id
                                              )
                    # Log
                    _logger.warning("\n\n\n" + " StoreAdmin API : \n" + " Data : " + str(admin_API.get('data')) + "\n Status : " + str(admin_API.get('status_code')) + "\n json_dump :" + str(admin_API.get('json_dump')))
                    if admin_API.get('status_code') == 200 and admin_API.get('admin_id'):
                            self.write({'gomart_admin_id':admin_API.get('admin_id')})
                    else:
                        msg = "GoMart API setStoreAdmin having invalid status code is %s " % str(admin_API.get('status_code'))
                        _logger.warning(msg)
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            msg = "GoMart API setStoreAdmin is not working or Server down."
            _logger.warning(msg)

        return True
