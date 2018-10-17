# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import urlparse

from odoo import http
from odoo.http import request
import base64
from datetime import datetime
import werkzeug
from odoo.addons.website_mail.controllers.main import WebsiteMail
from odoo.addons.website_support.controllers.main import MyController


class WebsiteMailController(WebsiteMail):

    @http.route(['/website_mail/post/json'], type='json', auth='public', website=True)
    def chatter_json(self, res_model='', res_id=None, message='', **kw):
        # Creating and updating message chatter from website part.
        params = kw.copy()
        message_data = super(WebsiteMailController, self).chatter_json(res_model=res_model, res_id=res_id, message=message, **params)
        if message_data and kw.get('attachments'):  # restrict rating only for
            attachment_obj = request.env['ir.attachment']
            attachment = attachment_obj.sudo().create({
                'name': kw.get('attachment_name'),
                'datas': str(kw.get('attachments').split(',')[1]),
                'datas_fname':kw.get('attachment_name'),
                'res_model': 'project.case',
                'res_id': res_id,
                'type': 'binary'
            })
            message_data.update({
                'attachment_ids' : [attachment.id],
                'attachments' :   str(kw.get('attachments').split(',')[1]),
            })
            maile_id = request.env['mail.message'].sudo().search([('id',
                                                               '=',
                                                               message_data.get('id')),
                                                            ])
            if attachment:
                maile_id.write({'attachment_ids' : [(6, 0, [attachment.id])]})
        return message_data

class MyControllerExt(MyController):

    @http.route('/support/ticket/submit', type="http", auth="public",
                website=True)
    def support_submit_ticket_category(self, **post):
        values = {}
        category_data = request.env['ticket.category'].search([])
        values.update({'category_data':category_data})
        return http.request.render("website_support.category", values)


    @http.route('/support/ticket/category/submit', type="http", auth="public",
                website=True)
    def support_submit_ticket(self, **kw):
        """Let's public and registered user submit a support ticket"""
        category = int(kw.get('support category'))
        values = {}

        category_data = request.env['ticket.category'].browse(category)
        call_type_data = request.env['ticket.call.type'].search([])

        values.update({'category_data':category_data,
                       'call_type_data':call_type_data,
                       'email': http.request.env.user.email})

        person_name = ""
        if http.request.env.user.name != "Public user":
            person_name = http.request.env.user.name
            values.update({'person_name': person_name,})
        return http.request.render('website_support.support_submit_ticket',values)


    @http.route('/support/ticket/process', type="http", auth="public", website=True, csrf=False)
    def support_process_ticket(self, **kwargs):
        """Adds the support ticket to the database and sends out emails to everyone following the support ticket category"""
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        my_attachment = ""
        file_name = ""
        if 'file' in values:
            my_attachment = base64.encodestring(values['file'].read())
            file_name = values['file'].filename

        if http.request.env.user.partner_id.parent_id.id:
            partner_id = http.request.env.user.partner_id.parent_id.id
        else:
            partner_id = http.request.env.user.partner_id.id

        project_case_vals = {
            'case_name': values['subject'],
            'call_type_id': int(values['call type']),
            'category' : int(
                values['category_data']),
            'description': values['description'],
            'case_origin': 'web_form',
            'partner_id': partner_id,
            'contact_id': http.request.env.user.partner_id.id,
            'reported_by_id': http.request.env.user.partner_id.id,
            'email_from': http.request.env.user.partner_id.email or '',
            'call_received': datetime.now(),
            'stage_id': 'draft',
            'attachment': my_attachment,
            'attachment_filename': file_name,
        }
        project_case_rec = request.env['project.case'].sudo().create(project_case_vals)
        if 'file' in values and my_attachment:
            attachment_obj = request.env['ir.attachment']
            attachment_obj.sudo().create({
                'name': file_name,
                'datas': my_attachment,
                'datas_fname': file_name,
                'res_model': 'project.case',
                'res_id': project_case_rec.id,
                'type': 'binary'
            })
        return werkzeug.utils.redirect("/support/ticket/thanks")

