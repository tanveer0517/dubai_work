# -*- coding: utf-8 -*-
import werkzeug
from odoo import http
from odoo.http import request
import urllib

class SaasClient(http.Controller):

    @http.route(['/login_parameter'], type='json', auth='user')
    def login_parameter(self, **post):
        dbuuid = request.env['ir.config_parameter'].get_param('database.uuid')
        portal_provider = request.env['ir.config_parameter'].get_param(
            'portal.provider')
        portal_db = request.env['ir.config_parameter'].get_param(
            'portal.database')
        redirect_uri = request.env['ir.config_parameter'].get_param(
            'portal.url') + '/auth_oauth/signin'
        r = "%2Fmy%2Fhome%3F"
        state = '{"p": %s, "r": "%s" ,"d" : "%s"}' % (
        portal_provider, r, portal_db)
        url1 = '/oauth2/auth?%s' % urllib.urlencode({
            'state': state,
            "redirect_uri": redirect_uri,
            "response_type": "token",
            "client_id": dbuuid,
            "debug": False,
            "scope": "userinfo"
        })
        return {'portal_url': url1}