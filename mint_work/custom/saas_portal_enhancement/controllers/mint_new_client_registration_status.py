# -*- coding: utf-8 -*-
import base64
import json
import copy

from odoo import http
from odoo.http import request


class BistaPlanSubscription(http.Controller):

    # Route to display the "MY Status" Page on Portal
    @http.route(['/new_registration_status'], type='http', auth='user',
                website=True)
    def new_registration_status(self, **post):
        new_registration_obj = request.env['saas_portal.new.client']
        res_user_obj = request.env['res.users']
        user_rec =  res_user_obj.browse(request.uid)
        client_rec = new_registration_obj.search([('client_id', '=',
                                                   user_rec.id)], limit=1)

        values = {}
        if client_rec:
            values = {
                'client_rec': client_rec,
                'user_id': user_rec,
            }
        return http.request.render(
            "saas_portal_enhancement.new_registration_status", values)

    # Route to Upload the User Documents from Portal to Backend New
    # Registration Request of the user record
    @http.route(['/confirmed_update'], type='http', auth='user', website=True)
    def document_update_confirm(self, **post):
        vals = {}
        params = dict(request.params)

        client_obj = request.env['saas_portal.new.client']
        client_rec = client_obj.sudo().browse(int(params.get('client_id')))

        if client_rec:
            if request.params.get('emirates_id_card' or False):
                emirates_id_card = request.params['emirates_id_card']
                vals.update({
                    'emirates_id_card' :
                        base64.encodestring(emirates_id_card.read()),
                    'emirates_id_card_name' : str(emirates_id_card.filename),
                    'emirates_id_card_rejected': False,
                    'emirates_id_card_rejected_state' : 'updated',
                })
            if request.params.get('passport_and_poa' or False):
                passport_and_poa = request.params['passport_and_poa']
                vals.update({
                    'passport_and_poa' :
                        base64.encodestring(passport_and_poa.read()),
                    'passport_and_poa_name' : str(passport_and_poa.filename),
                    'passport_and_poa_rejected': False,
                    'passport_and_poa_rejected_state' : 'updated',
                })
            if request.params.get('vat_num' or False):
                vat_num = request.params['vat_num']
                vals.update({
                    'vat_num' : base64.encodestring(vat_num.read()),
                    'vat_num_name' : str(vat_num.filename),
                    'vat_num_rejected' : False,
                    'vat_num_rejected_state' : 'updated',
                })
            if request.params.get('visa_and_poa' or False):
                visa_and_poa = request.params['visa_and_poa']
                vals.update({
                    'visa_and_poa' : base64.encodestring(visa_and_poa.read()),
                    'visa_and_poa_name' : str(visa_and_poa.filename),
                    'visa_and_poa_rejected' : False,
                    'visa_and_poa_rejected_state' : 'updated',
                })
            if request.params.get('operating_address_uae' or False):
                operating_address_uae = request.params['operating_address_uae']
                vals.update({
                    'operating_address_uae' :
                        base64.encodestring(operating_address_uae.read()),
                    'operating_address_uae_name' :
                        str(operating_address_uae.filename),
                    'operating_address_uae_rejected' : False,
                    'operating_address_uae_rejected_state' : 'updated',
                })
            if request.params.get('trade_license' or False):
                trade_license = request.params['trade_license']
                vals.update({
                    'trade_license' : base64.encodestring(trade_license.read()),
                    'trade_license_name' : str(trade_license.filename),
                    'trade_license_rejected' : False,
                    'trade_license_rejected_state' : 'updated',
                })

            vals.update({
                'state': 'document_approval',
            })
            client_rec.write(vals)
        return http.request.render(
            "saas_portal_enhancement.client_docuemnt_updated")
