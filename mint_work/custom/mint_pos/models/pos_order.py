# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import datetime
from odoo.tools import float_is_zero


class PosOrderReject(models.TransientModel):
    _name = 'pos.order.reject'

    reject_reason = fields.Text(string="Reject Reason")

    #Reject order with reason and mail will be sent to customer.
    @api.one
    def reject_reason_pos(self):
        if self._context.get('active_id'):
            pos_order_rec = self.env['pos.order'].browse(self._context.get('active_id'))
            pos_order_rec.write({'reject_reason':self.reject_reason,'state':'cancel'})
            rejection_template_id = self.env['ir.model.data'].get_object('mint_pos',
                                                                     'email_template_reject_pos_order')
            if rejection_template_id:
                if pos_order_rec.partner_id.email:
                    rejection_template_id.send_mail(pos_order_rec.id, force_send=True,
                                                email_values={'email_to': pos_order_rec.partner_id.email})
                else:
                    raise UserError(_("Your customer have not Email id!!! "))


class PosOrder(models.Model):
    _inherit = "pos.order"

    reject_reason = fields.Text(string="Reject Reason")

    #Inherited Create picking to support return order functionality.
    def create_picking(self):
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': order.name,
                    'partner_id': address.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    order_picking.message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    return_picking.message_post(body=message)

            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
                moves |= Move.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)
                for pack in order_picking.pack_operation_product_ids:
                    pack.write({'qty_done':pack.product_qty})
                order_picking.do_new_transfer()

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                tracked_moves = moves.filtered(lambda move: move.product_id.tracking != 'none')
                untracked_moves = moves - tracked_moves
                tracked_moves.action_confirm()
                untracked_moves.action_assign()
                moves.filtered(lambda m: m.state in ['confirmed', 'waiting']).force_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none').action_done()
        return True


