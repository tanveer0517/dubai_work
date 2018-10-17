# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import requests
import json
import base64
import smtplib
from odoo import exceptions
from odoo.exceptions import ValidationError

class product_brand(models.Model):
    _inherit = 'product.brand'

    brand_code = fields.Char('Brand Code')
    brand_lang_name = fields.One2many('brand.language.name','brand_id','Brand Lang Name')
    brand_img_url = fields.Char('Brand Image Url')

    @api.model
    def create(self,vals):
        brand_code = vals.get('brand_code')
        if brand_code:
            brand_id = self.sudo().search([('brand_code','=',brand_code)])
            if brand_id:
                raise exceptions.ValidationError(_("Duplicate Brand Code."))
        rec = super(product_brand, self).create(vals)
        return rec

    @api.model
    def sync_brand_marakez(self,brand_code=None):
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        if marakez_api_rec and marakez_api_rec.name:
            token_id = ''
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_brandmaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        domain = ['|',('active','=',True),('active','=',False)]
        if brand_code:
            domain.append(('brand_code','in',brand_code))
        brand_rec_ids = self.sudo().search(domain)
        for rec in brand_rec_ids:
            brand_name = []
            if rec.brand_lang_name:
                for brand in rec.brand_lang_name:
                    brand_name.append({"lang":brand.language_id and brand.language_id.code,"val":brand.name})
            payload = {
                "brandcode": rec.brand_code,
                "image": rec.brand_img_url,
                "brandname": brand_name,
                "description": brand_name,
                "isActive": rec.active
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
                        print "#########updating record",response.text
        
        return True

class brand_language_name(models.Model):
    _name = 'brand.language.name'
    _description = 'Brand Language Name'

    brand_id = fields.Many2one('product.brand','Brand ID')
    language_id = fields.Many2one('res.lang','Language')
    name = fields.Char('Name')


class product_category(models.Model):
    _inherit = 'product.category'

    sequence_no = fields.Char('Sequence Number')
    category_lang_name = fields.One2many('product.category.language.name','brand_id','Brand Lang Name')
    category_img_url = fields.Char('Product Category Image Url')

    @api.onchange('sequence_no')
    def onchange_sequence_no(self):
        if self.sequence_no:
            try:
                sequence_no = int(self.sequence_no)
            except ValueError:
                raise exceptions.ValidationError(_('Please enter valid Sequence Number. It should not contain characters.'))

    @api.model
    def create(self,vals):
        sequence_no = vals.get('sequence_no')
        if sequence_no:
            try:
                sequence_no = int(sequence_no)
            except ValueError:
                raise exceptions.ValidationError(_('Please enter valid Sequence Number. It should not contain characters.'))
        rec = super(product_category, self).create(vals)
        return rec

    @api.multi
    def write(self,vals):
        sequence_no = vals.get('sequence_no')
        if sequence_no:
            try:
                sequence_no = int(sequence_no)
            except ValueError:
                raise exceptions.ValidationError(_('Please enter valid Sequence Number. It should not contain characters.'))
        super(product_category, self).write(vals)
        return True

    @api.model
    def sync_category_marakez(self,category_code=None):
        domain = []
        marakez_api_rec = self.env['marakez.server.api'].sudo().search([],limit=1)
        if marakez_api_rec and marakez_api_rec.name:
            token_id = ''
            token = self.env['jwt.authentication']
            token_rec = token.sudo().search([],limit=1)
            if token_rec:
                token_id = token_rec.token
            url = marakez_api_rec.name+'erp_categorymaster'
        else:
            raise exceptions.ValidationError(_("Please add marakez server API url."))
        if category_code:
            domain.append(('reference_id','in',category_code))
        categ_rec_ids = self.sudo().search(domain)
        for rec in categ_rec_ids:
            categ_name = []
            if rec.category_lang_name:
                for categ in rec.category_lang_name:
                    categ_name.append({"lang":categ.language_id and categ.language_id.code,"val":categ.name})
            payload = {
                "categorycode": rec.reference_id,
                "image": rec.category_img_url,
                "parent_id": rec.parent_id and rec.parent_id.reference_id or "",
                "sequenceno": rec.sequence_no,
                "categoryname": brand_name,
                "description": brand_name,
                "isActive": rec.active
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
                        print "#########updating record",response.text
        
        return True

class product_category_language_name(models.Model):
    _name = 'product.category.language.name'
    _description = 'Product Category Language Name'

    brand_id = fields.Many2one('product.category','Category ID')
    language_id = fields.Many2one('res.lang','Language')
    name = fields.Char('Name')