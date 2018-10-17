# -*- coding: utf-8 -*-
import base64
import csv
import StringIO
import sys

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError

class ProductBarcodeImport(models.TransientModel):
    _name = 'product.multi.barcode.import'
    _description = 'Product Multi Barcode Import'

    barcode_file = fields.Binary('Select File')
    fname = fields.Char('File Name')

    #read csv file of barcode and creates a barcode to its realted product.
    @api.multi
    def create_barcodes(self):
        self.invalidate_cache()
        ctx = dict(self.env.context)
        self.ensure_one()
        file = StringIO.StringIO(base64.decodestring(self.barcode_file))
        if not self.fname.endswith('.csv'):
            raise UserError(_('Please select only CSV file to import barcode.'))
        reader = csv.DictReader(file)
        header =  reader.fieldnames
        csv.field_size_limit(sys.maxsize)
        keys = ['parent_barcode', 'child_barcode', 'qty', 'unit_of_measurement']
        if set(keys) != set(header):
            raise UserError(_('Header is missing in the CSV file, Please add the header. '
                      'Header keys should be as:') + "parent_barcode, child_barcode, qty, unit_of_measurement")
        if self.fname.endswith('.csv'):
            if not header:
                raise UserError(_('Header rows can not be empty.'))
            multi_barcode_obj = self.env['product.multi.barcode']
            uom_obj = self.env['product.uom']
            product_id = self.env.context['active_id']
            counter = 0
            for row in reader:
                try:
                    counter += 1
                    parent_barcode = row.get('parent_barcode', False)
                    child_barcode = row.get('child_barcode', False)
                    qty = (row.get('qty', False)).strip()
                    if not qty:
                        raise UserError(_('Incorrect Data. Barcode Quantity cannot be blank.'))
                    qty = float(qty)
                    uom = (row.get('unit_of_measurement', False)).strip()
                    existing_qty = 0
                    multi_barcode_rec = False
                    vals = {'product_id' : product_id}
                    if not parent_barcode and not child_barcode:
                        raise UserError(_('Incorrect Data. There has to be atleast one parent barcode or child barcode.'))
                    if not uom:
                        raise UserError(_('Incorrect Data. Unit of Measure cannot be blank.'))
                    if uom != False:
                        uom_rec = uom_obj.search([('name', '=', uom)])
                        if not uom_rec:
                            raise UserError(_("Error!. No Unit of Measurement "
                                            "match for '%s' "
                                            "found in row '%s'.") % (uom, counter))
                    if qty and qty == 0:
                        raise UserError(_('Incorrect Data. Barcode Quantity cannot be 0.'))

                    if ((qty >= 1) or (uom_rec)) and (parent_barcode or child_barcode):
                        multi_barcode_rec = multi_barcode_obj.search(['|',
                                                                      ('parent_barcode', '=', parent_barcode),
                                                                      ('child_barcode', '=', child_barcode)])
                        existing_qty = multi_barcode_rec.qty
                        if existing_qty and qty :
                            qty += existing_qty
                        vals.update({'qty' : qty})
                        if uom_rec :
                            vals.update({'product_uom_id' : uom_rec.id})
                        if multi_barcode_rec and (qty >= 1 or uom_rec):
                            multi_barcode_rec.write(vals)
                        if not multi_barcode_rec and (qty >= 1 or uom_rec):
                            if parent_barcode:
                                vals.update({'parent_barcode': parent_barcode})
                            if child_barcode:
                                vals.update({'child_barcode': child_barcode})
                            multi_barcode_obj.create(vals)
                except Exception as e:
                    raise UserError(_("Error: We got %s. Please correct the "
                                      "CSV and import it again!") % (e))
        return {'type': 'ir.actions.client', 'tag': 'reload'}
