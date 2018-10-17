# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import requests
import json
import base64
import smtplib
from datetime import datetime
from odoo import exceptions
from odoo.exceptions import ValidationError

class saas_portal_new_client(models.Model):
    _inherit = 'saas_portal.new.client'

    @api.multi
    def sync_merchant_marakez(self):
        for rec in self:
            marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
            if marakez_api_rec and marakez_api_rec.name:
                token_id = ''
                token = self.env['jwt.authentication']
                token_rec = token.sudo().search([],limit=1)
                if token_rec:
                    token_id = token_rec.token
                url = marakez_api_rec.name+'erp_merchantregister'
                name = (rec.client_id and rec.client_id.name).split(' ',1)
                firstname = name[0]
                lastname = name[1] if len(name) > 1 else ''
                citycode = self.env['city.city'].sudo().search([('name','=',rec.city),('country_id','=',rec.country_id.id),('state_id','=',rec.state_id and rec.state_id.id)])
                citycode = citycode.code if citycode else ''
                onboarddate = datetime.strptime(rec.create_date,'%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                payload = {
                    "sellercode":rec.request_no,
                    "sellertype":rec.plan_id and rec.plan_id.name,
                    "companyname":rec.company,
                    "companylogo":"https://rukminim1.flixcart.com/image/300/300/jepzrm80/shoe/a/z/e/nm001-8-newport-black-original-imaf3chapbgyrk2h.jpeg?q=70",
                    "phoneno":rec.contact_no,
                    "firstname":firstname,
                    "lastname":lastname,
                    "email":rec.client_email,
                    "address1":rec.street1,
                    "address2":rec.street2,
                    "countrycode":rec.country_id and rec.country_id.code,
                    "statecode":rec.state_id and rec.state_id.code,
                    "citycode":citycode,
                    "pincode":"",
                    "iban":rec.client_bank_iban,
                    "bankname":rec.client_bank_id and rec.client_bank_id.name,
                    "accountno":rec.client_bank_acc,
                    "accountname":"current",
                    "onboarddate":onboarddate,
                    "category":[ "MI2000", "MI200001"]
                    }

                data = json.dumps(payload)
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "############payload",payload
                print "##########headers",headers
                # response = requests.request("POST", url, data=data, headers=headers)
                # if response and response.status_code == 200:
                #     response = json.loads(response.text)
                #     print "##########response1",response
                #     if response['status'] == 'fail':
                #         response = requests.request("PUT", url, data=data, headers=headers)
                #         print "###########response2",response.text
                # else:
                #     token_rec.get_jwt_authentication()
                #     headers = {
                #         'content-type': "application/json",
                #         'Authorization': "Bearer "+token_rec.token,
                #     }
                #     response = requests.request("POST", url, data=data, headers=headers)
                #     if response and response.status_code == 200:
                #         response = json.loads(response.text)
                #         print "##############response2",response
                #         if response['status'] == 'fail':
                #             response = requests.request("PUT", url, data=data, headers=headers)
                #             print "#########updating record",response
            else:
                raise exceptions.ValidationError(_("Please add marakez server API url."))
        return True


