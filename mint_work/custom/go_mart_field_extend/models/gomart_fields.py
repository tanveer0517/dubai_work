# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class GomartStore(models.Model):
    _name = 'gomart.store'
    
    partner_id = fields.Many2one('res.partner')


    name = fields.Char(related='partner_id.name',string='Store Name', help='Store Name')
    # date_order = fields.Datetime(string='Order Date',readonly=True, index=True, default=fields.Datetime.now)

    
    active = fields.Boolean(default=True, help='Active or Inactive status from the Go Mart Store')
    
    marchant_type = fields.Selection([('gocery', 'Gocery'), ('resturant', 'Resturant')], string='Marchant type', help='Group Name')
    store_type = fields.Selection([('individual', 'Individual'), ('seperatestore', 'Seperate store')], string='Store type', help='Store type')
    image = fields.Binary(string='Logo', help='Logo')
    suggestion = fields.Text(string='Suggestion ', help='Suggestion')
    longitude = fields.Char(string='Logitude', help='Logitude')
    latitude = fields.Char(string='Latitude', help='Latitude')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    commission = fields.Float(string='Commission')
    startdate = fields.Date(string='Start Date')
    currency = fields.Char(string='Currency', default='AED', readonly='True')
    address = fields.Char(string='Store Address ', help='Store Address')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State')
    city_id = fields.Char(string='City')
    phone = fields.Char(string='Store Phone ', help='Phone Number ')
    locality_id = fields.Many2one('gomart.locality', string='Locality')
    mobile = fields.Char(string='Mobile Number ', help='Mobile Number ')
    email = fields.Char(string='Your Email', help='Your Email')
    website = fields.Char(string='Store Web Site ', help='Website')


class GomartLocality(models.Model):
    _name = 'gomart.locality'

    name = fields.Char('Locality')


