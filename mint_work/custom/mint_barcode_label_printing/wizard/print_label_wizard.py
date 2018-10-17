# -*- coding: utf-8 -*-
import math


from odoo import _, api, models, fields
from odoo.exceptions import Warning


class BarcodeLabelPrintingWizard(models.TransientModel):
    _name = 'barcode.label.printing'

    # Params values in thier variable
    columns = fields.Integer('Columns', default=1, required=True,
                             help="""Define how many columns you want in 
                             one row. Max is 5 columns""")
    rows = fields.Integer('Rows', default=1, required=True, help="""will be 
    calculate on basis of how much quantity you are printing and no's of 
    columns provided
    """)
    quantity = fields.Integer('Quantity', default=1, required=True)
    define_custom_position = fields.Boolean('Define Custom Starting Position')
    starting_row_position = fields.Integer('Starting Row Position', default=1,
                                           help="""Defines from which Row you 
                                           want to start printing """)
    starting_column_position = fields.Integer('Starting Column Position',
                                              default=1,
                                              help="""
    Defines from which position of the columns you want to start printing """)
    template_id = fields.Many2one('product.template', string = "Template")
    price = fields.Float(related="template_id.list_price", string='Price')
    ref_code = fields.Char(related="template_id.default_code", string='Reference Code')
    product_name = fields.Char(related="template_id.name",
                               string='Product Name')
    barcode_base = fields.Integer(related="template_id.barcode_base",
                                  string='Barcode Base')
    barcode = fields.Char(related="template_id.barcode", string='Barcode',
                          store=True)
    encoding = fields.Char(string='Encoding Format')


    @api.model
    def default_get(self, fields):
        # upper_list = ['Codabar', 'Code11', 'Code128', 'EAN13', 'EAN8',
        #               'Extended39', 'Extended93', 'FIM', 'I2of5', 'MSI',
        #               'POSTNET', 'QR', 'Standard39', 'Standard93', 'UPCA',
        #               'USPS_4State']
        res = super(BarcodeLabelPrintingWizard, self).default_get(fields)
        context = self.env.context or {}
        active_id = context.get('active_id')
        product_rec = self.env['product.template'].browse(active_id)
        if product_rec and product_rec.barcode_rule_id:
            code_format= (product_rec.barcode_rule_id.encoding).upper()
            encoding = code_format
            if encoding == 'ANY':
                encoding = "EAN13"
            res.update({
                'encoding': encoding,
                'template_id': product_rec.id,
            })
        else:
            res.update({
                'encoding' : 'EAN13',
                'template_id' : product_rec.id,
            })
        return res

    @api.onchange('quantity', 'columns', 'starting_column_position',
                  'starting_row_position')
    def onchange_qty_col(self):
        self.check_validation()

    @api.multi
    def print_barcode_labels(self):
        self.check_validation()
        # action_dict = self.env[
        #     'report'].get_action(self, 'mint_barcode_label_printing.report_barcode_label_printing')
        # del action_dict['report_type']
        # return action_dict
        return self.env[
            'report'].get_action(self, 'mint_barcode_label_printing.report_barcode_label_printing')

    def check_validation(self):
        rows = self.rows
        columns = self.columns
        qty = self.quantity
        row_start = self.starting_row_position
        column_start = self.starting_column_position

        if columns <= 0 or qty <= 0 or row_start <= 0 or column_start <= 0 :
            raise Warning(_("Please select a value greater then 0"))

        if columns > 5 :
            raise Warning(_("Please Enter Column value less then or "
                            "equal to 5"))

        if columns >= 1 or qty >= 1 :
            rows = math.ceil(qty / float(columns))
        self.update({'rows' : rows})

        if row_start > rows :
            raise Warning(_("Please select Row Start value less then Row "
                            "value"))

        if column_start > 5 :
            raise Warning(_("Please Enter Column Start value less then or "
                            "equal to 5"))
