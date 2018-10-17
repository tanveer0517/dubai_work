# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)

# class ProductUomUUID(models.Model):
#     _inherit = 'product.uom'
# 
#     master_db_uom_id = fields.Integer('Product uom ID in Master DB', readonly=True, required=True)


class CityCityUUID(models.Model):
    _inherit = 'city.city'

    master_db_city_id = fields.Integer('City ID in Master DB')


class CityAreaUUID(models.Model):
    _inherit = 'city.area'

    master_db_area_id = fields.Integer('Area ID in Master DB')


class ResCountryStateUUID(models.Model):
    _inherit = 'res.country.state'

    master_db_state_id = fields.Integer('State ID in Master DB')


class ResCountryUUID(models.Model):
    _inherit = 'res.country'

    master_db_country_id = fields.Integer('Country ID in Master DB')
