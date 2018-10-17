# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError


class PosOrderHistory(models.TransientModel):
    _name = 'pos.order.history'

    company_id = fields.Many2one('res.company', default = lambda
        self : self.env.user.company_id.id)
    start_date = fields.Date(string='Start Date', help="Start Date")
    end_date = fields.Date(string='End Date', help="End Date")
    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])
    location = fields.Many2one('stock.location', string='Location', domain=[('usage', '=', 'internal')])
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced')],
        'Status')

    @api.multi
    def order_history(self):
        self.ensure_one()
        data = {
            'ids': self.id,
            'model': 'pos.order.history',
            'form': self.read()[0]
        }
        quary = """
                select po.name as order,pt.name,pp.barcode, pol.qty, pol.price_unit
                from pos_order_line pol
                left join pos_order po ON (po.id = pol.order_id)
                left join product_product pp ON (pp.id = pol.product_id)
                left join product_template pt ON (pt.id = pp.product_tmpl_id)
                where pol.create_date::date >= '%s' and pol.create_date::date <= '%s'
                """ % (self.start_date, self.end_date)
        if self.partner_id:
            quary += """ and po.partner_id=%s""" % (self.partner_id.id)
        if self.location:
            quary += """ and po.location_id=%s""" % (self.location.id)
        if self.state:
            quary += """ and po.state='%s'""" % (self.state)
        self.env.cr.execute(quary)
        result = self._cr.dictfetchall()
        data.update({
            'company_logo' : self.company_id.logo,
            'company_name' : self.company_id.partner_id.name,
            'company_street' : self.company_id.partner_id.street,
            'company_street2' : self.company_id.partner_id.street2,
            'company_city' : self.company_id.partner_id.city,
            'company_state_id' :
                self.company_id.partner_id.state_id.name,
            'company_country_id' :
                self.company_id.partner_id.country_id.name,
            'company_zip' : self.company_id.partner_id.zip,
            'company_phone' : self.company_id.partner_id.phone,
            'company_mobile' : self.company_id.partner_id.mobile,
            'company_fax' : self.company_id.partner_id.fax,
            'company_email' : self.company_id.partner_id.email,
            'company_website' : self.company_id.partner_id.website,
            'partner_name':self.partner_id.name,
            'street':self.partner_id.street,
            'street2':self.partner_id.street2,
            'city':self.partner_id.city,
            'state':self.partner_id.state_id.name,
            'country':self.partner_id.country_id.name,
            'zip':self.partner_id.zip,

            'lines':result,
            'start_date': self.start_date,
            'end_date': self.end_date,
        })
        return self.env['report'].get_action(self, 'pos_order_history.report_order_history', data=data)


class ReportPOSOrderHistory(models.AbstractModel):

    _name = 'report.pos_order_history.report_order_history'

    @api.multi
    def render_html(self, docids, data=None):
        return self.env['report'].render('pos_order_history.report_order_history', dict(data or {}))
