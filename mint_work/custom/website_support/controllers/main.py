# -*- coding: utf-8 -*-
import werkzeug
import json
import base64
from datetime import datetime
import openerp.http as http
from openerp.http import request
from openerp.addons.website.models.website import slug


class MyController(http.Controller):

    @http.route('/website_support/stage/change', type='json', auth='public',
                website=True)
    def get_translated_length(self, stage):
        # partner_rec= http.request.env['res.users'].sudo().browse(
        #     request.session.uid).partner_id
        # print "::::::::::::::",partner_rec
        # # partner_rec = http.request.env.user.partner_id
        # partner_id_list = []
        # partner_id_list.append(http.request.env['res.users'].sudo().browse(
        #     request.session.uid).partner_id.id)
        # print "list-------------",partner_id_list
        # ticket_group = http.request.env.user.partner_id.ticket_grp.id
        # ticket_groups_m2m = http.request.env.user.partner_id.ticket_group_ids
        # ticket_groups_m2m_default =  http.request.env['ticket.group'].sudo().search([])
        # print "\n\n\n DEFAULTTTTTTTTT",ticket_groups_m2m_default
        # print "\n\n\n GROUPS ISSSSSSSSSSS",ticket_groups_m2m
        # support_tickets = http.request.env['project.case'].sudo().search(['|','&','|', ('partner_id', 'in', partner_id_list),
        #                                                                       ('contact_id', 'in', partner_id_list),
        #                                                                       ('ticket_group','in',ticket_groups_m2m.ids),
        #                                                                       ('ticket_group', '=', False)])
        #     support_dict = ({{'support_tickets': support_tickets,
        #                       'stage':stage}})
        #     print "suportt---------",support_tickets
        return stage


    @http.route('/support/help', type="http", auth="public", website=True)
    def support_help(self, **kw):
        if kw and kw.get('stage') and kw.get('stage') != 'all':
            partner_rec = http.request.env.user.partner_id
            partner_id_list = []
            partner_id_list.append(http.request.env.user.partner_id.id)
            ticket_group = http.request.env.user.partner_id.ticket_grp.id
            ticket_groups_m2m = http.request.env.user.partner_id.ticket_group_ids
            ticket_groups_m2m_default = http.request.env[
                'ticket.group'].sudo().search([])
            if partner_rec.all_ticket:
                if partner_rec.parent_id.id:
                    if partner_rec.parent_id.id not in partner_id_list:
                        partner_id_list.append(partner_rec.parent_id.id)
                    for child_rec in partner_rec.parent_id.child_ids:
                        if child_rec.id not in partner_id_list:
                            partner_id_list.append(child_rec.id)
                elif partner_rec.child_ids:
                    for child_rec in partner_rec.child_ids:
                        if child_rec.id not in partner_id_list:
                            partner_id_list.append(child_rec.id)
                support_tickets = http.request.env[
                    'project.case'].sudo().search(
                    ['|', '&', '|', ('partner_id', 'in', partner_id_list),
                     ('contact_id', 'in', partner_id_list),
                     ('ticket_group', 'in', ticket_groups_m2m.ids),
                     ('ticket_group', '=', False),
                     ('stage_id', '=', kw['stage'])])
            else:
                support_tickets = http.request.env[
                    'project.case'].sudo().search(
                    [('partner_id', 'in', partner_id_list),
                     ('stage_id', '=', kw['stage'])])
            """Displays all help groups and thier child help pages"""
            return http.request.render('website_support.support_help_pages',
                                       {'support_tickets': support_tickets,
                                        'ticket_count': len(support_tickets),
                                        'stage': support_tickets.STATE,
                                        'c_stage': kw['stage']})
        partner_rec = http.request.env.user.partner_id
        partner_id_list = []
        partner_id_list.append(http.request.env.user.partner_id.id)
        ticket_group = http.request.env.user.partner_id.ticket_grp.id
        ticket_groups_m2m = http.request.env.user.partner_id.ticket_group_ids
        ticket_groups_m2m_default =  http.request.env['ticket.group'].sudo().search([])
        if partner_rec.all_ticket:
            if partner_rec.parent_id.id:
                if partner_rec.parent_id.id not in partner_id_list:
                    partner_id_list.append(partner_rec.parent_id.id)
                for child_rec in partner_rec.parent_id.child_ids:
                    if child_rec.id not in partner_id_list:
                        partner_id_list.append(child_rec.id)
            elif partner_rec.child_ids:
                for child_rec in partner_rec.child_ids:
                    if child_rec.id not in partner_id_list:
                        partner_id_list.append(child_rec.id)
            support_tickets = http.request.env['project.case'].sudo().search(['|','&','|', ('partner_id', 'in', partner_id_list),
                                                                              ('contact_id', 'in', partner_id_list),
                                                                              ('ticket_group','in',ticket_groups_m2m.ids),
                                                                              ('ticket_group', '=', False)])

        else:
            support_tickets = http.request.env['project.case'].sudo().search([('partner_id', 'in', partner_id_list)])
        """Displays all help groups and thier child help pages"""
        return http.request.render('website_support.support_help_pages',
                                   {'support_tickets': support_tickets,
                                    'ticket_count': len(support_tickets),
                                    'stage':support_tickets.STATE,
                                    'c_stage': ''})

    # @http.route('/support/ticket/submit', type="http", auth="public", website=True)
    # def support_submit_ticket(self, **kw):
    #     """Let's public and registered user submit a support ticket"""
    #     person_name = ""
    #     if http.request.env.user.name != "Public user":
    #         person_name = http.request.env.user.name
    #     return http.request.render('website_support.support_submit_ticket', {'person_name': person_name, 'email': http.request.env.user.email})

    @http.route('/support/ticket/submit', type="http", auth="public",
                website=True)
    def support_submit_ticket_category(self, **post):
        # category = str(post.get('category'))
        # print "\n\n\n\n\n category", category, type(category)
        return http.request.render("website_support.category")

    @http.route('/support/ticket/category/submit', type="http", auth="public",
                website=True)
    def support_submit_ticket(self, **kw):
        """Let's public and registered user submit a support ticket"""
        category = str(kw.get('category'))
        person_name = ""
        if http.request.env.user.name != "Public user":
            person_name = http.request.env.user.name
        return http.request.render('website_support.support_submit_ticket',
                                   {'person_name': person_name,
                                    'email': http.request.env.user.email,
                                    'query': category})

    @http.route('/support/feedback/process/<help_page>', type="http", auth="public", website=True)
    def support_feedback(self, help_page, **kw):
        """Process user feedback"""
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value
        # Don't want them distorting the rating by submitting -50000 ratings
        if int(values['rating']) < 1 or int(values['rating']) > 5:
            return "Invalid rating"
        # Feeback is required
        if values['feedback'] == "":
            return "Feedback required"
        request.env['website.support.help.page.feedback'].sudo().create({'hp_id': int(help_page), 'feedback_rating': values['rating'], 'feedback_text': values['feedback']})
        return werkzeug.utils.redirect("/support/help")

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
            'call_type': values['call_type'],
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

    @http.route('/support/ticket/thanks', type="http", auth="public", website=True)
    def support_ticket_thanks(self, **kw):
        """Displays a thank you page after the user submits a ticket"""
        return http.request.render('website_support.support_thank_you', {})

    @http.route('/support/ticket/view', type="http", auth="user", website=True)
    def support_ticket_view_list(self, **kw):
        """Displays a list of support tickets owned by the logged in user"""
        partner_rec = http.request.env.user.partner_id
        partner_id_list = []
        partner_id_list.append(http.request.env.user.partner_id.id)
        ticket_group = http.request.env.user.partner_id.ticket_grp.id
        if partner_rec.all_ticket:
            if partner_rec.parent_id.id:
                if partner_rec.parent_id.id not in partner_id_list:
                    partner_id_list.append(partner_rec.parent_id.id)
                for child_rec in partner_rec.parent_id.child_ids:
                    if child_rec.id not in partner_id_list:
                        partner_id_list.append(child_rec.id)
            elif partner_rec.child_ids:
                for child_rec in partner_rec.child_ids:
                    if child_rec.id not in partner_id_list:
                        partner_id_list.append(child_rec.id)

            support_tickets = http.request.env['project.case'].sudo().search(['|', ('partner_id', 'in', partner_id_list),
                                                                              ('contact_id', 'in', partner_id_list)])
        else:
            support_tickets = http.request.env['project.case'].sudo().search([('partner_id', 'in', partner_id_list)])
            # support_tickets = http.request.env['project.case'].sudo().search(['|', ('partner_id', 'in', partner_id_list),
            #                                                                   ('ticket_group', '=', ticket_group)])
        return http.request.render('website_support.support_ticket_view_list', {'support_tickets': support_tickets, 'ticket_count': len(support_tickets)})

    @http.route('/support/ticket/view/<ticket>', type="http", auth="user", website=True)
    def support_ticket_view(self, ticket):
        """View an individual support ticket"""
        # only let the user this ticket is assigned to view this ticket
        # support_ticket = http.request.env['project.case'].sudo().search([('partner_id','=',http.request.env.user.partner_id.id), ('id','=',ticket) ])[0]
        support_ticket = http.request.env['project.case'].sudo().search([('id', '=', ticket)])[0]
        return http.request.render('website_support.support_ticket_view', {'support_ticket': support_ticket,'ticket':ticket})

    @http.route('/support/ticket/comment', methods=['GET', 'POST'], type="http", auth="user", csrf=False)
    def support_ticket_comment(self, **post):

        ticket = http.request.env['project.case'].sudo().search([('id', '=', post.get('ticket_id'))])
        content = str(post.get('comment'))
        attach_obj = request.env['ir.attachment']
        # print "\n\n\n ATTACHMENT DATA",base64.encodestring(str(post.get('attachment')))
        file = post.get('attachment')
        attach = file.stream
        f = attach.getvalue()
        from_name = ""
        if http.request.env.user.name != "Public user":
            from_name = http.request.env.user.name
        line_id = http.request.env['page.case.ticket.message'].create({'project_case_id': ticket.id,
                                                                       'content': content,
                                                                       'mesage_from': from_name,
                                                                       'filename':file.filename})
        attachment_value = {
            'type':'binary',
            'name': post.get('attachment').filename,
            'datas': base64.encodestring(f),
            'datas_fname': post.get('attachment').filename,
            'public': True,
            'res_model': 'page.case.ticket.message',
            'res_id': line_id.id,
        }
        a = attach_obj.sudo().create(attachment_value)
        line_id.write({'attachment_id': a.id,'attachment':a.datas})
        return werkzeug.utils.redirect("/support/ticket/view/" + str(ticket.id))
