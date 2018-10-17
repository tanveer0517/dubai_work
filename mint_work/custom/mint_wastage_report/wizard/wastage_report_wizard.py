# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WastageRreportWizard(models.TransientModel):
    _name = "wastage.report.wizard"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    @api.multi
    def generate_wastage_report(self):
        """
        Search MO which was betwwen entered dates
        :return: print MO report
        """
#         mo_orders = self.env['mrp.production'].search([
#             ('create_date', '>=', self.from_date),
#             ('create_date', '<=', self.to_date),
#             ('state', '=', 'done'), ('is_wastage_moved', '=', True)])
        move_line = self.env['stock.move'].search([
            ('location_dest_id','=',self.env.ref('mint_wastage_report.location_wastage').id),
            ('state','=','done'),('picking_id.wastage_date','>=',self.from_date + " 00:00:00"),
            ('picking_id.min_date','<=',self.to_date + " 23:59:59")])
        if not move_line:
            raise UserError(_('There is no wastage between selected date.'))
        return self.env['report'].get_action(
            move_line,
            'mint_wastage_report.template_view_wastage_report')
