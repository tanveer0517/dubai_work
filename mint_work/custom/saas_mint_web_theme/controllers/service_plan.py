# -*- coding: utf-8 -*-
import odoo
import json


from odoo import http
from odoo.http import request


class Bista_Mint_Server(http.Controller):

    # Get the server id and and display plans according to that
    @http.route(['/page/service/<int:server_id>'], type='http', auth="public",
                website=True)
    def mint_server(self, server_id, **post):
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        uid = request.uid
        company = request.env['res.company'].search([], limit=1)
        server = request.env['saas_portal.server'].sudo().search([
            ('id', '=', server_id)])
        domain = [('state', 'in', ['confirmed']),
                  ('server_id', '=', server_id)]
        templates = request.env['saas_portal.plan'].sudo().search(
            domain,
            order='id asc'
        )

        if server and templates :
            values = {'templates': templates,
                      'uid': uid,
                      'company': company,
                      'server': server}
        else:
            no_template_found = "THERE ARE NO SERVICES AVAILABLE FOR THIS " \
                                "SERVER RIGHT NOW"
            values = {'uid' : uid,
                      'company' : company,
                      'server' : server,
                      'no_template_found': no_template_found}

        return http.request.render('saas_mint_web_theme.server_plan', values)


    # To get the Plan Feature List and display it on website
    @http.route(['/web/plan/description'], type='http', auth="public",
                website=True)
    def plan_description(self, **post):

        plan_description = []
        tmpl_id = request.params['id']
        plan = request.env['saas_portal.plan'].sudo().search(
            [('id', '=', tmpl_id)])
        for plan_desc in plan.plan_description_ids:
            plan_description.append(plan_desc.plan_description_details)

        if len(plan_description) == 0:
            plan_description.append('No Plan Description Available')

        return json.dumps(plan_description)