class sale_order(models.Model):
    _inherit = "sale.order"

    #Accept the sale order and send sale acceptance mail to customer.
    @api.model
    def update_so(self, vals={}):
        if vals.get('order_id', False):
            order = self.browse(vals['order_id'])
            if not order.partner_email or not vals.get('pos_config_id',False):
                return
            pos_config_rec = self.env['pos.config'].browse(vals['pos_config_id'])
            accept_reason_template_id = pos_config_rec.accept_reason_template_id and pos_config_rec.accept_reason_template_id.id or False
            if not accept_reason_template_id:
                return {
                    'error': "Please contact your Administrator. Missing Accept Reason Email Template configuration."
                }
            order.is_accepted = vals.get('is_accepted', False)
            self.env['mail.template'].browse(accept_reason_template_id).with_context(lang=order.partner_id.lang).send_mail(order.id, force_send=True,raise_exception=False)
            return True
        return False

    #Reject the sale order and send sale rejection mail to customer.
    #Based on payment status of the order if there are invoice related to this order,
    #It will also cancel its related invoice and if needed it will create a refund.
    @api.model
    def set_cancel_order(self, vals={}):
        ctx = self.env.context.copy()
        if vals.get('order_id', False):
            invoice_refund_obj = self.env['account.invoice.refund']
            order = self.browse(vals['order_id'])
            if not order.partner_email or not vals.get('pos_config_id',False):
                return
            pos_config_rec = self.env['pos.config'].browse(vals['pos_config_id'])
            reject_reason_template_id = pos_config_rec.reject_reason_template_id and pos_config_rec.reject_reason_template_id.id or False
            if not reject_reason_template_id:
                return {
                    'error': "Please contact your Administrator. Missing Reject Reason Email Template configuration."
                }
            if vals.get('reject_reason',False):
                order.note = vals.get('reject_reason','')
            invoices = order.invoice_ids.filtered(
                    lambda invoice: invoice.state not in ['cancel'])
            ctx.update({
                'active_id': inv.id,
                'active_ids': [inv.id],
            })
            refund_vals = {
                'description': vals.get('reject_reason',''),
                'date':datetime.date.today(),
                'filter_refund':'refund'
            }
            if order.payment_status == 'unpaid':
                for inv in invoices:
                    if inv.state in ['proforma2', 'draft', 'open']:
                        inv.action_invoice_cancel()
                    if inv.state == 'paid':
                        acc_inv_refund = invoice_refund_obj.create(refund_vals)
                        acc_inv_refund.with_context(ctx).invoice_refund()
            if order.payment_status == 'paid':
                for inv in invoices:
                    if inv.state == 'paid':
                        acc_inv_refund = invoice_refund_obj.create(refund_vals)
                        acc_inv_refund.with_context(ctx).invoice_refund()
            order.action_cancel()
            self.env['mail.template'].browse(reject_reason_template_id).with_context(lang=order.partner_id.lang).send_mail(order.id, force_send=True,raise_exception=False)
            return True
        return False

    #Calculate the amount due and set payment status.
    #If amount due is 0 payment status will be paid else it will be unpaid.
    @api.one
    @api.depends('invoice_ids', 'invoice_ids.residual')
    def _calculate_amount_due(self):
        total = 0.00
        invoices = self.invoice_ids.filtered(
            lambda invoice: invoice.state not in ['cancel'])
        for invoice in invoices:
            total += invoice.state in ('draft') and invoice.amount_total or \
            invoice.residual
        if not invoices:
            total = self.amount_total
        payment_status = 'unpaid'
        if invoices and total <= 0.0:
            payment_status = 'paid'
        self.amount_due = total
        self.payment_status = payment_status

    #Checks if all the pickings related to this order is done than mark this order as shipped.
    @api.one
    @api.depends('picking_ids', 'picking_ids.state')
    def _check_shipped(self):
        for picking in self.picking_ids:
            all_delivered = True
            if picking.state != "done":
                all_delivered = False
            self.is_shipped = all_delivered

    #Set delivery status completed if order is shipped.
    @api.one
    @api.depends('is_shipped')
    def _compute_delivery_status(self):
        self.delivery_status = 'pending'
        if self.is_shipped:
            self.delivery_status = 'completed'

    partner_email = fields.Char("Partner Email", related="partner_id.email")
    amount_due = fields.Float("Amount Due", compute="_calculate_amount_due")
    is_accepted = fields.Boolean('Is Accepted')
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ], string='Payment Status', default='unpaid', compute="_calculate_amount_due")
    is_shipped = fields.Boolean('Is shipped', compute="_check_shipped")
    delivery_status = fields.Selection([
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ], string='Delivery Status', default='pending', compute="_compute_delivery_status")
    order_type = fields.Selection([
        ('offline', 'Offline'),
        ('online', 'Online'),
    ], string='Order Type', default='offline')

    #Used to create or update the sale order.
    #Return sale order data.
    @api.model
    def create_sales_order(self, vals):
        sale_pool = self.env['sale.order']
        prod_pool = self.env['product.product']
        sale_line_pool = self.env['sale.order.line']
        customer_id = vals.get('customer_id')
        orderline = vals.get('orderlines')
        journals = vals.get('journals')
        location_id = vals.get('location_id')
        sale_id = False

        if journals and vals.get('amount_return'):
            journals[0]['amount_return'] = vals.get('amount_return')

        if not vals.get('sale_order_id'):
            if customer_id:
                customer_id = int(customer_id)
                sale = {
                    'partner_id': customer_id,
                    'partner_invoice_id': vals.get('partner_invoice_id', customer_id),
                    'partner_shipping_id': vals.get('partner_shipping_id', customer_id),
                    'from_pos': True,
                    'date_order': vals.get('order_date') or datetime.datetime.now().strftime ("%Y-%m-%d"),
                    'note': vals.get('note') or '',
                }
                new = sale_pool.new({'partner_id': customer_id})
                new.onchange_partner_id()
                if vals.get('pricelist_id'):
                    sale.update({'pricelist_id': vals.get('pricelist_id')})
                if vals.get('partner_shipping_id'):
                    sale.update({'partner_shipping_id': vals.get('partner_shipping_id')})
                if vals.get('partner_invoice_id'):
                    sale.update({'partner_invoice_id': vals.get('partner_invoice_id')})
                sale_id = sale_pool.create(sale)
                #create sale order line
                sale_line = {'order_id': sale_id.id}
                for line in orderline:
                    prod_rec = prod_pool.browse(line['product_id'])
                    sale_line.update({'name': prod_rec.name or False,
                                      'product_id': prod_rec.id,
                                      'product_uom_qty': line['qty'],
                                      'discount': line.get('discount')})
                    new_prod = sale_line_pool.new({'product_id': prod_rec.id})
                    prod = new_prod.product_id_change()
                    sale_line.update(prod)
                    sale_line.update({'price_unit': line['price_unit']});
                    taxes = map(lambda a: a.id, prod_rec.taxes_id)
                    if sale_line.get('tax_id'):
                        sale_line.update({'tax_id': sale_line.get('tax_id')})
                    elif taxes:
                        sale_line.update({'tax_id': [(6, 0, taxes)]})
                    sale_line.pop('domain')
                    sale_line.update({'product_uom': prod_rec.uom_id.id})
                    sale_line_pool.create(sale_line)

                if self._context.get('confirm'):
                    sale_id.action_confirm()
                if self._context.get('paid'):
                    sale_id.action_confirm()
                    for picking_id in sale_id.picking_ids:
                        if not picking_id.delivery_order(location_id):
                            return False
                    if not sale_id._make_payment(journals):
                        return False

        elif vals.get('sale_order_id') and vals.get('edit_quotation'):
            if customer_id:
                customer_id = int(customer_id)
                sale_id = self.browse(vals.get('sale_order_id'))
                if sale_id:
                    vals = {
                        'partner_id': customer_id,
                        'partner_invoice_id': vals.get('partner_invoice_id', customer_id),
                        'partner_shipping_id': vals.get('partner_shipping_id', customer_id),
                        'from_pos': True,
                        'date_order': vals.get('order_date') or datetime.datetime.now().strftime ("%Y-%m-%d"),
                        'note': vals.get('note') or '',
                        'pricelist_id': vals.get('pricelist_id') or False
                    }
                    sale_id.write(vals)
                    [line.unlink() for line in sale_id.order_line]
                    sale_line = {'order_id': sale_id.id}
                    for line in orderline:
                        prod_rec = prod_pool.browse(line['product_id'])
                        sale_line.update({'name': prod_rec.name or False,
                                          'product_id': prod_rec.id,
                                          'product_uom_qty': line['qty'],
                                          'discount': line.get('discount')})
                        new_prod = sale_line_pool.new({'product_id': prod_rec.id})
                        prod = new_prod.product_id_change()
                        sale_line.update(prod)
                        sale_line.update({'price_unit': line['price_unit']});
                        taxes = map(lambda a: a.id, prod_rec.taxes_id)
                        if sale_line.get('tax_id'):
                            sale_line.update({'tax_id': sale_line.get('tax_id')})
                        elif taxes:
                            sale_line.update({'tax_id': [(6, 0, taxes)]})
                        sale_line.pop('domain')
                        sale_line.update({'product_uom': prod_rec.uom_id.id})
                        sale_line_pool.create(sale_line)
                    if journals:
                        if sale_id.state in ['draft', 'sent']:
                            sale_id.action_confirm()
                            # for picking_id in sale_id.picking_ids:
                            #     if not picking_id.delivery_order(location_id):
                            #         return False
                        for picking_id in sale_id.picking_ids:
                            if picking_id.state != "done":
                                if not picking_id.delivery_order(location_id):
                                    return False
                        sale_id._make_payment(journals)

        elif vals.get('sale_order_id') and not vals.get('edit_quotation'):
            sale_id = self.browse(vals.get('sale_order_id'))
            if sale_id:
                inv_id = False
                if vals.get('inv_id'):
                    inv_id = vals.get('inv_id')
                if sale_id.state in ['draft', 'sent']:
                    sale_id.action_confirm()
                for picking_id in sale_id.picking_ids:
                    if picking_id.state != "done":
                        if not picking_id.delivery_order(location_id):
                            return False
                sale_id._make_payment(journals)
        if not sale_id:
            return  False
        if sale_id._action_order_lock():
            sale_id.action_done()
        return sale_id.read()

    #Used to crete or update the invoice.
    @api.multi
    def _make_payment(self, journals):
        if not self.invoice_ids or self.invoice_status == "to invoice":
            try:
                self.action_invoice_create()
            except Exception, e:
                raise
        if not self.generate_invoice(journals):
            return False
        return True

    #Checkes the invoice state and delivery state.
    #If any invoice is not in paid or delivery is not done that return true else retur false.
    def _action_order_lock(self):
        if not self.invoice_ids:
            return False
        inv = [invoice.id for invoice in self.invoice_ids if invoice.state != "paid"]
        picking = [invoice.id for picking in self.picking_ids if picking.state != "done"]
        if self and not inv and not picking:
            return True
        return False

    #Create a payment of unpaid invoices and post the payment.
    @api.model
    def generate_invoice(self, journals):
        invoices = []
        if self.invoice_ids:
            for account_invoice in self.invoice_ids:
                account_invoice.action_invoice_open()
                if account_invoice.state != "paid":
                    invoices.append(account_invoice.id)
            account_payment_obj = self.env['account.payment']
            for journal in journals:
                account_journal_obj= self.env['account.journal'].browse(journal.get('journal_id'))
                if account_journal_obj:
                    payment_id = account_payment_obj.create({
                                               'payment_type': 'inbound',
                                               'partner_id': account_invoice.partner_id.id,
                                               'partner_type': 'customer',
                                               'journal_id': account_journal_obj.id or False,
                                               'amount': journal.get('amount'),
                                               'payment_method_id': account_journal_obj.inbound_payment_method_ids.id,
                                               'invoice_ids': [(6, 0, invoices)],
                                               })
                    payment_id.post()

                    # cash return journal entry
                    if journal.get('amount_return'):
                        return_payment_id = account_payment_obj.create({
                            'payment_type': 'outbound',
                            'partner_id': account_invoice.partner_id.id,
                            'partner_type': 'customer',
                            'journal_id': account_journal_obj.id or False,
                            'amount': journal.get('amount_return'),
                            'payment_method_id': account_journal_obj.outbound_payment_method_ids.id,
                        })
                        return_payment_id.post()

            return True
        return False


