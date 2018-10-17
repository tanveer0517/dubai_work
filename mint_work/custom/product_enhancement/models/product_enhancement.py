# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)


class ProductGroup(models.Model):
    _name = 'product.group'

    name = fields.Char(string='Group Name', help='Group Name')
    active = fields.Boolean(string='Active', default=True, help='Active or Inactive status from the Group Info')
#     attributs_id = fields.Many2many('product.attribute', string="Attribute Groups")
    attributs_id = fields.Many2many('product.attribute', 'product_attribute_group_rel', 'group_id', 'attribute_id', string="Attribute Groups")

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product brand"
    _order = "name"

    name = fields.Char(string='Name', help='Enter Brand name')
    brand_img = fields.Binary(string="Brand image", attachment=True, help="Medium-sized image of the brand. It is automatically")
    active = fields.Boolean(string='Active', default=True, help='Active or Inactive status from the Brand Info')
    server_id = fields.Many2one('saas_portal.server', 'Server name')

    _sql_constraints = [('name_uniq', 'unique (name)', "The Brand name must be unique, Brand name is already choosen.")]


class ProductTemplate(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string='Brand', help='Choose Brand Name ')


class  ProdcutGroupAttributes(models.Model):
    """ ProdcutGroupAttributes"""
    _name = 'product.group.attributes'

    attribute_id = fields.Many2one('product.attribute', string='Product Group attributes')
    attribute_value = fields.Char(string='Value')
    template_id = fields.Many2one('product.template', string='Template')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Brand', help='Choose Brand Name')
    attributes_id = fields.One2many('product.group.attributes', 'template_id', string='Attributs')
    server_id = fields.Many2one('saas_portal.server','Server')
    mrp_price = fields.Float('Mrp Price')
    mop_price = fields.Float('Mop Price')

    @api.multi
    @api.constrains('is_subscription','server_id')
    def _check_server(self):
        context =  self._context or {}
        if context.get('subscription_product'):
            return True
        for template in self:
            if not template.is_subscription and not template.server_id:
                raise ValidationError(_("Server must be configured on the Product."))
        return True


    @api.multi
    @api.constrains('pos_categ_id','available_in_pos')
    def _check_pos_categ(self):
        context = self._context or {}
        for template in self :
            if not context.get('subscription_product'):
                if template.available_in_pos and not template.pos_categ_id :
                    raise ValidationError(
                        _("POS category is mandatory If you need this product in POS! Please select the correct POS category on the product!"))
        return True

    @api.onchange('pos_categ_id')
    def pos_catagory_on_change(self):
        attribute_lst = []
        if self.pos_categ_id:
            if self.pos_categ_id.group_id:
                for attributes in self.pos_categ_id.group_id.attributs_id:
                    attribute_lst.append((0, 0, {'attribute_id': attributes.id,
                                          'template_id': self._origin.id}))
        self.attributes_id = attribute_lst


class PosCategory(models.Model):
    """POS Category"""
    _inherit = 'pos.category' 

    group_id = fields.Many2one('product.group', string='Group', help='Group Info ')

class ProductCategory(models.Model):
    """Product Category"""
    _inherit = 'product.category'

    category_id = fields.Char(string='Reference No',default=lambda self: _('New'))
    server_id = fields.Many2one('saas_portal.server', 'Server name')
    allow_product = fields.Boolean('Allow Product',default=True)
    is_subscription = fields.Boolean("Subscription Category", default=False)

    @api.constrains('is_subscription')
    def _check_server(self):
        context =  self._context or {}
        if context.get('subscription_cate'):
            return True
        for category in self:
            if not category.is_subscription and not category.server_id:
                raise ValidationError(_("Server must be configured on the Category."))
        return True

    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['category_id'] = self.env['ir.sequence'].next_by_code('product.category') or _('New')
        return super(ProductCategory, self).create(vals)
