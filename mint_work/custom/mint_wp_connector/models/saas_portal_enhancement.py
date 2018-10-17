# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from unidecode import unidecode

import logging
_logger = logging.getLogger(__name__)


class saas_portal_enhancementinherits(models.Model):
    _name = 'saas_portal.server'
    _inherit = ['saas_portal.server', 'update.wp_db']
    _rec_name = 'server_name'

    # Create Method Override and menu record is created
    @api.model
    def create(self, vals):
        res = super(saas_portal_enhancementinherits, self).create(vals)
        server_master_data = self.get_server_features_data(res)
        server_feature_rel_data = self.get_server_feature_rel_data(res)
        self.create_update_data(res, server_master_data)
        self.create_update_data(res, server_feature_rel_data)
        return res

    @api.multi
    def write(self, vals):
        result = super(saas_portal_enhancementinherits, self).write(vals)
        res = self
        server_master_data = self.get_server_features_data(res)
        for rec in server_master_data:
            description = unidecode(rec.get('description'))
            terms_and_conditions = unidecode(rec.get('terms_conditons'))
            rec.update({
                'description':description,
                'terms_conditons':terms_and_conditions,
            })
        server_feature_rel_data = self.get_server_feature_rel_data(res)
        self.create_update_data(res, server_master_data)
        self.create_update_data(res, server_feature_rel_data)
        return result

    # This method will unlink the website service menu if the server is
    # deleted
    @api.multi
    def unlink(self) :
        res = self
        server_master_data = self.get_server_features_data(res)
        server_feature_rel_data = self.get_server_feature_rel_data(res)
        self.create_update_data(res, server_master_data, unlink=True)
        self.create_update_data(res, server_feature_rel_data, unlink=True)
        result = super(saas_portal_enhancementinherits, self).unlink()
        return result

    @api.multi
    def get_server_features_data(self, res = False) :
        if res :
            rec_ids = res.ids
            server_master_query = """select id, server_name, name, create_uid, 
            write_uid, active, description, terms_conditons, short_desc,
            server_image, server_image_icon 
            from saas_portal_server"""
            if len(rec_ids) == 1 :
                server_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                server_master_query += """ where id in %s""" % tuple(rec_ids)
            self.env.cr.execute(server_master_query)
            server_master_data = self._cr.dictfetchall()
            return server_master_data

    @api.multi
    def get_server_feature_rel_data(self, res = False) :
        if res :
            rec_ids = res.ids
            server_feature_rel_query = """select * from server_feature_rel"""
            if len(rec_ids) == 1 :
                server_feature_rel_query += """ where server_id = %s""" % \
                                          rec_ids[0]
            if len(rec_ids) > 1 :
                server_feature_rel_query += """ 
                where server_id in %s""" % tuple(rec_ids)

            self.env.cr.execute(server_feature_rel_query)
            server_feature_rel_data = self._cr.dictfetchall()
            return server_feature_rel_data


class Saas_Portal_Server_Feature_Desc_Inherits(models.Model):
    _name = 'saas_portal.feature_description'
    _inherit = ['saas_portal.feature_description','update.wp_db']

    @api.model
    def create(self, vals):
        res = super(Saas_Portal_Server_Feature_Desc_Inherits, self).create(vals)
        server_feature_desc_data = self.get_server_feature_description_data(
            res)
        self.create_update_data(res, server_feature_desc_data)
        return res

    @api.multi
    def write(self, vals):
        result = super(Saas_Portal_Server_Feature_Desc_Inherits, self).write(vals)
        res = self
        server_feature_desc_data = self.get_server_feature_description_data(
            res)
        self.create_update_data(res, server_feature_desc_data)
        return result

    @api.multi
    def unlink(self):
        res = self
        server_feature_desc_data = self.get_server_feature_description_data(
            res)
        self.create_update_data(res, server_feature_desc_data, unlink = True)
        result = super(Saas_Portal_Server_Feature_Desc_Inherits, self).unlink()
        return result


    @api.multi
    def get_server_feature_description_data(self, res = False) :
        if res :
            rec_ids = res.ids
            server_feature_desc_query = """select * from 
                saas_portal_feature_description"""
            if len(rec_ids) == 1 :
                server_feature_desc_query += """ 
                    where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                server_feature_desc_query += """ 
                    where id in %s""" % tuple(rec_ids)
            self.env.cr.execute(server_feature_desc_query)
            server_feature_desc_data = self.env.cr.dictfetchall()
            return server_feature_desc_data
