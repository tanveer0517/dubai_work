# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import requests
import json
import base64
import smtplib
from odoo import exceptions
from odoo.exceptions import ValidationError

class marakez_server_api(models.Model):
    _name = 'marakez.server.api'
    _description = 'Marakez Server API'

    name = fields.Char('Name')

class jwt_authentication(models.Model):
    _name = 'jwt.authentication'
    _description = 'JWT Authentication'

    name = fields.Char('Name')
    userid = fields.Char('User ID')
    password = fields.Char('Password')
    token = fields.Char('Token')
    expiry = fields.Char('Expiry')

    @api.multi
    def get_jwt_authentication(self):
        for rec in self:
            token = ''
            expiry = ''
            if rec.userid and rec.password and rec.name:
                marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
                if marakez_api_rec and marakez_api_rec.name:
                    url = marakez_api_rec.name+rec.name
                    userid = rec.userid
                    password = rec.password
                    payload = {
                            "userid": userid,
                            "password": password
                            }

                    data = json.dumps(payload)
                                    
                    headers = {
                        'content-type': "application/json",
                        'cache-control': "no-cache",
                    }
                    response = requests.request("POST", url, data=data, headers=headers)
                    print "##########response1",response
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "############response2",response
                        if response['status'] == 'SUCCESS':
                            token = response['token']
                            expiry = response['expiry']
                            rec.sudo().write({'token':token,'expiry':expiry})
                    else:
                        raise exceptions.ValidationError(_("JWT Authentication fails"))
                else:
                    raise exceptions.ValidationError(_("Please add marakez server API url."))
        return True