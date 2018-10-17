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
    def ir_sync_store_products(self):
        product_obj = self.env["product.template"]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        for rec in product_obj.search([]):
            rec.add_to_catelog_gomart()

    @api.multi
    def ir_sync_store_product_range(self):
        product_obj = self.env["product.template"]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        for rec in product_obj.search([]):
            rec.add_to_store_product_range_gomart()


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def ir_sync_res_partner(self):
        for data in self.env['res.partner'].search([]):
            if data.is_company == False:
                data.createCustomer()
