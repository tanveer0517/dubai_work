# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PosSalesReportProductType(models.TransientModel):
    _name = 'pos.sales.report.type'

    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Stockable Product')], string = 'Product Type',
        default = 'consu',
        help = 'A stockable product is a product for which you manage stock. The "Inventory" app has to be installed.\n'
               'A consumable product, on the other hand, is a product for which stock is not managed.\n'
               'A service is a non-material product you provide.\n'
               'A digital content is a non-material product you sell online. The files attached to the products are the one that are sold on '
               'the e-commerce such as e-books, music, pictures,... The "Digital Product" module has to be installed.')
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced')],
        'State')

    # This method is called from the wizard which will get all the pos order
    #  which will have the the product type which is selected in wizard.
    @api.multi
    def sales_order_report_type(self):
        self.ensure_one()
        data = {
            'ids': self.id,
            'model': 'pos.sales.report',
            'form': self.read()[0],
        }

        query = """
                select po.name as order,pt.name,pp.barcode, pol.qty, pol.price_unit
                from pos_order_line pol
                left join pos_order po ON (po.id = pol.order_id)
                left join product_product pp ON (pp.id = pol.product_id)
                left join product_template pt ON (pt.id = pp.product_tmpl_id)
                where pt.type='%s'""" % (self.type)
        if self.state :
            query += """ and po.state='%s'""" % (self.state)
        self.env.cr.execute(query)
        result = self._cr.dictfetchall()
        if result :
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
                'product_type_name' : self.type,
                'lines' : result,
            })
        else :
            raise UserError(
                _('There is no Record related to this Product Type.'))

        return self.env['report'].get_action(self,
                                             'pos_order_history_type.report_sale_orders_type', data=data)


class ReportPOSSaleOrderProductTypeMulti(models.AbstractModel):

    _name = 'report.pos_order_history_type.report_sale_orders_type'

    @api.multi
    def render_html(self, docids, data=None):
        return self.env['report'].render('pos_order_history_type.report_sale_orders_type', dict(data or {}))
