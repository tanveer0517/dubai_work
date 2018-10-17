# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo import SUPERUSER_ID
from odoo.api import Environment
from odoo.sql_db import db_connect
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model
    def create_from_ui(self, partner):
        #Overwrote create_from_ui for checking custome exsiting in local or
        #Portal database. if not exsiting than method create new or raise
        # warining

        domain = ['|','|',('phone', '=', partner.get('phone')),
                  ('email', '=',partner.get('email')),
                  ('ref', '=', partner.get('ref', True))]
        partner_in_local = self.search(domain)
        if partner_in_local:
            portal_db_record = self.env[
                'ir.config_parameter'].sudo().get_param('portal.database')
            new_cr = db_connect(str(portal_db_record)).cursor()
            new_env = Environment(new_cr, SUPERUSER_ID, {})
            partner_in_portal = new_env['res.partner'].search(domain, limit=1)
            if not partner_in_portal:
                new_env['res.partner'].create(partner)
                new_cr.commit()
                new_cr.close()
            else:
                raise ValidationError(_("Customer already exist!"))
        else:
            portal_db_record = self.env[
                'ir.config_parameter'].sudo().get_param('portal.database')
            new_cr = db_connect(str(portal_db_record)).cursor()
            new_env = Environment(new_cr, SUPERUSER_ID, {})
            partner_in_portal = new_env['res.partner'].search(domain, limit=1)
            if not partner_in_portal:
                new_env['res.partner'].create(partner)
                new_cr.commit()
                new_cr.close()
                if partner.get('message_follower_ids'):
                    partner.pop('message_follower_ids')
                if partner.get('image'):
                    partner.pop('image')
                return super(ResPartner, self).create_from_ui(partner)
            else:
                return super(ResPartner, self).create_from_ui(partner)


    # @api.model
    # def create(self, vals):
    #     if not self._context.get('from_pos'):
    #         domain = ['|','|', ('phone', '=', vals.get('phone','')),
    #                   ('email', '=', vals.get('email','')),
    #                   ('ref', '=', vals.get('ref',''))]
    #         partner_in_local = self.search(domain, limit=1)
    #         print 'partner_in_local'
    #         if partner_in_local and partner_in_local.id:
    #             raise ValidationError(
    #                 _("Customer already exist!2"))
    #         portal_db_record = self.env['ir.config_parameter'].sudo().get_param('portal.database')
    #         new_cr = db_connect(str(portal_db_record)).cursor()
    #         new_env = Environment(new_cr, SUPERUSER_ID, {})
    #         parther_data_in_portal = new_env['res.partner'].search(domain, limit=1)
    #         if parther_data_in_portal:
    #             partner_data = self.partner_data(parther_data_in_portal,
    #                                              new_env)
    #             return super(ResPartner, self).with_context({
    #                 'from_pos': True}).create(
    #                 partner_data)
    #         else:
    #             new_env['res.partner'].create(vals)
    #         new_cr.commit()
    #     return super(ResPartner, self).create(
    #         vals)
    #
    # @api.multi
    # def write(self, vals):
    #     domain = ['|', '|', ('phone', '=', vals.get('phone', '')),
    #               ('email', '=', vals.get('email', '')),
    #               ('ref', '=', vals.get('ref', ''))]
    #     partner_in_local = self.search(domain, limit=1)
    #     if partner_in_local and partner_in_local.id:
    #         raise ValidationError(
    #             _("Customer already exist!4"))
    #     portal_db_record = self.env['ir.config_parameter'].sudo().get_param(
    #         'portal.database')
    #     new_cr = db_connect(str(portal_db_record)).cursor()
    #     new_env = Environment(new_cr, SUPERUSER_ID, {})
    #     parther_data_in_portal = new_env['res.partner'].search(domain, limit=1)
    #     if parther_data_in_portal:
    #         raise ValidationError(
    #             _("Customer already exist!5"))
    #     return super(ResPartner, self).create(vals)

    @api.model
    def fetch_client(self, query):
        domain = ['|','|', ('phone','=',query), ('email','=',query), ('ref','=',query)]
        if domain:
            parther_data_in_local = self.search(domain, limit=1)

        portal_db_record = self.env['ir.config_parameter'].sudo().get_param(
            'portal.database')
        new_cr = db_connect(str(portal_db_record)).cursor()
        new_env = Environment(new_cr, SUPERUSER_ID, {})
 
        if portal_db_record:
            if parther_data_in_local:
                partner_in_portal = new_env['res.partner'].search(domain, limit=1)
                if not partner_in_portal:
                    parther_vals = self.partner_data(parther_data_in_local, new_env)
                    new_partner = new_env['res.partner'].create(parther_vals)
                    child_list = []
                    for child in parther_data_in_local.child_ids:
                        childs_vals = self.partner_data(child, new_env)
                        childs_vals.update({'parent_id':new_partner.id})
                        child_list.append((0,0, childs_vals))
                    if child_list:
                        new_partner.write({'child_ids' : child_list})
                    new_cr.commit()
                return parther_data_in_local.id
            else:
                partner_in_portal = new_env['res.partner'].search(domain, limit=1)
                if partner_in_portal:
                    parther_vals = self.partner_data(partner_in_portal,
                                                     self.env)
                    new_partner = self.create(
                        parther_vals)
                    child_list = []
                    if partner_in_portal.child_ids:
                        for child in partner_in_portal.child_ids:
                            childs_vals = self.partner_data(child, self.env)
                            childs_vals.update({'parent_id':new_partner.id})
                            child_list.append((0,0, childs_vals))
                        if child_list:
                            new_partner.write({'child_ids' : child_list})
                    return new_partner.id
        return False
        

    @api.model
    def partner_data(self, partner, Environment):
        rec = {}
        if partner and partner.id:
            rec.update({
                'name':partner.name,
                'type': partner.type,
                'city' : partner.city or '',
                'email': partner.email or '',
                'is_company': partner.is_company or False,
                'customer' : partner.customer or False,
                'supplier' : partner.supplier or False,
                'mobile;' : partner.mobile or '',
                'comment' : partner.comment or '',
                'phone' : partner.phone or '',
                'state_id' : Environment['res.country.state'].search([(
                    'name','=',partner.state_id.name)],limit=1).id or False,
                'country_id': Environment['res.country'].search([('name','=',partner.country_id.name)], limit=1).id or False,
                'street' : partner.street or '',
                'street2' : partner.street2 or '',
                'title' : Environment['res.partner.title'].search([('name',
                                                                    '=',
                                                                    partner.title.name)],limit=1).id or False,
                'website': partner.website or '',
                'zip': partner.zip or '',
            })
        return rec
