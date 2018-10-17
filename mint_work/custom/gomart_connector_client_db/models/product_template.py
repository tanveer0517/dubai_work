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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    gomart_store_product_id = fields.Integer("GoMart Store Product ID", readonly="True",
                                             help="This field is generated from the GoMart.")

    gomart_store_product_range_id = fields.Integer("GoMart Store Product Range ID", readonly="True",
                                             help="This field is generated from the GoMart.")

#     company_id = fields.Many2one("res.company", string="Select company")

#     user_id = fields.Many2one("res.users", string="Added by ")

    qty_available = fields.Integer("Qty Available")
    unlimited = fields.Boolean("Unlimited", default=True)
    limited_qty = fields.Integer("Limited Qty")
    out_of_stock = fields.Boolean(string="Out of stock")
    gomart_low_stock = fields.Float("Low Stock", help="Low stock reminder")

    @api.multi
    def add_to_catelog_gomart(self):
        _company_id = self.env.user.company_id.id
        store_chain_id = 0
        if self.env.user.company_id.parent_id:
            store_chain_id = self.env.user.company_id.parent_id.id

        gomart_server = self.env['gomart.server.api'].search([], limit=1)

        try:
            if gomart_server and gomart_server.name: 
                    if self.categ_id.parent_id.master_db_pro_cat_id:
                        StoreProduct_API = setStoreProduct(
                                                        gomart_server.name,
                                                        self.id,  # erp_store_product_id
                                                        _company_id,  # erp_store_id
                                                        store_chain_id,  # erp_store_chain_id
                                                        self.master_db_product_id,  # erp_product_id
                                                        self.categ_id.parent_id.master_db_pro_cat_id,  # id,  # erp_category_id
                                                        self.categ_id.master_db_pro_cat_id,  # id,  # erp_subcategory_id
                                                        self.default_code,  # erp_store_sku,
                                                        self.env.user.company_id.gomart_store_id or 0
                                                        )
                    else:
                        StoreProduct_API = setStoreProduct(
                                                        gomart_server.name,
                                                        self.id,  # erp_store_product_id
                                                        _company_id,  # erp_store_id
                                                        store_chain_id,  # erp_store_chain_id
                                                        self.master_db_product_id,  # erp_product_id
                                                        0,  # self.categ_id.parent_id.id,  # erp_category_id
                                                        self.categ_id.master_db_pro_cat_id,  # id,  # erp_category_id
                                                        self.default_code,  # erp_store_sku
                                                        self.env.user.company_id.gomart_store_id or 0
                                                        )
                    # Log
                    _logger.warning("\n\n\n" + " Store Product API : \n" + " Data : " + str(StoreProduct_API.get('data')) + "\n Status : " + str(StoreProduct_API.get('status_code')) + "\n json_dump :" + str(StoreProduct_API.get('json_dump')))
                    if (StoreProduct_API.get('status_code') and StoreProduct_API.get('json_dump').get('code')) == 200:
                        if StoreProduct_API.get('store_product_id'):
                            self.write({'gomart_store_product_id':StoreProduct_API.get('store_product_id')})
                        else:
                            _logger.warning("GoMart APi setStoreProduct return None data.")
                    else:
                        msg = "GoMart APi setStoreProduct, with the invalid status code %s" % str(StoreProduct_API.get('json_dump').get('code')) + ' ' + 'GoMart Message : %s' % str(StoreProduct_API.get('json_dump').get('error'))
                        _logger.warning(msg)
            else:
                    msg = "Please update correct GoMart APi server."
                    _logger.warning(msg)
        except:
            _logger.warning(" GoMart setStoreProduct APi,it might be not working or GoMart Server Down.")
        return True

    @api.multi
    def add_to_store_product_range_gomart(self):
        _discount = 0
        _unlimited = {True:1, False:0}
        _out_of_stock = {True:2, False:1}

        gomart_server = self.env['gomart.server.api'].search([], limit=1)

        store_chain_id = 0
        if self.env.user.company_id.parent_id:
            store_chain_id = self.env.user.company_id.parent_id.id

        try:
            if gomart_server and gomart_server.name: 
                    StoreProductRange_API = setStoreProductRange(
                                                    gomart_server.name,
                                                    self.id,  # erp_store_product_range_id
                                                    self.master_db_product_id,  # erp_range_id
                                                    self.env.user.company_id.id,  # erp_store_id
                                                    store_chain_id,  # erp_store_chain_id
                                                    self.id,  # erp_store_product_id
                                                    self.list_price,  # erp_mrp_price
                                                    _discount,  # erp_prod_disc
                                                    self.list_price,  # erp_offer_price
                                                    self.qty_available,  # erp_qty_available
                                                    _unlimited.get(self.unlimited),  # erp_unlimited [0 – Limited, 1 ‐ Unlimited]
                                                    self.limited_qty,  # erp_pur_limit [Integer value – Limit of quantity per purchase]
                                                    _out_of_stock.get(self.out_of_stock),  # erp_out_of_stock [1 – Not outofstock, 2 ‐ Outofstock]
                                                    self.gomart_low_stock,  # erp_low_stock [Float ‐ Low stock reminder value]
                                                    self.barcode,  # erp_barcode
                                                    self.env.user.id,  # erp_added_by
                                                    self.env.user.company_id.gomart_store_id or 0
                                                    )
                    # Log
                    _logger.warning("\n\n\n" + " Store Product Range API : \n" + " Data : " + str(StoreProductRange_API.get('data')) + "\n Status : " + str(StoreProductRange_API.get('status_code')) + "\n json_dump :" + str(StoreProductRange_API.get('json_dump')))
                    if StoreProductRange_API.get('status_code') and StoreProductRange_API.get('json_dump').get('code') == 200:
                        if StoreProductRange_API.get('store_product_id'):
                            self.write({'gomart_store_product_range_id':StoreProductRange_API.get('store_product_id')})
                        else:
                            _logger.warning("GoMart APi setStoreProductRange returns None data. ")
                    else:
                        _logger.warning("GoMart API setStoreProductRange,Invalid code %s " % str(StoreProductRange_API.get('json_dump').get('code')) + ' ' + 'GoMart Message : %s' % str(StoreProductRange_API.get('json_dump').get('error') or 'None.'))
            else:
                _logger.warning("Please update correct GoMart APi server.")
        except:
            _logger.warning(" GoMart setStoreProductRange APi,it might be not working or GoMart Server Down.")
        return True

    @api.multi
    def inventory_stock(self):
        _unlimited = {True:1, False:0}
        _out_of_stock = {True:2, False:1}
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                StoreInventory_API = setInventoryStock(
                                                gomart_server.name,
                                                self.id,  # erp_store_inventory_range_id
                                                self.qty_available,  # erp_qty_available
                                                _unlimited.get(self.unlimited),  # erp_unlimited [0 – Limited, 1 - Unlimited]
                                                self.limited_qty,  # erp_pur_limit [Integer value – Limit of quantity per purchase]
                                                _out_of_stock.get(self.out_of_stock),  #  erp_out_of_stock [1 – Not outofstock, 2 - Outofstock]
                                                self.gomart_low_stock,  # erp_low_stock [Float - Low stock reminder value]
                                                self.env.user.company_id.gomart_store_id or 0
                                                )
                # Log
                _logger.warning("\n\n\n" + " Store Inventory API : \n" + " Data : " + str(StoreInventory_API.get('data')) + "\n Status : " + str(StoreInventory_API.get('status_code')) + "\n json_dump :" + str(StoreInventory_API.get('json_dump')))
                if StoreInventory_API.get('status_code') == 200 and StoreInventory_API.get('json_dump').get('code') == 200 and StoreInventory_API.get('store_range_id'):
                    self.write({'gomart_store_product_range_id':StoreInventory_API.get('store_range_id')})
                    return True 
                else:
                    msg = "GoMart API setInventoryStock with the invalid status code %s" % str(StoreInventory_API.get('json_dump').get('code')) + '\n' + str(StoreInventory_API.get('json_dump').get('error'))
                    _logger.warning(msg)
                    raise exceptions.Warning(msg)
                    return False
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            _logger.warning(" GoMart setInventoryStock APi,it might be not working or GoMart Server Down.")

    @api.multi
    def gomartcatelog(self, company_id=None):
        if company_id:
            _company_id = company_id
        else:
            _company_id = self.env.user.company_id.id
        gomart_server = self.env['gomart.server.api'].search([], limit=1)

        store_chain_id = 0
        if self.env.user.company_id.parent_id:
            store_chain_id = self.env.user.company_id.parent_id.id
        
        try:
            if gomart_server and gomart_server.name: 
                    if self.categ_id.parent_id.master_db_pro_cat_id:
                        StoreProduct_API = setStoreProduct(
                                                        gomart_server.name,
                                                        self.id,  # erp_store_product_id
                                                        _company_id,  # erp_store_id
                                                        store_chain_id,  # erp_store_chain_id
                                                        self.master_db_product_id,  # erp_product_id
                                                        self.categ_id.parent_id.master_db_pro_cat_id,  # id,  # erp_category_id
                                                        self.categ_id.master_db_pro_cat_id,  # id,  # erp_subcategory_id
                                                        self.default_code,  # erp_store_sku
                                                        self.env.user.company_id.gomart_store_id or 0
                                                        )
                    else:
                        StoreProduct_API = setStoreProduct(
                                                        gomart_server.name,
                                                        self.id,  # erp_store_product_id
                                                        _company_id,  # erp_store_id
                                                        store_chain_id,  # erp_store_chain_id
                                                        self.master_db_product_id,  # erp_product_id
                                                        0,  # self.categ_id.parent_id.id,  # erp_category_id
                                                        self.categ_id.master_db_pro_cat_id,  # id,  # erp_category_id
                                                        self.default_code,  # erp_store_sku
                                                        self.env.user.company_id.gomart_store_id or 0
                                                        )
                    # Log
                    _logger.warning("\n\n\n" + " Store Product API : \n" + " Data : " + str(StoreProduct_API.get('data')) + "\n Status : " + str(StoreProduct_API.get('status_code')) + "\n json_dump :" + str(StoreProduct_API.get('json_dump')))
                    if (StoreProduct_API.get('status_code') and StoreProduct_API.get('json_dump').get('code')) == 200:
                        if StoreProduct_API.get('store_product_id'):
                            self.write({'gomart_store_product_id':StoreProduct_API.get('store_product_id')})
                        else:
                            _logger.warning("GoMart APi setStoreProduct return None data.")
                    else:
                        msg = "GoMart APi setStoreProduct, with the invalid status code %s" % str(StoreProduct_API.get('json_dump').get('code')) + ' ' + 'GoMart Message : %s' % str(StoreProduct_API.get('json_dump').get('error'))
                        _logger.warning(msg)
            else:
                    msg = "Please update correct GoMart APi server."
                    _logger.warning(msg)
        except:
            _logger.warning(" GoMart setStoreProduct APi,it might be not working or GoMart Server Down.")
        return True
