# -*- coding: utf-8 -*-
import StringIO
import sys
import base64
import csv

from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError, Warning


class catelogimport(models.TransientModel):
    _name = 'catelog.import'

    csv_file = fields.Binary(string='CSV File', required=True)
    fname = fields.Char('File Name')

    @api.multi
    def import_csv(self) :
        self.invalidate_cache()
        self.ensure_one()
        file = StringIO.StringIO(base64.decodestring(self.csv_file))
        if not self.fname.endswith('.csv') :
            raise UserError(_('Please select only CSV file to import product catelog.'))
        reader = csv.DictReader(file)
        header = reader.fieldnames
        csv.field_size_limit(sys.maxsize)
        keys = ['name', 'internal_reference', 'barcode']
        if set(keys) != set(header) :
            raise UserError(_('Header is missing in the CSV file, Please add the header. '
                      'Header keys should be as:') + " 'name', 'internal_reference', 'barcode'. ")
        if self.fname.endswith('.csv') :
            if not header :
                raise UserError(_('Header rows can not be empty.'))
            catelog_obj = self.env['product.catelog']
            pro_request_obj = self.env['product.request']
            for row in reader :
                try:
                    name = (row.get('name', False)).strip()
                    barcode = (row.get('barcode', False)).strip()
                    internal_reference = (row.get('internal_reference', False)).strip()
                    type = 'product'
                    product_request_vals = {}
                    if name and barcode:
                        catelog_rec = catelog_obj.search([('barcode', '=', barcode)], limit=1)
                        if catelog_rec :
                            catelog_rec.update_template()
                        else :
                            product_request_vals.update({
                                'name': name,
                                'default_code':internal_reference,
                                'type':type,
                                'barcode':barcode,
                            })
                            rec = pro_request_obj.search(
                                [('name', '=', name),
                                 ('barcode', '=', barcode)], limit=1)
                            if not rec:
                                pro_request_obj.create(product_request_vals)
                            try:
                                pro_request_obj.gomartcatelog(self.env.user.company_id.id)
                            except:
                                pass
                    else:
                        raise UserError(_(
                            'Incorrect Data. The Field cannot be blank or '
                            'remove the unwanted record from the CSV.'))
                except Exception as e :
                    raise UserError(_("Error! %s ") % (e))
        return {'type' : 'ir.actions.client', 'tag' : 'reload'}

    # @api.multi
    # def import_csv(self):
    #     ctx = self._context
    #     catelog_obj = self.env['product.catelog']
    #     pro_request_obj = self.env['product.request']
    #     if not self.csv_file:
    #         raise exceptions.Warning(_("You need to select a file!"))
    #     # Decode the file data
    #     data = base64.b64decode(self.csv_file).decode("utf-8")
    #     file_input = io.StringIO(data)
    #     file_input.seek(0)
    #     reader_info = []
    #     delimeter = ','
    #     reader = csv.reader(file_input, delimiter=delimeter,
    #                         lineterminator='\r\n')
    #     try:
    #         reader_info.extend(reader)
    #     except Exception:
    #         raise exceptions.Warning(_("Not a valid file!"))
    #     keys = reader_info[0]
    #     del reader_info[0]
    #     values = {}
    #     p_values = {}
    #     for i in range(len(reader_info)):
    #         val = {}
    #         p_val = {}
    #         field = reader_info[i]
    #         values = dict(zip(keys, field))
    #         p_values = dict(zip(keys, field))
    #         code = p_values.get('internal_reference')
    #         catelog_rec = catelog_obj.search([('default_code','=',code)])
    #         if catelog_rec:
    #             catelog_rec.update_template()
    #         else:
    #             p_val['name'] = p_values.get('name')
    #             p_val['default_code'] = p_values.get('internal_reference')
    #             p_val['type'] = p_values.get('type')
    #             p_id = pro_request_obj.create(p_val)
    #     return {}

