# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import requests
import json
import base64
import smtplib
from odoo import exceptions
from odoo.exceptions import ValidationError

class res_lang(models.Model):
    _inherit = 'res.lang'

    #server_id = fields.Many2one('saas_portal.server','Server')
    is_default = fields.Boolean('Is Default')

    @api.model
    def sync_language_marakez(self,lang_ids=None):
        #lang ids (['en_US','aa'],)
        domain = ['|',('active','=',True),('active','=',False)]
        if lang_ids:
            domain.append(('code','in',lang_ids))
        lang_rec_ids = self.sudo().search(domain)
        for rec in lang_rec_ids:
            marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
            if marakez_api_rec and marakez_api_rec.name:
                token_id = ''
                token = self.env['jwt.authentication']
                token_rec = token.sudo().search([],limit=1)
                if token_rec:
                    token_id = token_rec.token
                url = marakez_api_rec.name+'erp_languagemaster'
                payload = {
                    "langName": rec.name,
                    "langCode": rec.iso_code,
                    "langDescription": rec.name,
                    "isActive": rec.active,
                    "isDefault": rec.is_default
                    }
                data = json.dumps(payload)
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "############payload",payload
                print "##########headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                if response and response.status_code == 200:
                    response = json.loads(response.text)
                    print "##########response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "###########response2",response.text
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response
            else:
                raise exceptions.ValidationError(_("Please add marakez server API url."))
        return True


