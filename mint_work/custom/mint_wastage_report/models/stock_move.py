# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, models, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    wastage_date = fields.Datetime('Wastage Date', help="""Select the Date 
    on which the Items were Wastage.""")

    @api.model
    def default_get(self, fields_list):
        rec = super(StockPicking, self).default_get(fields_list)
        if self._context.get('wastage'):
            rec.update({'picking_type_id':self.env.ref('mint_wastage_report.picking_type_wastage').id})
        return rec

class StockMove(models.Model):
    _inherit = 'stock.move'

    expected_wastage_qty = fields.Float(string="Expected Wastage QTY")
