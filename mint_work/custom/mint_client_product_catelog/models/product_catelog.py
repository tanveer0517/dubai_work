# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp


class Productcatelog(models.Model):
    _name = "product.catelog"

    # @api.model
    # def _default_company_ids(self):
    #     Companies = self.env['res.company']
    #     return [
    #         (6, 0, Companies._company_default_get().ids),
    #     ]

    name = fields.Char(related='pro_tmpl_ids.name', string='Name',
                          store=True)
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    # image_medium = fields.Binary(
    #     "Medium-sized image", attachment=True,
    #     help="Medium-sized image of the product. It is automatically "
    #          "resized as a 128x128px image, with aspect ratio preserved, "
    #          "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    # image_small = fields.Binary(
    #     "Small-sized image", attachment=True,
    #     help="Small-sized image of the product. It is automatically "
    #          "resized as a 64x64px image, with aspect ratio preserved. "
    #          "Use this field anywhere a small image is required.")

    pro_tmpl_ids = fields.Many2one('product.template', 'Product Template')
    barcode = fields.Char(related='pro_tmpl_ids.barcode', string='Barcode',
                          store=True)
    active = fields.Boolean('Active')
    default_code = fields.Char('Internal Reference')
    list_price = fields.Float('Sale Price', default=1.0, digits=dp.get_precision('Product Price'))
    categ_id = fields.Many2one('product.category', 'Product Category')
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        # default=lambda s: s._default_company_ids(),
        # auto_join=True,
    )

    @api.multi
    def update_template(self):
        # Method call when we click on add to catelog button on product
        # catelog.
        # Write company_ids on product.template so product visible in
        # product list and hide from product catelog.
        # Also make visible upto parent level category on point of sale.
        product_obj = self.env['product.template']
        pos_cate_obj = self.env['pos.category']
        product_rec = product_obj.sudo().search([('default_code', '=',
                                            self.default_code)])
        if product_rec:
            if product_rec.pos_categ_id:
                product_rec.pos_categ_id.active = True
                parent_categ = self.get_parent_category(product_rec.pos_categ_id)
                pos_cate_data = pos_cate_obj.search([('id', 'in',
                                                   parent_categ),
                                                     ('active', '=', False)])
                pos_cate_data.write({'active':True})
                if parent_categ:
                    for parent in parent_categ:
                        parent_rec = self.env['pos.category'].browse(parent)
                        for pos_cate in product_rec:
                            pos_cate.active = True
            product_rec.sudo().write({'company_ids': [(4,
                                            self.env.user.company_id.id)]})
        # prod_cat = self.env['product.catelog'].sudo().browse(self.id)
        self.sudo().write({
            'company_ids': [(4, self.env.user.company_id.id)]})
        kanban_id = self.env.ref(
            'mint_client_product_catelog.product_catelog_kanban_view').id
#         
        try:
            product_rec.gomartcatelog(company_id=self.env.user.company_id.id)
        except:
            pass
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Catalog'),
            'view_type': 'kanban',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.catelog',
            'views': [(kanban_id, 'kanban')],
        }

    @api.multi
    def get_parent_category(self, category_id):
        # Return list of parent level category for given category.
        res = []
        pos_cate = self.env['pos.category'].browse(category_id.id)
        if pos_cate.parent_id:
            for parent_cate in pos_cate.parent_id:
                res.append(parent_cate.id)
                if parent_cate.parent_id:
                    parent_ids = self.get_parent_category(parent_cate)
                    for parent_id in parent_ids:
                        res.append(parent_id)
        return res

    @api.model
    def create(self, vals):
        # tools.image_resize_images(vals)
        template = super(Productcatelog, self).create(vals)
        return template


class ProductTemplateUUID(models.Model):
    _inherit = 'product.template'

    master_db_product_id = fields.Integer('Product ID in Master DB', readonly=True, required=True)
    brand_id = fields.Many2one('product.brand', string='Brand Info',
                               help='Brand Info ')


class Product(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('product.brand', string='Brand Info',
                               help='Brand Info ')

    @api.multi
    def unload_product(self):
        prod_cat_rec = self.env['product.catelog'].sudo().search([(
            'pro_tmpl_ids', '=', self.product_tmpl_id.id)])
        self.product_tmpl_id.sudo().write({'company_ids':  [(3,
                                                      self.env.user.company_id.id)]})
        prod_cat_rec.sudo().write({'company_ids': [(3,
                                                   self.env.user.company_id.id)]})
        kanban_id = self.env.ref(
            'product.product_kanban_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Products'),
            'view_type': 'kanban',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.product',
            'views': [(kanban_id, 'kanban')],
        }


class ProductCategory(models.Model):
    """Product Category"""
    _inherit = 'product.category'

    master_db_pro_cat_id = fields.Integer('Master db Category ID')
    category_id = fields.Char(string='Reference No')
    # server_id = fields.Many2one('saas_portal.server', 'Server name')
    client_allow_product = fields.Boolean('Allow Product', default=True)


class ProductTemplate(models.Model):
    """Product Category"""
    _inherit = 'product.template'

    @api.multi
    def _recursive_search_of_parent(self, category_rec):
        categ_ids = []
        if category_rec and category_rec.parent_id:
            for category in category_rec.parent_id:
                categ_ids += self._recursive_search_of_parent(category)
        return [category_rec.id] + categ_ids

    @api.multi
    def categ_prod_exist(self, category_id):
        Products = self.search([('active', '=', True), ('pos_categ_id', '=', category_id.id)])
        if len(Products) >= 1:
            return True
        else:
            return False

    @api.multi
    def write(self, vals):
        PosCateg = self.env['pos.category']
        for product in self:
            if vals.get('active') == False:
                product_pos_categ_ids = product.pos_categ_id
                if product.pos_categ_id.parent_id:
                    product_pos_categ_ids = PosCateg.browse(self._recursive_search_of_parent(product.pos_categ_id))
                for pos_categ_id in product_pos_categ_ids:
                    if pos_categ_id and not self.categ_prod_exist(pos_categ_id):
                        pos_categ_id.active = False
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def unload_product(self):
        prod_cat_rec = self.env['product.catelog'].sudo().search([(
            'pro_tmpl_ids', '=', self.id)])
        self.write({'company_ids':  [(3, self.env.user.company_id.id)]})
        prod_cat_rec.sudo().write({'company_ids': [(3,
                                                   self.env.user.company_id.id)]})
        kanban_id = self.env.ref(
            'product.product_template_kanban_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Products'),
            'view_type': 'kanban',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.template',
            'views': [(kanban_id, 'kanban')],
        }


class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def unload_product(self):
        prod_cat_rec = self.env['product.catelog'].sudo().search([(
            'pro_tmpl_ids', '=', self.product_tmpl_id.id)])
        self.product_tmpl_id.sudo().write({'company_ids':  [(3,
                                                      self.env.user.company_id.id)]})
        prod_cat_rec.sudo().write({'company_ids': [(3,
                                                   self.env.user.company_id.id)]})
        kanban_id = self.env.ref(
            'mint_client_product_catelog.product_catelog_kanban_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Catalog'),
            'view_type': 'kanban',
            'view_mode': 'kanban,tree,form',
            'res_model': 'product.catelog',
            'domain': [('id', '=', prod_cat_rec.id,)],
            'views': [(kanban_id, 'kanban')],
        }
