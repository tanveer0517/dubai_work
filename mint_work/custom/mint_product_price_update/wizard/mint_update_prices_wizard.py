# -*- coding: utf-8 -*-
import base64
import csv
import StringIO
import sys


from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError
from odoo.tools import html2text, ustr


class mint_prices_update_wizard(models.Model):
    _name = 'mint.price.update.wizard'

    select_price = fields.Selection([
        ('list_price', 'Sale price'),
        ('standard_price', 'Cost price'),
        ('both', 'Both')
    ], string = 'Select Price to Update', help = """Select the Price which you 
        want to Update""")
    csv_import = fields.Boolean('Import CSV', help="""Import Product 
    updated price csv with fields like product name, barcode, internal 
    reference, sale price, cost price""")
    csv_file = fields.Binary(string = 'CSV File')
    csv_file_name = fields.Char('file Name')
    product_ids = fields.One2many('product.template.custom',
                                  'product_temp_id', string='Products list')
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Stockable Product')], string = 'Product Type',
        default = 'product', readonly=True,
        help = 'A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
               'A consumable product, on the other hand, is a product for which stock is not managed.\n'
               'A service is a non-material product you provide.\n'
               'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
               'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')

    # This function will update the product template price list based on the
    # selection of the price like sale, cost, both, or else if a csv file
    # is imported then it will take the data from csv file and update the
    # product tempalte price
    @api.multi
    def update_prodcut_price(self):
        try:
            if not self.select_price:
                raise UserError(_("Please select Product Price to be updated."))

            if not self.csv_import and not (self.product_ids):
                raise UserError(_("Please select Product or Import CSV."))

            if self.select_price == 'list_price' and self.product_ids and not self.csv_import:
                for rec in self.product_ids:
                    if self.env.user.company_id.id in rec.product_id.mapped('company_ids.id'):
                        rec.product_id.write({'list_price':rec.new_list_price})

            if self.select_price == 'standard_price' and self.product_ids and not self.csv_import:
                for rec in self.product_ids:
                    if self.env.user.company_id.id in rec.product_id.mapped('company_ids.id'):
                        rec.product_id.write({'standard_price':rec.new_standard_price})

            if self.select_price == 'both' and self.product_ids and not self.csv_import:
                for rec in self.product_ids:
                    if self.env.user.company_id.id in rec.product_id.mapped('company_ids.id') :
                        rec.product_id.write({'list_price' : rec.new_list_price,
                                              'standard_price' : rec.new_standard_price})

            if self.csv_import and self.csv_file:
                ctx = dict(self.env.context)
                self.ensure_one()
                file = StringIO.StringIO(base64.decodestring(self.csv_file))
                if not self.csv_file_name.endswith('.csv') :
                    raise UserError(_('Please select only CSV file to import Product updated price.'))
                reader = csv.DictReader(file)
                header = reader.fieldnames
                csv.field_size_limit(sys.maxsize)
                keys = ['name', 'default_code', 'barcode','standard_price','list_price']
                if set(keys) != set(header) :
                    raise UserError(_('Incorrect Header Keys. You can only use:') + "name, default_code, barcode, standard_price, list_price")
                if self.csv_file_name.endswith('.csv') :
                    if not header :
                        raise UserError(_('Header rows can not be empty.'))
                    for row in reader:
                        name = row.get('name', False)
                        default_code = row.get('default_code', False)
                        barcode = row.get('barcode', False)
                        if self.select_price == 'list_price' or self.select_price == 'both':
                            if row.get('list_price') == '':
                                raise UserError(_('Sale Price should be a Numeric Value for product %s. Please Update the List Price column') % row.get('name'))
                            if isinstance(float(row.get('list_price','0.00')),(int, float)):
                                list_price = float(row.get('list_price', '0.00'))
                        if self.select_price == 'standard_price' or self.select_price == 'both':
                            if row.get('standard_price') == '':
                                raise UserError(_('Cost Price should be a Numeric Value for product %s. Please Update the Cost Price column') % row.get('name'))
                            if isinstance(float(row.get('standard_price','0.00')), (int, float)):
                                standard_price = float(row.get('standard_price','0.00'))
                        if name and barcode :
                            if self.select_price == 'list_price' :
                                if list_price and list_price > 0.00 :
                                    rec = self.get_product_template_rec(name,barcode)
                                    if rec :
                                        if self.env.user.company_id.id in rec.mapped('company_ids.id') :
                                            rec.write({'list_price' : list_price})
                                else :
                                    raise UserError(_('Sale Price is blank or 0. Please Update the List Price column'))
                            if self.select_price == 'standard_price' :
                                if standard_price and standard_price > 0.00:
                                    rec = self.get_product_template_rec(name,barcode)
                                    if rec :
                                        if self.env.user.company_id.id in rec.mapped('company_ids.id') :
                                            rec.write({'standard_price' : standard_price})
                                else :
                                    raise UserError(_('Cost Price is blank or 0. Please Update the Standard Price column'))
                            if self.select_price == 'both' :
                                if (list_price and list_price > 0.00) and (standard_price and standard_price > 0.00) :
                                    rec = self.get_product_template_rec(name,barcode)
                                    if rec :
                                        if self.env.user.company_id.id in rec.mapped('company_ids.id') :
                                            rec.write({
                                                'standard_price' : standard_price,
                                                'list_price' : list_price})
                                else :
                                    raise UserError(_(
                                        'Sale Price or Cost Price is blank or 0. Please Update the Price column'))
                        else :
                            raise UserError(_(
                                'Name or Barcode is blank. Please Update the CSV File.'))
        except Exception as e :
            raise UserError(_("Error:\n%s") % ustr(e))

    @api.multi
    def get_product_template_rec(self, name=False,  barcode=False):

        product_obj = self.env['product.template']
        rec = product_obj.search([('name', '=', name),('barcode', '=', barcode)], limit = 1)
        return rec


class Product_Template_Custom(models.Model):
    _name = 'product.template.custom'

    product_temp_id = fields.Many2one('mint.price.update.wizard')
    product_id = fields.Many2one('product.template', string="Product")
    sequence = fields.Char('sequence')
    barcode = fields.Char(related='product_id.barcode', string='Barcode')
    default_code = fields.Char(related='product_id.default_code',
                               string="Internal Reference")
    list_price = fields.Float(related='product_id.list_price', string="Sale "
                                                                      "Price")
    standard_price = fields.Float('Cost price')
    new_list_price = fields.Float('New Sale Price')
    new_standard_price = fields.Float('New Cost Price')

    # This onchange will set the cost price as per the users company and it
    # will be on be update in the user allocated company products only. ie
    # it will change the cost price in the product template for the user
    # allocated store only.
    @api.onchange('product_id')
    def onchange_custom_porduct_id(self):
        product_id = self.product_id
        if self.env.user.company_id.id in product_id.mapped('company_ids.id'):
            self.standard_price = product_id.standard_price
            self.list_price = product_id.list_price
