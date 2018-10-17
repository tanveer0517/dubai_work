# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
from gomartapi import *
import logging

_logger = logging.getLogger(__name__)


class GomartConfigSettings(models.TransientModel):

    _name = 'gomart.config.settings'

    product = fields.Boolean("Product")
    product_category = fields.Boolean('Product Category')
    account_tax = fields.Boolean('Account Tax')
    product_uom = fields.Boolean('Product UOM')
    product_brand = fields.Boolean('Product Brand')
    product_group = fields.Boolean('Product Group')
    product_attribute = fields.Boolean('Product Attribute')
    city = fields.Boolean('City')
    location = fields.Boolean('Location')
    state = fields.Boolean('State')

    @api.multi
    def gomart_sync(self):

        if self.state:
            state_ids = self.env['res.country.state'].search([])
            for recs in state_ids:
                recs.write({})

        if self.city:
            city_ids = self.env['city.city'].search([])
            for recs in city_ids:
                recs.write({})

        if self.location:
            area_ids = self.env['city.area'].search([])
            for recs in area_ids:
                recs.write({})

        if self.account_tax:
            tax_ids = self.env['account.tax'].search([])
            for recs in tax_ids:
                recs.write({})

        if self.product_uom:
            uom_ids = self.env['product.uom'].search([])
            for recs in uom_ids:
                recs.write({})

        if self.product_brand:
            brand_ids = self.env['product.brand'].search([])
            for recs in brand_ids:
                recs.write({})

        if self.product_group:
            group_ids = self.env['product.group'].search([])
            for recs in group_ids:
                recs.write({})

        if self.product_attribute:
            attribute_ids = self.env['product.attribute'].search([])
            for recs in attribute_ids:
                recs.write({})

        if self.product_category:
            categ_ids = self.env['product.category'].search([])
            for recs in categ_ids:
                recs.write({})

        if self.product:
            product = self.env['product.template'].search([])
            for recs in product:
                recs.add_to_gomart()

        return True
