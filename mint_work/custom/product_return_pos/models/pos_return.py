# -*- coding: utf-8 -*-
from odoo import models, api, fields


class PosReturn(models.Model):
    _inherit = 'pos.order'

    return_ref = fields.Char(string='Return Ref', readonly=True, copy=False)
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status", default='nothing_return',
        help="Return status of Order")

    #Returns line information related to pos reference.
    @api.model
    def get_lines(self, ref):
        result = []
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        if order_id:
            lines = self.env['pos.order.line'].search([('order_id', '=', order_id.id)])
            for line in lines:
                if line.qty - line.returned_qty > 0:
                    new_vals = {
                        'product_id': line.product_id.id,
                        'product': line.product_id.name,
                        'qty': line.qty - line.returned_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'line_id': line.id,
                    }
                    result.append(new_vals)

        return [result]

    #Search for the client and returns it.
    @api.model
    def get_client(self, ref):
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        client = ''
        if order_id:
            client = order_id.partner_id.id
        return client

    #Override _order_fields to handle return order functionality.
    def _order_fields(self, ui_order):
        order = super(PosReturn, self)._order_fields(ui_order)
        if ui_order.get('lines',[]):
            for data in ui_order['lines']:
                if data[2] and data[2].get('line_id', False):
                    line = self.env['pos.order.line'].search([('id', '=', data[2]['line_id'])])
                    if line:
                        qty = -(data[2]['qty'])
                        line.returned_qty += qty
        if ui_order.get('return_ref', False):
            order['return_ref'] = ui_order['return_ref']
            order_product_dict = {}
            parent_order = self.search([('pos_reference', '=', ui_order['return_ref'])], limit=1)
            for line in parent_order.lines:
                if line.product_id and line.product_id.id not in order_product_dict:
                    order_product_dict[line.product_id.id] = {'tot_qty': line.qty}
                else:
                    qty = order_product_dict[line.product_id.id][tot_qty]
                    order_product_dict[line.product_id.id]['tot_qty'] = qty + line.qty
            for ret_order in self.search([('return_ref', '=', ui_order['return_ref'])]):
                for line in ret_order.lines:
                    if line.product_id and line.product_id.id not in order_product_dict:
                        order_product_dict[line.product_id.id] = {'tot_qty': line.qty}
                    else:
                        qty = order_product_dict[line.product_id.id]['tot_qty']
                        order_product_dict[line.product_id.id]['tot_qty'] = qty + line.qty
            for order_line in order.get('lines'):
                line = order_line[2]
                if line.get('product_id'):
                    if line.get('product_id') not in order_product_dict:
                        order_product_dict[line.get('product_id')] = {'tot_qty': line.get('qty')}
                    else:
                        qty = order_product_dict[line.get('product_id')]['tot_qty']
                        order_product_dict[line.get('product_id')]['tot_qty'] = qty + line.get('qty')
            product_qty = order_product_dict.values()
            product_qty_lst = [x for x in product_qty if x.get('tot_qty')]
            if not product_qty_lst:
                parent_order.return_status = 'fully_return'
            else:
                parent_order.return_status = 'partialy_return'

        return order

    @api.model
    def get_status(self, ref):
        order_id = self.search([('pos_reference', '=', ref)], limit=1)
        if order_id.return_status == 'fully_return':
            return False
        return True


class NewPosLines(models.Model):
    _inherit = "pos.order.line"

    returned_qty = fields.Integer(string='Returned', digits=0)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    restrict_return = fields.Boolean('Restrict Return',
        help='Enable restriction of return pos order', default=False)
    return_accepted_in_days = fields.Integer(
        string='Returned Accepted In Days', default=7,)