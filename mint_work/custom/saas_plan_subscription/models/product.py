from odoo import models, fields, api,_

class ProductTemplate(models.Model):

    _inherit='product.template'

    is_package = fields.Boolean(string='Package Product')
    bundled_product_ids = fields.Many2many('product.template',
                                          'budled_product_rel',
                                           'budled_product_id',
                                           'template_id',
                                          string="Bundled Product")
    is_subscription = fields.Boolean(string="Subscription")
    module_ids = fields.Many2many('ir.module.module',
                                           'module_product_rel',
                                           'product_id',
                                           'module_id',
                                           string="Modules")
    saas_prod_desc = fields.Text(
        'Subscription Description', translate=True,
        help="A description of the Product that you want to show for plan "
             "description. ")
