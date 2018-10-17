# -*- coding: utf-8 -*-
from odoo import api, models, fields, _


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product brand"
    _order = "name"

    name = fields.Char(string='Brand Name', help='Brand name')
    brand_img = fields.Binary(string="Brand image", attachment=True, help="Medium-sized image of the brand. It is automatically")
    active = fields.Boolean(string='Active', default=True, help='Active or Inactive status from the Brand Info')
    master_db_brand_id = fields.Integer('Brand ID in Master DB', readonly = True, required = True)

    _sql_constraints = [('name_uniq', 'unique (name)', "The Brand name must be unique, Brand name is already choosen.")]
