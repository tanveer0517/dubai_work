# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
from odoo.report import report_sxw
from odoo import models, api


class WastageReportParser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(WastageReportParser, self).__init__(cr, uid, name,
                                                  context=context)

        self._cr, self._uid, self._context = cr, uid, context
        self.localcontext.update({
            'calculate_wastage_line_report':
                self.calculate_wastage_line_report,
        })

    @api.model
    def calculate_wastage_line_report(self, data):
        """
        Create dict for use in report tempplate
        :param data: all MO between dates
        :return: dict of mo and wastage lines
        """
        result = []
#         move_line = self.search(['location_dest_id','=',self.env.ref('mint_wastage_report.picking_type_wastage').id])
        for move in data:
            line = []
            line.append(move.picking_id.name)
            line.append(move.product_id.name)
            line.append(move.product_uom_qty)
            line.append(move.product_uom.name)
            line.append(move.picking_id.wastage_date)
            line.append(move.picking_id.min_date)
            result.append(line)
        result.sort(key = lambda x: x[1])
        return result


class PoHistoryReportAbs(models.AbstractModel):
    _name = 'report.mint_wastage_report.template_view_wastage_report'
 
    _inherit = 'report.abstract_report'
 
    _template = 'mint_wastage_report.template_view_wastage_report'
 
    _wrapped_report_class = WastageReportParser
