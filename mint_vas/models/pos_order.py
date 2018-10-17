# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo import exceptions
from odoo.exceptions import ValidationError     
import requests
import json
import base64
import smtplib
from pyDes import *
from binascii import unhexlify as unhex
from binascii import hexlify as hexi
import jxmlease

class pos_order(models.Model):
    _inherit = 'pos.order'

    reference_number = fields.Char('Reference Number')
    transaction_number = fields.Char('Transaction Number')

    @api.model
    def _order_fields(self, ui_order):
        fields = super(pos_order, self)._order_fields(ui_order)
        fields['reference_number'] = ui_order.get('reference_number', False)
        fields['transaction_number'] = ui_order.get('transaction_number', False)
        print ">>>>>fields>>>>", fields
        return fields

    @api.model
    def get_product_name(self,prod_id):
        print "#########prod_id",prod_id
        product_rec_ids = self.env['product.template'].sudo().search([('id','=',prod_id)],limit=1)
        res = []
        for rec in product_rec_ids:
            res.append(rec.categ_id.name)
        print "#########res",res
        return res

    @api.model
    def get_du_topup(self,args):
        result = {}
        param = self.env['ir.config_parameter']
        base_url = param.search([('key', '=', 'web.base.url')]).value
        url = base_url+'/vasapi/du-direct-topup'
        headers = {'Content-Type': 'application/json'}
        partner_rec = self.env['res.partner'].sudo().search([('id','=',args[0])])
        mobile_no = partner_rec.phone or partner_rec.mobile
        data = {
            "fields": {
                "mobileNo": mobile_no,
                "amount": args[1]
            }
        }
        payload = {'params': data}
        data_json = json.dumps(payload)
        print "########payload",payload
        print "#########data_json",data_json
        res = requests.get(url=url, data=data_json, headers=headers)
        response = json.loads(res.text)
        print "##############res",response
        resp_result = response['result']
        print "###########resp_result"
        if resp_result:
            xml_doc = str(resp_result)
            root = jxmlease.parse(xml_doc)
            print "########root",root
            status_code = root['soap:Envelope']['soap:Body']['DuDirectTopUp1Response']['StatusCode'].get_cdata()
            status_desc = root['soap:Envelope']['soap:Body']['DuDirectTopUp1Response']['StatusDescription'].get_cdata()
            receipt_num = root['soap:Envelope']['soap:Body']['DuDirectTopUp1Response']['ReceiptNo'].get_cdata()
            reference_num = root['soap:Envelope']['soap:Body']['DuDirectTopUp1Response']['ReferenceNo'].get_cdata()
            result = {'status_code':status_code,'status_desc':status_desc,'receipt_num':receipt_num,'reference_num':reference_num}
        print "############result",result
        return result

    @api.model
    def get_etisalat_topup(self,args):
        result = {}
        param = self.env['ir.config_parameter']
        base_url = param.search([('key', '=', 'web.base.url')]).value
        url = base_url+'/vasapi/etisalat-direct-topup'
        headers = {'Content-Type': 'application/json'}
        partner_rec = self.env['res.partner'].sudo().search([('id','=',args[0])])
        mobile_no = partner_rec.phone or partner_rec.mobile
        data = {
            "fields": {
                "mobileNo": mobile_no,
                "amount": args[1]
            }
        }
        payload = {'params': data}
        data_json = json.dumps(payload)
        print "########payload",payload
        print "#########data_json",data_json
        res = requests.get(url=url, data=data_json, headers=headers)
        response = json.loads(res.text)
        print "##############res",response
        resp_result = response['result']
        print "###########resp_result"
        if resp_result:
            xml_doc = str(resp_result)
            root = jxmlease.parse(xml_doc)
            print "########root",root
            status_code = root['soap:Envelope']['soap:Body']['EtisalatDirectTopUp1Response']['StatusCode'].get_cdata()
            status_desc = root['soap:Envelope']['soap:Body']['EtisalatDirectTopUp1Response']['StatusDescription'].get_cdata()
            receipt_num = root['soap:Envelope']['soap:Body']['EtisalatDirectTopUp1Response']['ReceiptNo'].get_cdata()
            reference_num = root['soap:Envelope']['soap:Body']['EtisalatDirectTopUp1Response']['ReferenceNo'].get_cdata()
            result = {'status_code':status_code,'status_desc':status_desc,'receipt_num':receipt_num,'reference_num':reference_num}
        print "############result",result
        return result

    @api.model
    def get_fly_dubai(self,args):
        result = {}
        param = self.env['ir.config_parameter']
        base_url = param.search([('key', '=', 'web.base.url')]).value
        url = base_url+'/vasapi/fly-dubai'
        headers = {'Content-Type': 'application/json'}
        partner_rec = self.env['res.partner'].sudo().search([('id','=',args[0])])
        reference_pnr = partner_rec.reference_pnr or False
        data = {
            "fields": {
                "referencePnr": reference_pnr,
                "amount": args[1]
            }
        }
        payload = {'params': data}
        data_json = json.dumps(payload)
        print "########payload",payload
        print "#########data_json",data_json
        res = requests.get(url=url, data=data_json, headers=headers)
        response = json.loads(res.text)
        print "##############res",response
        resp_result = response['result']
        print "###########resp_result"
        if resp_result:
            xml_doc = str(resp_result)
            root = jxmlease.parse(xml_doc)
            print "########root",root
            status_code = root['soap:Envelope']['soap:Body']['FlyDubai1Response']['StatusCode'].get_cdata()
            status_desc = root['soap:Envelope']['soap:Body']['FlyDubai1Response']['StatusDescription'].get_cdata()
            receipt_num = root['soap:Envelope']['soap:Body']['FlyDubai1Response']['ReceiptNo'].get_cdata()
            reference_num = root['soap:Envelope']['soap:Body']['FlyDubai1Response']['ReferenceNo'].get_cdata()
            outstanding_amount = root['soap:Envelope']['soap:Body']['FlyDubai1Response']['OutstandingAmount'].get_cdata()
            result = {'status_code':status_code,'status_desc':status_desc,'receipt_num':receipt_num,'reference_num':reference_num,'outstanding_amount':outstanding_amount}
        print "############result",result
        return result

    @api.model
    def get_addc_topup(self,args):
        result = {}
        param = self.env['ir.config_parameter']
        base_url = param.search([('key', '=', 'web.base.url')]).value
        url = base_url+'/vasapi/addc-topup'
        headers = {'Content-Type': 'application/json'}
        partner_rec = self.env['res.partner'].sudo().search([('id','=',args[0])])
        addc_account_no = partner_rec.addc_acc_no or False
        data = {
            "fields": {
                "addcAccNo": addc_account_no,
                "amount": args[1]
            }
        }
        payload = {'params': data}
        data_json = json.dumps(payload)
        print "########payload",payload
        print "#########data_json",data_json
        res = requests.get(url=url, data=data_json, headers=headers)
        response = json.loads(res.text)
        print "##############res",response
        resp_result = response['result']
        print "###########resp_result"
        if resp_result:
            xml_doc = str(resp_result)
            root = jxmlease.parse(xml_doc)
            print "########root",root
            status_code = root['soap:Envelope']['soap:Body']['ADDC1Response']['StatusCode'].get_cdata()
            status_desc = root['soap:Envelope']['soap:Body']['ADDC1Response']['StatusDescription'].get_cdata()
            receipt_num = root['soap:Envelope']['soap:Body']['ADDC1Response']['ReceiptNo'].get_cdata()
            reference_num = root['soap:Envelope']['soap:Body']['ADDC1Response']['ReferenceNo'].get_cdata()
            outstanding_amount = root['soap:Envelope']['soap:Body']['ADDC1Response']['OutstandingAmount'].get_cdata()
            result = {'status_code':status_code,'status_desc':status_desc,'receipt_num':receipt_num,'reference_num':reference_num,'outstanding_amount':outstanding_amount}
        print "############result",result
        return result
