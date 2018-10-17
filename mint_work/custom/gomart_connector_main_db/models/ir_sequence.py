# * coding: utf8 *
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, exceptions
from gomartapi import *
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def ir_sync_products(self):
        product_obj = self.env["product.template"]
        for rec in product_obj.search([]):
                rec.add_to_gomart()
        return True


class CountryState(models.Model):
    _inherit = 'res.country.state'

    @api.multi
    def ir_sync_state(self):
        state_obj = self.env["res.country.state"]
        for rec in state_obj.search([]):
           rec.write({})
        return True


class CityCity(models.Model):
    _inherit = 'city.city'

    @api.multi
    def ir_sync_city(self):
        city_obj = self.env["city.city"]
        for rec in city_obj.search([]):
           rec.write({})
        return True


class CityArea(models.Model):
    _inherit = 'city.area'

    @api.multi
    def ir_sync_area(self):
        area_obj = self.env["city.area"]
        for rec in area_obj.search([]):
           rec.write({})
        return True


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.multi
    def ir_sync_account_tax(self):
        tax_obj = self.env["account.tax"]
        for rec in tax_obj.search([]):
           rec.write({})
        return True


class ProductUnit(models.Model):
    _inherit = "product.uom"

    @api.multi
    def ir_sync_product_uom(self):
        uom_obj = self.env["product.uom"]
        for rec in uom_obj.search([]):
           rec.write({})
        return True


class ProductGroup(models.Model):
    _inherit = "product.group"

    @api.multi
    def ir_sync_product_group(self):
        group_obj = self.env["product.group"]
        for rec in group_obj.search([]):
           rec.write({})
        return True


class ProductCategory(models.Model):
    _inherit = 'product.attribute'

    def ir_sync_attribute(self):
        attribute_obj = self.env["product.attribute"]
        for rec in attribute_obj.search([]):
           rec.write({})
        return True


class ProductBrand(models.Model):
    _inherit = "product.brand"

    @api.multi
    def ir_sync_produc_brand(self):
        brand_obj = self.env["product.brand"]
        for rec in brand_obj.search([]):
           rec.write({})
        return True


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def ir_sync_category(self):
        category_obj = self.env["product.category"]
        for rec in category_obj.search([]):
           rec.write({})
        return True


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def ir_sync_res_partner(self):
        for data in self.env['res.partner'].search([]):
            if data.is_company == False:
                data.createCustomer()
            return True
