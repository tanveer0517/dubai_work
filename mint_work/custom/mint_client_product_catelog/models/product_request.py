# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from odoo import api, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.http import request
from odoo.sql_db import db_connect
from odoo.api import Environment

class Productrequest(models.Model):
    _name = "product.request"

    def _get_default_category_id(self):
        Category =  self.env['product.category']
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        # category = self.env.ref('product.product_category_1', raise_if_not_found=False)
        category = Category.search([('name', '=', 'Saleable')], limit=1)
        return category and category.type == 'normal' and category.id or False

    def _get_default_uom_id(self):
        return self.env["product.uom"].search([], limit=1, order='id').id

    name = fields.Char('Name', index=True, required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help='Gives the sequence order when displaying a product list')
    description = fields.Text(
        'Description', translate=True,
        help="A precise description of the Product, used only for internal information purposes.")
    description_purchase = fields.Text(
        'Purchase Description', translate=True,
        help="A description of the Product that you want to communicate to your vendors. "
             "This description will be copied to every Purchase Order, Receipt and Vendor Bill/Refund.")
    description_sale = fields.Text(
        'Sale Description', translate=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sale Order, Delivery Order and Customer Invoice/Refund")
    type = fields.Selection([
        ('consu', _('Consumable')),
        ('service', _('Service')),
        ('product', _('Stockable Product'))],
        string='Product Type', default='product', required=True, readonly=True,
        help='A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
             'A consumable product, on the other hand, is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.\n'
             'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
             'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    rental = fields.Boolean('Can be Rent')
    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, default=_get_default_category_id, domain="[('type','=','normal')]",
        required=True, help="Select category for the current product")
    barcode = fields.Char('Barcode', readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    default_code = fields.Char('Internal Reference', index=True)

    # price fields
    list_price = fields.Float(
        'Sale Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        help="Base price to compute the customer price. Sometimes called the catalog price.")
    lst_price = fields.Float(
        'Public Price', related='list_price',
        digits=dp.get_precision('Product Price'))

    volume = fields.Float(
        'Volume', compute='_compute_volume', inverse='_set_volume',
        help="The volume in m3.", store=True)
    weight = fields.Float(
        'Weight', compute='_compute_weight', digits=dp.get_precision('Stock Weight'),
        inverse='_set_weight', store=True,
        help="The weight of the contents in Kg, not including any packaging, etc.")

    warranty = fields.Float('Warranty')
    sale_ok = fields.Boolean(
        'Can be Sold', default=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist', store=False,
        help='Technical field. Used for searching on pricelists, not stored in database.')
    uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default Unit of Measure used for all stock operation.")
    uom_po_id = fields.Many2one(
        'product.uom', 'Purchase Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default Unit of Measure used for purchase orders. It must be in the same category than the default unit of measure.")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('product.template'), index=1)
    packaging_ids = fields.One2many(
        'product.packaging', 'product_tmpl_id', 'Logistical Units',
        help="Gives the different ways to package the same product. This has no impact on "
             "the picking order and is mainly used if you use the EDI module.")
    seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors')

    active = fields.Boolean('Active', default=True,
                            help="If unchecked, it will allow you to hide the product without removing it.")
    color = fields.Integer('Color Index')

    # related to display product product information if is_product_variant
    default_code = fields.Char(
        'Internal Reference', store=True)

    item_ids = fields.One2many('product.pricelist.item', 'product_tmpl_id', 'Pricelist Items')

    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users','Current User', default=lambda self: self.env.user)

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    @api.multi
    def _compute_template_price(self):
        prices = {}
        pricelist_id_or_name = self._context.get('pricelist')
        if pricelist_id_or_name:
            pricelist = None
            partner = self._context.get('partner')
            quantity = self._context.get('quantity', 1.0)

            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist_id_or_name, basestring):
                pricelist_data = self.env['product.pricelist'].name_search(pricelist_id_or_name, operator='=', limit=1)
                if pricelist_data:
                    pricelist = self.env['product.pricelist'].browse(pricelist_data[0][0])
            elif isinstance(pricelist_id_or_name, (int, long)):
                pricelist = self.env['product.pricelist'].browse(pricelist_id_or_name)

            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                prices = pricelist.get_products_price(self, quantities, partners)

        for template in self:
            template.price = prices.get(template.id, 0.0)

    @api.model
    def create(self,vals):
        config_id = self.env['ir.config_parameter'].sudo().get_param('portal.database')
        if config_id:
            new_cr = db_connect(str(config_id)).cursor()
            new_env = Environment(new_cr, SUPERUSER_ID, {})
            user_id = new_env['res.users'].search([('id','=',1)])
            if user_id:
                vals.update({'partner_id':user_id.partner_id.id})
        return super(Productrequest, self).create(vals)

    @api.multi
    def action_progress(self):
        config_id = self.env['ir.config_parameter'].sudo().get_param('portal.database')
        if config_id:
            new_cr = db_connect(str(config_id)).cursor()
            new_env = Environment(new_cr, SUPERUSER_ID, {})
            client_rec = new_env['saas_portal.client'].search([('name', '=', str(self._cr.dbname))])
            for my_product in self:
                product_categ = new_env['product.category'].search(
                    [('category_id', '=', my_product.categ_id.category_id)],limit=1)
                product_vals = {'name': my_product.name, 'type': my_product.type, 'categ_id': product_categ.id,
                                'state':'new','client_id':client_rec.id,
                                'list_price': my_product.list_price, 'image': my_product.image}
                client_product = new_env['product.request'].sudo().create(product_vals)
                rejection_template_id = self.env['ir.model.data'].get_object('mint_client_product_catelog',
                                                                             'email_template_product_client_request')
                if rejection_template_id:
                    if self.env.user.partner_id.email:
                        rejection_template_id.sudo().send_mail(self.id,
                                                         force_send=True,
                                                        email_values={'email_to': self.env.user.partner_id.email})
                my_product.state = 'inprogress'
            new_cr.commit()




