# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import requests
import json
import base64
import smtplib
from odoo import exceptions
from odoo.exceptions import ValidationError

class res_country(models.Model):
    _inherit = 'res.country'

    language_id = fields.Many2one('res.lang','Language')
    active = fields.Boolean('Active')
    is_default = fields.Boolean('Is Default')

    @api.model
    def sync_country_marakez(self,country_ids=None):
        domain = []
        if country_ids:
            domain = [('code','in',country_ids)]
        for rec in self.sudo().search(domain):
            marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
            if marakez_api_rec and marakez_api_rec.name:
                token_id = ''
                token = self.env['jwt.authentication']
                token_rec = token.sudo().search([],limit=1)
                if token_rec:
                    token_id = token_rec.token
                url = marakez_api_rec.name+'erp_countrymaster'
                payload = {
                    "countrycode": rec.code,
                    "countryname": rec.name,
                    "basecurrencycode": rec.currency_id and rec.currency_id.name,
                    "defaultlangcode": rec.language_id and rec.language_id.code,
                    "isActive": rec.active,
                    "isDefault": rec.is_default
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                print "###########response0",response
                if response and response.status_code == 200:
                    print "#######response.text",response.text
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response.text
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
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

class res_country_state(models.Model):
    _inherit = 'res.country.state'

    @api.model
    def sync_state_marakez(self,state_ids=None):
        token_id = ''
        url = ''
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        if marakez_api_rec and marakez_api_rec.name:
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_statemaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        if state_ids:
            for stat in state_ids:
                state_code = stat[0]
                country_code = stat[1]
                state_rec = self.sudo().search([('code','=',state_code),('country_id.code','=',country_code)])
                payload = {
                    "statecode": state_rec.code,
                    "statename": state_rec.name,
                    "description": state_rec.name,
                    "countrycode": state_rec.country_id and state_rec.country_id.code,
                    "isActive": state_rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                if response and response.status_code == 200:
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response.text
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response.text
        else:
            for state_rec in self.sudo().search([]):
                payload = {
                    "statecode": state_rec.code,
                    "statename": state_rec.name,
                    "description": state_rec.name,
                    "countrycode": state_rec.country_id and state_rec.country_id.code,
                    "isActive": state_rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                print "###########response0",response
                print "###########status",response.status_code
                print type(response.status_code)
                if response and response.status_code == 200:
                    print "#######response.text",response.text
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response
                else:
                    print "!!!!!!!!!!!!!!!!!!!!!"
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response
        return True

class city_city(models.Model):
    _inherit = 'city.city'

    @api.model
    def sync_city_marakez(self,city_ids=None):
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        token_id = ''
        url = ''
        if marakez_api_rec and marakez_api_rec.name:
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_citymaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        if city_ids:
            for city in city_ids:
                city_code = city[0]
                state_code = city[1]
                city_rec = self.sudo().search([('code','=',city_code),('state_id.code','=',state_code)])
                payload = {
                    "citycode": city_rec.code,
                    "cityname": city_rec.name,
                    "description": city_rec.name,
                    "statecode": city_rec.state_id and city_rec.state_id.code,
                    "isActive": city_rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                if response and response.status_code == 200:
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response.text
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response
        else:
            for city_rec in self.sudo().search([]):
                payload = {
                    "citycode": city_rec.code,
                    "cityname": city_rec.name,
                    "description": city_rec.name,
                    "statecode": city_rec.state_id and city_rec.state_id.code,
                    "isActive": city_rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                print "###########response0",response
                if response and response.status_code == 200:
                    print "#######response.text",response.text
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response
            
        return True

class res_currency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def sync_currency_marakez(self,currency_ids=None):
        domain = ['|',('active','=',True),('active','=',False)]
        token_id = ''
        url = ''
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        if marakez_api_rec and marakez_api_rec.name:
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_currencymaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        if currency_ids:
            domain.append(('name','in',currency_ids))
        for rec in self.sudo().search(domain):
            payload = {
                "currencycode": rec.name,
                "currencynote": rec.name,
                "currencysymbol": rec.symbol,
                "isActive": rec.active
                }
            data = json.dumps(payload)
            print "##############data",data              
            headers = {
                'content-type': "application/json",
                'Authorization': "Bearer "+token_id,
            }
            print "#################headers",headers
            response = requests.request("POST", url, data=data, headers=headers)
            if response and response.status_code == 200:
                response = json.loads(response.text)
                print "##############response1",response
                if response['status'] == 'fail':
                    response = requests.request("PUT", url, data=data, headers=headers)
                    print "#########updating record",response.text
            else:
                token_rec.get_jwt_authentication()
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_rec.token,
                }
                print "#########headers2",headers
                response = requests.request("POST", url, data=data, headers=headers)
                if response and response.status_code == 200:
                    response = json.loads(response.text)
                    print "##############response2",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response
            
        return True

class city_area(models.Model):
    _inherit = 'city.area'

    latitude = fields.Char('Latitude')
    longitude = fields.Char('Longitude')

    @api.model
    def sync_locality_marakez(self,locality_ids=None):
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        token_id = ''
        if marakez_api_rec and marakez_api_rec.name:
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_locationmaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        if locality_ids:
            for locale in locality_ids:
                code = locale[0]
                city_code = locale[1]
                locale_rec = self.sudo().search([('code','=',code),('city_id.code','=',city_code)])
                payload = {
                    "name": locale_rec.name,
                    "description": locale_rec.name,
                    "pincode": locale_rec.zip,
                    "citycode": locale_rec.city_id and locale_rec.city_id.code,
                    "latitude": locale_rec.latitude or '',
                    "longitude": locale_rec.longitude or '',
                    "isActive": locale_rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                if response and response.status_code == 200:
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response.text
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response    
        else:
            for rec in self.sudo().search([]):
                payload = {
                    "name": rec.name,
                    "description": rec.name,
                    "pincode": rec.zip,
                    "citycode": rec.city_id and rec.city_id.code,
                    "latitude": rec.latitude or '',
                    "longitude": rec.longitude or '',
                    "isActive": rec.is_active
                    }
                data = json.dumps(payload)
                print "##############data",data              
                headers = {
                    'content-type': "application/json",
                    'Authorization': "Bearer "+token_id,
                }
                print "#################headers",headers
                response = requests.request("POST", url, data=data, headers=headers)
                print "###########response0",response
                if response and response.status_code == 200:
                    print "#######response.text",response.text
                    response = json.loads(response.text)
                    print "##############response1",response
                    if response['status'] == 'fail':
                        response = requests.request("PUT", url, data=data, headers=headers)
                        print "#########updating record",response
                else:
                    token_rec.get_jwt_authentication()
                    headers = {
                        'content-type': "application/json",
                        'Authorization': "Bearer "+token_rec.token,
                    }
                    print "#########headers2",headers
                    response = requests.request("POST", url, data=data, headers=headers)
                    if response and response.status_code == 200:
                        response = json.loads(response.text)
                        print "##############response2",response
                        if response['status'] == 'fail':
                            response = requests.request("PUT", url, data=data, headers=headers)
                            print "#########updating record",response
            
        return True