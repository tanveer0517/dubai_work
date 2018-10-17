# -*- coding: utf-8 -*-
import csv
import imghdr
import base64
import StringIO
import sys
from odoo import models, fields, api, _
from odoo.exceptions import Warning

class ProductImageImportWizard(models.TransientModel):
    _name = 'import.product_image'

    file = fields.Binary('File to import', required=True)
    fname = fields.Char('File Name')

    @api.multi
    def import_file(self):
        self.ensure_one()
        file = StringIO.StringIO(base64.decodestring(self.file))
        reader = csv.DictReader(file)
        header =  reader.fieldnames
        csv.field_size_limit(sys.maxsize)
        keys = ['name', 'main_image', 'image1', 'image2', 'image3', 'image4', 'image5']
        allowed_img_types = ['rgb', 'gif', 'pbm', 'pgm', 'ppm', 'tiff', 'rast', 'xbm', 'jpeg', 'bmp', 'png']
        if set(keys) != set(header):
            Warning(_('Incorrect Header Keys. You can only use:') + "name, main_image, image1, image2, image3, image4, image5")
        if not self.fname.endswith('.csv'):
            raise Warning(_('Please select only CSV file to import images.'))
        if self.fname.endswith('.csv'):
            product_obj = self.env['product.template']
            if not header:
                raise Warning(_('Header rows can not be empty.'))
            if header and header[0] != 'name':
                raise Warning(_('First Column of header should be name'))
            if header and header[1] != 'main_image':
                raise Warning(_('Second Column of header should be main_image')) 
            for row in reader:
                if not row.get("name",False):
                    raise Warning(_('Incorrect Data. Product Name not found. You have to define product name to import image.'))
                product_id = False
                vals = {}
                image_lst = []
                if row['name']:
                    product_id = product_obj.search([('name', '=', row['name'])])
                if not product_id:
                    raise Warning(_('Product Not Found.'))
                if product_id:
                    if row.get('main_image', False):
                        if imghdr.what(row['main_image']) not in allowed_img_types:
                            raise Warning(_("Incorrect Image format."))
                        try:
                            with open(row['main_image'], 'rb') as image:
                                image_base64 = image.read().encode("base64")
                            vals.update({'image_medium': image_base64})
                        except IOError:
                            raise Warning(_("Could not find the image. Please make sure it is accessible to import."))
                    if header and len(header) > 2:
                        if len(header[2:]) > 5:
                            raise Warning(_("Could not import more than 5 images."))
                        for header_img_data in header[2:]:
                            if row.get(header_img_data, False):
                                if imghdr.what(row[header_img_data]) not in allowed_img_types:
                                    raise Warning(_("Incorrect Image format."))
                                try:
                                    with open(row[header_img_data], 'rb') as image_data:
                                        image_data_base64 = image_data.read().encode("base64")
                                        image_lst.append((0, 0, {'image': image_data_base64}))
                                except IOError:
                                    raise Warning(_("Could not find the image. Please make sure it is accessible to import."))
                    vals.update({'image_ids': image_lst})
                    product_id.write(vals)
            return True
