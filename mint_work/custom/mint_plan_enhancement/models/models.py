# -*- coding: utf-8 -*-
import re


from odoo import models, fields, api, _
from odoo.exceptions import Warning
from python_hosts import Hosts, HostsEntry


class mint_plan_enhancement(models.Model):

    _inherit = 'saas_portal.plan'

    db_name = fields.Char('Database Name', size=16, help="""This field is 
    used to generate Current Plan Template and the databse will be created 
    according to that Plan Template Name. (Only 16 characters are allowed)""")

    @api.model
    def create(self, vals):
        # Inherit create_portal.plan create method for generating template
        # name from server name and plan name.
        # Give warning if template is already exist.
        saas_server_obj = self.env['saas_portal.server']
        portal_db_obj = self.env['saas_portal.database']
        config = self.env['ir.config_parameter']
        saas_config = self.env['saas_portal.config.settings'].search(
            [], limit=1, order="id desc")
        alies_name = saas_config.base_saas_domain
        if alies_name == False:
            base_saas_rec = config.search([('key', '=',
                                            'saas_portal.base_saas_domain')],
                                          limit=1)
            alies_name = base_saas_rec.value
        server_id = vals.get('server_id' or False)
        server_rec = saas_server_obj.browse(server_id)
        server_name = server_rec.name
        default_plan_name = vals.get('db_name')
        new_server_name = self.concate_string(server_name, alies_name)
        new_plan_name = self.concate_string(default_plan_name, alies_name)
        template_name = "template." + new_server_name + '.' + new_plan_name + \
                        '.' + alies_name

        exsiting_templates = portal_db_obj.search([
            ('name', '=', template_name),
            ('state', '=', 'template'),
            ('server_id', '=', server_id)], limit = 1)

        if exsiting_templates:
            raise Warning(_('Template already exists. Please give Different '
                            'Name of your Plan.'))
        else:
            # Host entry is done for the ip address and database name
            hosts = Hosts(path = '/etc/hosts')
            new_entry = HostsEntry(entry_type = 'ipv4', address = '127.0.0.1',
                                   names = [template_name])
            hosts.add([new_entry])
            hosts.write()
            portal_db_rec = portal_db_obj.create({
                'name': template_name,
                'server_id': server_id
            })
        vals.update({
            'template_id':portal_db_rec.id,
        })
        return super(mint_plan_enhancement, self).create(vals)


    def concate_string(self, name=False, alies_name=False):
        # Making plan name using alies name.
        # Remove space from name if space.
        if name == False or alies_name == False:
            raise Warning(_('No Alies Name or Server Name Found Please '
                            'select a Server Template.'))
        else:
            default_name = name.strip()
            alies_name = "." + alies_name
            find_alies_name = default_name.find(alies_name)
            last_4_digits = default_name[find_alies_name:]
            if last_4_digits == alies_name:
                default_name = default_name.replace(alies_name, '')
                default_name = default_name.replace("-", ".")
            remove_spe_cha = re.sub('[^ a-zA-Z\d.]', '', default_name)
            remove_space = ' '.join(remove_spe_cha.split())
            refine_name = remove_space.replace(" ", ".")
            return refine_name.lower()
