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


class ResCompany(models.Model):
    _inherit = 'res.company'

    gomart_store_field_id = fields.Integer("GoMart field id",
                                             readonly="True",
                                             help="This field is generated by from the GoMart.")

    return_order = fields.Boolean(default="False",
                                  string="Return Order",
                                  help="Return Order")

    @api.multi
    def Update_extra_details(self):
        _delivery_flag = {True:1, False:0}
        _return_order = {True:2, False:1}
        _status = {'one':1, 'zero':0}

        store_chain_id = 0
        if self.parent_id:
            store_chain_id = self.parent_id.id

        _Extra_time = ({
                        "erp_field_id": self.id,  # erp_field_id
                        "erp_store_id":self.id,  # erp_store_id
                        "erp_store_chain_id":store_chain_id,  # erp_store_chain_id
                        "erp_order_prefix":self.other_prefix,  # erp_order_prefix
                        "erp_min_order_amt":self.min_order_amt,  # erp_min_order_amt
                        "erp_delivery_charge":self.delivery_charge or 0.0,  # erp_delivery_charge
                        "erp_delivery_min_flag":_delivery_flag.get(self.delivery_charge_below),  # erp_delivery_min_flag [ 1-Delivery charge below Min order amount selected ]
                        "erp_delivery_min_amount":self.deli_charge_below_order or 0.0,  # erp_delivery_min_amount [float]
                        "erp_delivery_min_message":self.min_del_order_message or '',  # erp_delivery_min_message
                        "erp_take_back_flag":_return_order.get(self.return_order),  # erp_take_back_flag [1-Not to be returned,2-Returned]
                        "erp_delivery_duration":self.delivery_duration or '',  # erp_delivery_duration
                        "erp_terms":self.terms_and_conditions or '',  # erp_terms
                     })
        """
         STORE TIMING 
        """

        for days in self.store_time_ids:
            if days.dayofweek == "0":
                _Extra_time.update({"mon_status":_status.get(days.store_status), "mon_from":self._time(days.hour_from), "mon_to":self._time(days.hour_to)})
            elif days.dayofweek == "1":
                _Extra_time.update({"tue_status":_status.get(days.store_status), "tue_from":self._time(days.hour_from), "tue_to":self._time(days.hour_to)})
            elif days.dayofweek == "2":
                _Extra_time.update({"wed_status":_status.get(days.store_status), "wed_from":self._time(days.hour_from), "wed_to":self._time(days.hour_to)})
            elif days.dayofweek == "3":
                _Extra_time.update({"thurs_status":_status.get(days.store_status), "thurs_from":self._time(days.hour_from), "thurs_to":self._time(days.hour_to)})
            elif days.dayofweek == "4":
                _Extra_time.update({"fri_status":_status.get(days.store_status), "fri_from":self._time(days.hour_from), "fri_to":self._time(days.hour_to)})
            elif days.dayofweek == "5":
                _Extra_time.update({"satur_status":_status.get(days.store_status), "satur_from":self._time(days.hour_from), "satur_to":self._time(days.hour_to)})
            elif days.dayofweek == "6":
                _Extra_time.update({"sun_status":_status.get(days.store_status), "sun_from":self._time(days.hour_from), "sun_to":self._time(days.hour_to)})

        auth_token = self.env["auth.oauth.provider"].search([('name', '=', 'SaaS'), ('enabled', '=', 'True')], limit=1)
        if auth_token and auth_token.client_id:
            _Extra_time.update({"erp_reg_id":auth_token.client_id})
        else:
            _logger.warning("SaaS token is not present")

        # PAYMENT OPTIONS 
        """
        erp_pay_options (array [{1,’’},{4,’Sodexo’}]) – First Value if Pay Type, Second
        value is pay type text incase pay type is 4.
        Possible Pay Type IDS: 1 – Cash, 2- Online, 3 – Debit/Credit Card, 4 - Others
        """
        _journal = {"cash":1, "bank":3}
        _journal_name = {1:'Cash', 3:'Debit/Credit Card', 2:'Online', 4:'Card on delivery'}
        journal_list = []
        payoption = ''
        if self.payment_option:
            for payment in self.payment_option:
                journal_list.append(str(_journal.get(payment.type)) + "=>" + "'" + str(_journal_name.get(_journal.get(payment.type))) + "'") 
            payoption = "array(" + str(",".join(journal_list)) + ")"
            _Extra_time.update({"erp_pay_options":payoption})

        # API setStoreExtras
        store_extra = self._setStoreExtras(_Extra_time)
        return True

    def _setStoreExtras(self, values):
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                if isinstance(values, dict):
                    store_extra_API = setStoreExtras(
                                                gomart_server.name,
                                                values.get('erp_field_id') or 0,
                                                values.get('erp_store_id') or 0,
                                                values.get('erp_store_chain_id') or 0,
                                                values.get('erp_order_prefix') or '',
                                                values.get('erp_min_order_amt') or 0,
                                                values.get('erp_delivery_charge') or 0,
                                                values.get('erp_delivery_min_flag'),
                                                values.get('erp_delivery_min_amount') or 0,
                                                values.get('erp_delivery_min_message') or '',
                                                values.get('erp_take_back_flag'),
                                                values.get('erp_delivery_duration'),
                                                values.get('erp_terms'),
                                                values.get('mon_status'),
                                                values.get('mon_from'),
                                                values.get('mon_to'),
                                                values.get('tue_status'),
                                                values.get('tue_from'),
                                                values.get('tue_to'),
                                                values.get('wed_status'),
                                                values.get('wed_from'),
                                                values.get('wed_to'),
                                                values.get('thurs_status'),
                                                values.get('thurs_from'),
                                                values.get('thurs_to'),
                                                values.get('fri_status'),
                                                values.get('fri_from'),
                                                values.get('fri_to'),
                                                values.get('satur_status'),
                                                values.get('satur_from'),
                                                values.get('satur_to'),
                                                values.get('sun_status'),
                                                values.get('sun_from'),
                                                values.get('sun_to'),
                                                values.get('erp_reg_id'),
                                                values.get('erp_pay_options'),
                                                )
                    # Log
                    _logger.warning("\n\n\n" + " Store Extras  API : \n\n\n" + " Data : " + str(store_extra_API.get('data')) + 
                                    "\n\n\n Status : " + str(store_extra_API.get('status_code')) + "\n\n\n json_dump :" + str(store_extra_API.get('json_dump')) + "\n\n\n" + "payload: " + str(store_extra_API.get('payload')) + '\n\n\n')
                    if (store_extra_API.get('status_code') and store_extra_API.get('json_dump').get('code')) == 200 and store_extra_API.get('status_code'):
                        self.write({'gomart_store_field_id' :store_extra_API.get('store_field_id')})
                    else:
                        _logger.warning('GoMart API setStoreExtras, invalid status code is %s' % str(store_extra_API.get('json_dump').get('code')))
                else:
                    _logger.warning('For the SetStoreExtra API,data must be dict type data ')
            else:
                msg = "Please update correct GoMart APi server."
                _logger.warning(msg)
        except:
            msg = "GoMart APi SetStoreExtra is not working or server down."
            _logger.warning(msg)
        return True

    def _time(self, time):
        if time > 0:
            time1 = str(time).split('.')[-1][:2]  # if last digit is greater then 50
            if int(time1) > 30:
                return str(int(str(time).split('.')[0]) + 1) + ":" + "00"
            elif int(time1) > 0 and int(time1) < 30:
                return str(int(str(time).split('.')[0])) + ":" + "30"
            else:
                return str(int(str(time).split('.')[0])) + ":" + "00"
