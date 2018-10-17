# -*- coding: utf-8 -*-
import odoo
import json


from odoo import http
from odoo.http import request


class Bista_Mint_Homepage(http.Controller):

    # Home Page reload functionality
    @http.route(['/', '/page/homepage'], type = 'http', auth = "public",
                website= True)
    def mint_homepage(self, **post):
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        uid = request.uid
        values = {}
        # self.create_menus()

        return http.request.render('website.homepage', values)

    # # To Serach and create new menu if any servers are created
    # def create_menus(self):
    #     menu_recs = request.env['website.menu'].sudo().search([])
    #     website = request.env['website'].sudo().search([], limit = 1)
    #     servers = request.env['saas_portal.server'].sudo().search([])
    #     menu_name_list = self.get_menu_rec(menu_recs)
    #     root_menu_name = 'Services'
    #
    #     if servers :
    #         if root_menu_name not in menu_name_list :
    #             res = request.env['website.menu'].sudo().create(
    #                 {
    #                     'name' : root_menu_name,
    #                     'url' : '/',
    #                     'website_id' : website.id,
    #                     'parent_id' : self.get_parent_menu_id(menu_recs),
    #                 })
    #             menu_name_list.append(res.name)
    #
    #         if root_menu_name in menu_name_list :
    #             menu_recs = request.env['website.menu'].sudo().search([])
    #             parent_menu = self.get_service_menu_rec(menu_recs,
    #                                                     root_menu_name)
    #             for server in servers :
    #                 if server.server_name not in menu_name_list :
    #                     self._create_service_menus(server, parent_menu.id,
    #                                                website,
    #                                                menu_name_list)
    #
    #
    # # To Get the Parent menu Id to set the Service Menu Parent Id
    # def get_parent_menu_id(self, menu_recs=None):
    #     for parent_id in menu_recs:
    #         if parent_id.name == 'Top Menu':
    #             parent_menu_id = parent_id.id
    #             return parent_menu_id
    #
    #
    # # To Create Sub-Menu in the Service Root Menu
    # def _create_service_menus(self, server=None, parent_menu_id=None,
    #                           website=None, menu_name_list=None):
    #     if server.server_name not in menu_name_list:
    #         request.env['website.menu'].sudo().create({
    #             'name' : server.server_name,
    #             'url' : '/page/service/%s' % server.id,
    #             'parent_id' : parent_menu_id,
    #             'website_id': website.id,
    #         })
    #
    # # To Get All Menu Recordset
    # def get_menu_rec(self, menu_rec=None):
    #     menu_list = []
    #
    #     for menu in menu_rec:
    #         menu_list.append(menu.name)
    #
    #     return menu_list
    #
    # # To Get the Service Menu Record from website.menu model
    # def get_service_menu_rec(self, menu_recs=None, root_menu_name=None):
    #
    #     for rec in menu_recs:
    #         if rec.name == root_menu_name:
    #             return rec
