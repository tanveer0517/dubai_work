# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import requests
import json
import logging
_logger = logging.getLogger(__name__)
from odoo import http, SUPERUSER_ID

class mint_api(http.Controller):
    @http.route('/vasapi/intl-operator-info/<mobileNo>', auth='none')
    def getPlan(self,mobileNo):
        url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
        payload = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n  <soap:Body>\r\n    <InTopUpOperatorInfo xmlns=\"http://tempuri.org/\">\r\n      <username>17bac72646e19378</username>\r\n      <pass>95e696a6d6a1ba1c</pass>\r\n      <ChannelType>G</ChannelType>\r\n      <MobileNo>"+mobileNo+"</MobileNo>\r\n    </InTopUpOperatorInfo>\r\n  </soap:Body>\r\n</soap:Envelope>"
        headers = {
        'content-type': "text/xml",
        'data': "application/xml"
        }
        print "###########",payload
        response = requests.request("POST", url, data=payload, headers=headers)
        print "##########response",response.text
        return response.text

    @http.route('/vasapi/du-direct-topup', type='json', auth='none')
    def du_topup(self, fields):
        print "##################",fields
        mobileNo = fields.get("mobileNo")
        amount = fields.get("amount")
        url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
        payload = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <DuDirectTopUp1 xmlns="http://tempuri.org/">
                                    <username>17bac72646e19378</username>
                                    <pass>95e696a6d6a1ba1c</pass>
                                    <ChannelType>G</ChannelType>
                                    <Amount>"""+str(amount)+"""</Amount>
                                    <MobileNo>"""+mobileNo+"""</MobileNo>
                                </DuDirectTopUp1>
                            </soap:Body>
                        </soap:Envelope>
                  """
        headers = {
        'content-type': "text/xml",
        'data': "application/xml"
        }
        print "###########",payload
        response = requests.request("POST", url, data=payload, headers=headers)
        print "##########response",response.text
        return response.text

    @http.route('/vasapi/etisalat-direct-topup', type='json', auth='none')
    def etislat_topup(self, fields):
        print "##################",fields
        mobileNo = fields.get("mobileNo")
        amount = fields.get("amount")
        url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
        payload = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <EtisalatDirectTopUp1 xmlns="http://tempuri.org/">
                                    <username>17bac72646e19378</username>
                                    <pass>95e696a6d6a1ba1c</pass>
                                    <ChannelType>G</ChannelType>
                                    <Amount>"""+str(amount)+"""</Amount>
                                    <MobileNo>"""+mobileNo+"""</MobileNo>
                                </EtisalatDirectTopUp1>
                            </soap:Body>
                        </soap:Envelope>
                  """
        headers = {
        'content-type': "text/xml",
        'data': "application/xml"
        }
        print "###########",payload
        response = requests.request("POST", url, data=payload, headers=headers)
        print "##########response",response.text
        return response.text

    @http.route('/vasapi/fly-dubai', type='json', auth='none')
    def fly_dubai(self, fields):
        print "##################",fields
        reference_pnr = fields.get("referencePnr")
        amount = fields.get("amount")
        url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
        payload = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <FlyDubai1 xmlns="http://tempuri.org/">
                                  <username>17bac72646e19378</username>
                                  <pass>95e696a6d6a1ba1c</pass>
                                  <ChannelType>G</ChannelType>
                                  <Amount>"""+str(amount)+"""</Amount>
                                  <ReferenceOrPNR>"""+str(reference_pnr)+"""</ReferenceOrPNR>
                                </FlyDubai1>
                            </soap:Body>
                        </soap:Envelope>
                  """
        headers = {
        'content-type': "text/xml",
        'data': "application/xml"
        }
        print "###########",payload
        response = requests.request("POST", url, data=payload, headers=headers)
        print "##########response",response.text
        return response.text

    @http.route('/vasapi/addc-topup', type='json', auth='none')
    def fly_dubai(self, fields):
        print "##################",fields
        addc_account_no = fields.get("addcAccNo")
        amount = fields.get("amount")
        url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
        payload = """<?xml version="1.0" encoding="utf-8"?>
                        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <ADDC1 xmlns="http://tempuri.org/">
                                  <username>17bac72646e19378</username>
                                  <pass>95e696a6d6a1ba1c</pass>
                                  <ChannelType>G</ChannelType>
                                  <Amount>"""+str(amount)+"""</Amount>
                                  <AccountNo>"""+str(addc_account_no)+"""</AccountNo>
                                </ADDC1>
                            </soap:Body>
                        </soap:Envelope>
                  """
        headers = {
        'content-type': "text/xml",
        'data': "application/xml"
        }
        print "###########",payload
        response = requests.request("POST", url, data=payload, headers=headers)
        print "##########response",response.text
        return response.text

    # @http.route('/vasapi/intl-topup-loadamount/',type='json', auth='public', methods=['POST'], website=True, csrf=False)
    # def getReferenceNo(self,**kw):
    #     print "##########",kw
    #     user_name = "17bac72646e19378"
    #     password = "95e696a6d6a1ba1c"
    #     card_number = "9f7e582420907bcd1248ca3911fc1873"
    #     channel_type = "G"
    #     url = "https://mymintapp.com:4444/VS/WsVAS.asmx"
    #     payload == ""
    #     headers = {
    #     'content-type': "text/xml",
    #     'data': "application/xml"
    #     }
    #     response = requests.request("POST", url, data=payload, headers=headers)
    #     return response.text