class StockPicking(models.Model):
    _inherit="stock.picking"

    #Set location on pack operation and write location in move lines.
    def delivery_order(self, location_id):
        if not self:
            return False
        if location_id:
            self.pack_operation_product_ids.write({'location_id':location_id})
            self.move_lines.write({'location_id':location_id})
        self.action_confirm()
        self.force_assign()
        self.do_new_transfer()
        stock_transfer_id = self.env['stock.immediate.transfer'].search([('pick_id', '=', self.id)], limit=1)
        if stock_transfer_id:
            stock_transfer_id.process()
        return True


class PosCategory(models.Model):
    """Product Category"""
    _inherit = 'pos.category'

    category_id = fields.Char(string='Reference No',default=lambda self: _('New'))
    server_id = fields.Many2one('saas_portal.server', 'Server name')
    allow_product = fields.Boolean("Allow Product",default=True)

    @api.constrains('server_id')
    def _check_server(self) :
        for category in self :
            if not category.server_id :
                raise ValidationError(
                    _("Server must be configured on the Category."))
        return True

    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['category_id'] = self.env['ir.sequence'].next_by_code('pos.category') or _('New')
        result = super(PosCategory, self).create(vals)
        return result


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sale_order_last_days = fields.Integer(
        string='Sale Order Last Days', default=1,
        help="This field used to defined how old sale orders from current date you need to display in pos.")
    accept_reason_template_id = fields.Many2one(
        'mail.template', "Accept Reason Mail Template",
        help="If set, a message is posted on the customer using the template when the user accepts the order.")
    reject_reason_template_id = fields.Many2one(
        'mail.template', "Reject Reason Mail Template",
        help="If set, a message is posted on the customer using the template when the user rejects the order.")
    allow_online_orders = fields.Boolean("Allow Online Orders", default=False,
                                         help="Allow online orders to be processed from pos.")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create_contact_from_ui(self, partner_dict):
        """ create a contact from the point of sale ui.
            partner_dict contains the partner's fields. """
        res = {'ship_contact_id': False,
               'invoice_contact_id': False,
               }
        if partner_dict.get('create_shipping_contact', False):
            ship_contact_id = self.create(partner_dict.get('ship_contact_vals',{})).id
            res.update({'ship_contact_id': ship_contact_id})
        if partner_dict.get('create_invoice_contact', False):
            invoice_contact_id = self.create(partner_dict.get('invoice_contact_vals',{})).id
            res.update({'invoice_contact_id': invoice_contact_id})
        return res
