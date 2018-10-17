# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools

class PosCategory(models.Model):
    """Product Category"""
    _inherit = 'pos.category'

    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this category (Does not consider the children categories)")


    def _compute_product_count(self):
        # count the number of products under this pos category (Does not
        # consider
        # the children categories
        read_group_res = self.env['product.product'].read_group([
            ('pos_categ_id','in',self.ids)], ['pos_categ_id'], ['pos_categ_id'])
        group_data = dict((data['pos_categ_id'][0], data['pos_categ_id_count'])
                          for data in read_group_res)
        for categ in self:
            categ.product_count = group_data.get(categ.id, 0)

class product_category(models.Model):

    _inherit = 'product.category'

    image = fields.Binary(attachment=True,
        help="This field holds the image used as image for the cateogry, limited to 1024x1024px.")
    image_medium = fields.Binary(string="Medium-sized image", attachment=True,
        help="Medium-sized image of the category. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(string="Small-sized image", attachment=True,
        help="Small-sized image of the category. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        return super(product_category, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(product_category, self).write(vals)