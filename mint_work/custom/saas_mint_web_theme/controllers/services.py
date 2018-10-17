# -*- coding: utf-8 -*-
import odoo
import json


from odoo import http
from odoo.http import request


class Bista_Mint_Servers(http.Controller):

    # To Get the Servers and Display on the Services Page
    @http.route(['/page/services'], type='http', auth="public",
                website=True)
    def mint_services(self, **post):
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        uid = request.uid
        company = request.env['res.company'].sudo().search([], limit=1)
        servers = request.env['saas_portal.server'].sudo().search([])
        if servers:
            values = {'uid': uid,
                      'company': company,
                      'servers': servers}
        else:
            no_servers_found = "THERE ARE NO SERVICES AVAILABLE FOR THIS "
            values = {'uid' : uid,
                      'company' : company,
                      'no_servers_found': no_servers_found}

        return http.request.render('saas_mint_web_theme.serves_page', values)
