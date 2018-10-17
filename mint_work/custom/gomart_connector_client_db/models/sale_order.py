# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
from gomartapi import *
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    _ORDER_STATUS = [
                      ('0', _('Pendding')),
                      ('1', _('Shipped')),
                      ('2', _('Delivered')),
                      ('3', _('Cancelled')),
                      ('4', _('Returned')),
                      ('5', _('Processing'))
                    ]

    go_mart_order_status = fields.Selection(selection=_ORDER_STATUS, compute="_check_oder_status", string="Order status")
    go_mart_order_id = fields.Integer(string="GoMart Oder ID", readonly="True", help="This will be generated by GoMart.")

    @api.one
    def _check_oder_status(self):
        _state = {"draft":'0', 'sent':'1', 'sale':'2', 'done':'3', 'cancel':'3'}
        self.go_mart_order_status = _state.get(self.state)

    @api.model
    def create(self, vals):
        rec = super(SaleOrder, self).create(vals)
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                order_API = setOrderStatus(
                                            gomart_server.name,
                                            rec.id,  # erp_order_id
                                            rec.go_mart_order_status,  # erp_order_status
                                            rec.company_id.id,  # erp_store_id
                                            rec.company_id.id,  # erp_store_chain_id
                                            )
                # Log
                _logger.warning("\n\n\n" + " Sale Order API : \n" + " Data : " + str(order_API.get('data')) + "\n Status : " + str(order_API.get('status_code')) + "\n json_dump :" + str(order_API.get('json_dump')))
                if (order_API.get("status_code") and order_API.get('json_dump').get('code')) == 200 and order_API.get("order_id"):
                    rec.write({'go_mart_order_id':order_API.get("order_id")})
                else:
                    msg = "GoMart API setOrderStatus having invalid status code %s \n Order JSON dump %s" % str(order_API.get("status_code"), order_API.get("json_dump"))
                    _logger.warning(msg)
#                     raise execeptions.Warning(msg)
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            msg = "GoMart API setOrderStatus is not working or server down"
            _logger.warning(msg)
#             raise exceptions.Warning(msg)
        return rec

    @api.multi
    def write(self, vals):
        rec = super(SaleOrder, self).write(vals)
        try:
            order_API = setOrderStatus(
                                        self.id,  # erp_order_id
                                        self.go_mart_order_status,  # erp_order_status
                                        self.company_id.id,  # erp_store_id
                                        self.company_id.id,  # erp_store_chain_id
                                        )
            # Log
            _logger.warning("\n\n\n" + " Sale Order API : \n" + " Data : " + str(order_API.get('data')) + "\n Status : " + str(order_API.get('status_code')) + "\n json_dump :" + str(order_API.get('json_dump')))
            if (not self.go_mart_order_id) and (order_API.get("status_code") == 200):
                    self.write({'go_mart_order_id':order_API.get("order_id")})
            elif order_API.get("status_code") != 200:
                msg = "GoMart API setOrderStatus having invalid status code %s \n Order JSON dump %s" % str(order_API.get("status_code"), order_API.get("json_dump"))
                _logger.warning(msg)
#                 raise execeptions.Warning(msg)

        except:
            msg = "GoMart API setOrderStatus is not working or server down"
            _logger.warning(msg)
#             raise exceptions.Warning(msg)
        return rec

#     @api.model
#     def Create_SO(self, vals):
#         """
#         Order
#             {go_mart_order_id:'',partner_id:'',company_id:'',name:'',create_date:''
#             state:'',delivery_option:'',amount_untaxed:'',amount_total:'',amount_tax:'',
#             order_value:'',note:'',order_date:''}
#     
#         Invoice
#             {journal_id:'',
#             state:''}
#     
#         Delivery
#             {move_type:'',
#             shipment_date:''}
#     
#         Order_line
#             {tax_ids:''}
# 
#         """
#         if isinstance(vals, dict):
#             print "\n\n\n Vals : ", vals
#             print "\n\n\n"
# 
#             # Order Dictionary 
#             order_dict = vals.get('Order')
#             customer = order_dict.get('customer')
#             partner_id = self.env['res.partner'].search([('name', '=', str(customer.get('name')))], limit=1)
# 
#             if partner_id:
#                 return ({"odoo_customer_id":partner_id.id})
#             else:
#                 rec = self.env['res.partner'].create({'name':customer.get('name'),
#                                                       'firstname':customer.get('firstname'),
#                                                       'lastname':customer.get('lastname'),
#                                                       'email':customer.get('email'),
#                                                       'mobile':customer.get('mobile'),
#                                                       'phone':customer.get('phone'),
#                                                       'dob':customer.get('dob'),
#                                                       })
#                 return ({"odoo_customer_created_id":rec.id})
#                 return customer.get('name')

#             sale_order = super(SaleOrder, self).create(vals.get('order'))
#             print "\n\n\n Sale Order : ", sale_order
#         self.write(vals)
#         self.action_confirm()
#         self.action_invoice_create()
#         new_so_rec.create_sales_order()
#         return sale_order

#     @api.multi
#     def Browse_SO(self):
#         sale_order = self.env["sale.order"].search([('id', '=', '2')], limit=1)
#         print "\n\n\n Search SO : ", sale_order
#         print "\n\n\n Context", self._context
#         print "\n\n\n Read SO record : ", sale_order.read()
#         for x in sale_order.read():
#             print " Sale Order  : ", x.keys()
# 
#     @api.multi
#     def Read_SO(self, id=False):
#         if id: 
#             return (self.search([('id', '=', id)], limit=1).read())
#         else:
#             return self.read()
# 
#     @api.multi
#     def Master_field_SO(self):
#         for x in self.read():
#             print "Master Field ", x.keys()
#             raise exceptions.Warning()
