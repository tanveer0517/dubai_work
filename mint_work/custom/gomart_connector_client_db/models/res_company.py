##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
from gomartapi import *
import logging
import re
from datetime import datetime

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    gomart_store_id = fields.Integer("GoMart Store ID",
                                     readonly="True",
                                     help="This field will be generated by GoMart.")
    gomart_store_chain_id = fields.Integer("GoMart Store Chain ID",
                                           readonly="True",
                                           help="This field will be generated by GoMart.")
    _MERCHANT_TYPE = [
                     ('1', 'Grocery'),
                     ('2', 'Restaurant')
                  ]
    mobile = fields.Char("Mobile")
    commissions = fields.Float(string="Commission", help="Commission")
    type_merchant = fields.Selection([('1', 'Grocery'), ('2', 'Restaurant')], default='1', string="Merchant Type")
    store_type = fields.Boolean("Primary store", default="True")
    chain_flag = fields.Boolean("Chain flag", default="False")
    location_id = fields.Many2one("city.area", "Area")
    is_active = fields.Boolean("Is Active", default="True")
    # Delivery Location 
    gomart_delivery_region_id = fields.Integer("GoMart Delivery Region ID", readonly="True", help="This field is generated from the GoMart.")
    delivery_location = fields.Many2one("city.area", string="Delivery Location")
    city_id = fields.Many2one("city.city", string="City")

    @api.one
    @api.constrains("email")
    def _check_email(self):
        result = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
        if result == None:
            raise exceptions.Warning("Please enter valid Email id")

    @api.multi
    def Update_store_details(self, rec):
        _active = { True:1, False:2}
        chain_flag = {True:1, False:0}
        primary_store = {True:1, False:0}  
        _floor_plan = 0
        _store_rating = 5
        _merchant_type = { '1':1, '2':2}
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        auth_token = self.env["auth.oauth.provider"].search([('name', '=', 'SaaS'),
                                                             ('enabled', '=', 'True')], limit=1)

        store_chain_id = 0
        if self.parent_id:
            store_chain_id = self.parent_id.id

        try:
            if gomart_server and gomart_server.name: 
                if auth_token and auth_token.client_id:
                    # Longitude  and Latitude
                    long_lat = LocationLogiLati(str(self.location_id.city_id.name) + ',' 
                                                +str(self.location_id.city_id.state_id.name) + ',' 
                                                +str(self.country_id.name))
        
                    StoreDetail_API = setStoreDetail(
                                                    gomart_server.name,
                                                    self.id,
                                                    store_chain_id,
                                                    self.location_id.city_id.master_db_city_id or self.location_id.city_id.id,  # erp_city_id
                                                    self.location_id.city_id.state_id.master_db_state_id or self.location_id.city_id.state_id.id,  # erp_state_id
                                                    self.location_id.master_db_area_id or self.location_id.id,  # erp_location_id
                                                    self.name or '',
                                                    primary_store.get(self.store_type),
                                                    str(self.street) + ',' + str(self.street2) or ',',
                                                    long_lat.get("lat"),
                                                    long_lat.get("long"),
                                                    self.email,
                                                    self.website,
                                                    self.phone,
                                                    self.mobile,
                                                    self.rml_header1,  # erp_about
                                                    _floor_plan,  # "Not Used" erp_floor_plan_flag [1-Enabled,2-Not Enabled ] 
                                                    _store_rating,  # erp_store_rating 
                                                    _active.get(self.is_active),  # active [1- Active, 0- Inactive]
                                                    auth_token.client_id
                                                    )
                    # Log
                    _logger.warning("\n\n\n" + " Store Details API : \n\n " + " Data : " + str(StoreDetail_API.get('data')) + "\n\n Status : " + str(StoreDetail_API.get('status_code')) + "\n\n json_dump :" + str(StoreDetail_API.get('json_dump')))
                    if StoreDetail_API.get('status_code') == 200 and StoreDetail_API.get('store_chain_id'):
                        self.write({'gomart_store_chain_id':StoreDetail_API.get('store_chain_id')})
                    else:
                        msg = "GoMart APi setStoreDetail is not working."
                        _logger.warning(msg)
                else:
                    _logger.warning("SaaS token does not exist or something went wrong.")
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            _logger.warning("Server Down or SetStore GoMart API is not working.")
        return True

    @api.multi
    def Create_store(self):
        _active = { True:1, False:2}
        chain_flag = {True:1, False:0}
        primary_store = {True:1, False:0}  
        _floor_plan = 0
        _store_rating = 5
        _merchant_type = { '1':1, '2':2}
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        auth_token = self.env["auth.oauth.provider"].search([('name', '=', 'SaaS'), ('enabled', '=', 'True')], limit=1)

        store_chain_id = 0
        if self.parent_id:
            store_chain_id = self.parent_id.id

        # Longitude  and Latitude
        long_lat = LocationLogiLati(str(self.location_id.city_id.name) + ',' 
                                    +str(self.location_id.city_id.state_id.name) + ',' 
                                    +str(self.country_id.name))

        try:
            if gomart_server and gomart_server.name: 
                if auth_token and auth_token.client_id:
                    store_API = setStore(
                                    gomart_server.name,
                                    self.id,  # erp_store_id
                                    self.name ,  # erp_store_name
                                    store_chain_id,  # erp_store_chain_id
                                    self.location_id.city_id.master_db_city_id or self.location_id.city_id.id,  # erp_city_id
                                    self.location_id.master_db_area_id or self.location_id.id,  # erp_location_id
                                    self.location_id.city_id.state_id.master_db_state_id or self.location_id.city_id.state_id.id,  # erp_state_id
                                    self.rml_header1,  # erp_about
                                    _merchant_type.get(self.type_merchant),  # erp_merchant_type
                                    self.commissions,  # erp_commisssion
                                    str(datetime.now().date()),  # erp_start_date 
                                    chain_flag.get(self.chain_flag),  # erp_chain_flag  [1-Chain,0-Not Chain]
                                    primary_store.get(self.store_type),  # erp_primary_store [1-Primary Store,0-Non Primary Store]
                                    str(self.street) + ',' + str(self.street2) or '',  # erp_address
                                    self.email,
                                    long_lat.get("lat"),
                                    long_lat.get("long"),
                                    self.website,
                                    self.phone,
                                    self.mobile,
                                    _floor_plan,  # "Not Used" erp_floor_plan_flag [1-Enabled,2-Not Enabled ] 
                                    _store_rating,  # erp_store_rating 
                                    _active.get(self.is_active),  # active [1- Active, 0- Inactive]
                                    auth_token.client_id
                                    )
                    # Log
                    _logger.warning("\n\n\n" + " setStore  API : \n\n" + " Data : " + str(store_API.get('data')) + "\n \n Status : " + str(store_API.get('status_code')) + "\n\n json_dump :" + str(store_API.get('json_dump')))
                    if store_API.get('json_dump') and store_API.get('json_dump').get('code') == 200:
                        if store_API.get("store_id") and store_API.get('chain_id'):
                            self.write({'gomart_store_id':store_API.get('store_id'), 'gomart_store_chain_id':store_API.get('chain_id')})

                    else:
                        msg = "GoMart API setStore with the invalid status code %s" % str(store_API.get("status_code"))
                        _logger.warning(msg)
        #                     raise exceptions.Warning("Invalid status code %s \n Message : %s " % str(store_API.get('json_dump').get('code')) % str(store_API.get('json_dump').get('error')))
                else:
                    _logger.warning("SaaS token does not exist or something went wrong.")
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
             _logger.warning("Server Down or SetStore GoMart API is down.")
        return True

    @api.multi
    def Set_to_delivery_region(self):
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        auth_token = self.env["auth.oauth.provider"].search([('name', '=', 'SaaS'),
                                                             ('enabled', '=', 'True')], limit=1)
        store_chain_id = 0
        if self.parent_id:
            store_chain_id = self.parent_id.id

        try:
            if gomart_server and gomart_server.name: 
                if auth_token and auth_token.client_id:
                    # API setDeliveryRegion
                    delivery_API = setDeliveryRegion(
                                                    gomart_server.name,
                                                    self.id,  # erp_delivery_region_id
                                                    store_chain_id,  # erp_store_chain_id
                                                    self.delivery_location.master_db_area_id or self.delivery_location.id,  # erp_location_id
                                                    auth_token.client_id
                                                    )
                    # Log
                    _logger.warning("\n\n\n" + " setDeliveryRegion  API : \n" + " Data : " + str(delivery_API.get('data')) + "\n\n Status : " + str(delivery_API.get('status_code')) + "\n\n json_dump :" + str(delivery_API.get('json_dump')) + '\n\n')
                    if (delivery_API.get('status_code') and delivery_API.get('json_dump').get('code')) == 200 and delivery_API.get('region_id'):
                        self.write({'gomart_delivery_region_id':delivery_API.get('region_id')})
                    else:
                        msg = "GoMart API setDeliveryRegion with the invalid status code %s " % str(delivery_API.get('json_dump').get('code')) + '\n' + "Error message : %s" % str(delivery_API.get('json_dump').get('error')) 
                        _logger.warning(msg)
#                     raise exceptions.Warning("GoMart API invalid status code %s " % str(delivery_API.get('json_dump').get('code')) + '\n' + 'Message : ' + str(delivery_API.get('json_dump').get('error')))
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            msg = "GoMart APi setDeliveryRegion is not working."
            _logger.warning(msg)
        return True
