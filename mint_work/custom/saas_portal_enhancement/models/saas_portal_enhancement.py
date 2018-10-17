# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, except_orm

import logging
_logger = logging.getLogger(__name__)


class saas_portal_enhancement(models.Model):
    _inherit = 'saas_portal.server'
    _rec_name = 'server_name'

    _sql_constraints = [
        ('name_uniq', 'unique(server_name)',
         'Server name Already Exist!'),
    ]

    server_image = fields.Binary('Server Image',
                                 help="""Upload server Image that wil 
                                 display on website and size should be 
                                 below or equal to 1 mb only""")
    server_image_icon = fields.Binary('Server Image Icon',
                                      help="""Upload Image which is used to 
                                      display on the main server listing on 
                                      webpage and size should be below or 
                                      equal to 1 mb only
                                      """)
    server_name = fields.Char(string="Server Name", required=True)
    short_desc = fields.Char(string="Short Description", max=16, required=True)
    description = fields.Html(string="Description", required=True)
    terms_conditons = fields.Html(string = "Terms & Conditions", required=True)
    feature_ids = fields.Many2many('saas_portal.server.features',
                                   'server_feature_rel',
                                   'server_id','feature_id',
                                   help="""Define the Features that are to 
                                  be held in this Server and will be 
                                  available to all plans. You can optimized 
                                  it in Plan later.
                                  """)
    features_description_ids = fields.One2many(
        'saas_portal.feature_description', 'feature_description_id',
        help="""Enter Features Description list which will be displayed in the 
    information tab of the serverso that the users who are opting the 
    server will know what features this server provides.""")

    # Create Method Override and menu record is created
    @api.model
    def create(self, vals):
        res = super(saas_portal_enhancement, self).create(vals)
        # res.create_menus()
        return res

    # ======= Keep this code for future use ====================
    # # To Serach and create new menu if any servers are created
    # @api.one
    # def create_menus(self, active = None):
    #     root_menu_name = 'Services'
    #     menu_recs = self.env['website.menu'].search([])
    #     parent_menu = menu_recs.filtered(lambda r: r.name == root_menu_name)
    #     website = self.env['website'].search([], limit = 1)
    #     menu_name_list = menu_recs.mapped('name')
    #
    #     if self.active or active:
    #         if self.server_name not in menu_name_list :
    #             self._create_service_menus(parent_menu.id,
    #                                        website,
    #                                        menu_name_list,
    #                                        active = True)
    #         else:
    #             raise Warning(_('Server Menu Already Exists. Please Give '
    #                             'Another Server Menu Name'))
    #     else:
    #         if self.server_name not in menu_name_list :
    #             self._create_service_menus(parent_menu.id,
    #                                        website,
    #                                        menu_name_list,
    #                                        active = False)
    #         else:
    #             raise Warning(_('Server Menu Already Exists. Please Give '
    #                             'Another Server Menu Name'))

    # # To Create Sub-Menu in the Service Root Menu
    # @api.one
    # def _create_service_menus(self, parent_menu_id = None,
    #                           website = None, menu_name_list = None,
    #                           active = None) :
    #     self.env['website.menu'].create({
    #         'name' : self.server_name,
    #         'url' : '/page/service/%s' % self.id,
    #         'parent_id' : parent_menu_id,
    #         'website_id' : website.id,
    #         'show_menu': active,
    #     })

    # # This function will check in the website menu (which wil be visible in
    # # debug mode in website admin -> settings -> configur menu) the menu
    # # name if exist then it will replace the old one with the new one,
    # # if server deleted or inactive, it will deactivate the menu
    # @api.multi
    # def write(self, vals):
    #     existing_server_name = self.server_name
    #     new_server_name = vals.get('server_name')
    #     new_active = vals.get('active')
    #     menu_recs = self.env['website.menu'].search([('name', '=',
    #                                                   str(existing_server_name)
    #                                                   )], limit=1)
    #
    #     if not menu_recs:
    #         if new_active:
    #             self.create_menus(new_active)
    #         else:
    #             self.create_menus()
    #         # return super(saas_portal_enhancement, self).write(vals)
    #     elif new_server_name and menu_recs and new_active == True:
    #         menu_recs.write({'name' : new_server_name, 'show_menu' : True,
    #                          'url': '/page/service/%s' % self.id})
    #     elif new_server_name and menu_recs and new_active == False :
    #         menu_recs.write({'name' : new_server_name, 'show_menu' : False,
    #                          'url' : '/page/service/%s' % self.id})
    #     elif new_server_name and menu_recs and self.active == True :
    #         menu_recs.write({'name' : new_server_name, 'show_menu' : True,
    #                          'url' : '/page/service/%s' % self.id})
    #     elif new_server_name and menu_recs and self.active == False :
    #         menu_recs.write({'name' : new_server_name, 'show_menu' : False,
    #                          'url' : '/page/service/%s' % self.id})
    #     elif new_active and menu_recs:
    #         menu_recs.write({'show_menu': True,
    #                          'url' : '/page/service/%s' % self.id})
    #     elif new_active == False and menu_recs:
    #         menu_recs.write({'show_menu' : False,
    #                          'url' : '/page/service/%s' % self.id})
    #     else:
    #         pass
    #     return super(saas_portal_enhancement, self).write(vals)

    # # This method will unlink the website service menu if the server is
    # # deleted
    # @api.multi
    # def unlink(self) :
    #     server_id = self.id
    #     server_name = self.server_name
    #     menu_recs = self.env['website.menu'].search([
    #         ('url', '=', '/page/service/%s' % server_id),
    #         ('name', '=', str(server_name))], limit = 1)
    #     menu_recs.unlink()
    #     result = super(saas_portal_enhancement, self).unlink()
    #     return result


class Saas_Portal_Server_Feature_Desc(models.Model):
    _name = 'saas_portal.feature_description'

    feature_description_id = fields.Many2one('saas_portal.server')
    image_icon = fields.Binary('Feature Icon')
    icon_name = fields.Char('Icon Name', help="""Only Font-Awesome Icons 
    are allowed. Only place the Icon Name here eg : fa-arrow-right.""")
    name = fields.Char('Feature Name', required=True)
    description = fields.Text('Feature Description', required=True)
