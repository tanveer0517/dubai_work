# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from odoo import http, SUPERUSER_ID
from openerp.addons.web.controllers.main import Home, ensure_db
from openerp.addons.saas_base.tools import get_size
from openerp.addons.website_sale.controllers.main import WebsiteSale
import random
import string
import openerp
import xmlrpclib


import logging
_logger = logging.getLogger(__name__)

class ClientSuspended(http.Controller):

    @http.route(['/suspended'], type='http', auth='public', website=True)
    def page_suspeneded(self, **post):
        users = request.env['res.users'].sudo().browse(SUPERUSER_ID)
        if users and users.oauth_provider_id and \
                users.oauth_provider_id.auth_endpoint:
            base_url = users.oauth_provider_id.auth_endpoint.split('/oauth2/auth')
            values = {'base_url' : base_url[0] + '/web/login'}
        return request.render("saas_user_restrict.suspended", values)
