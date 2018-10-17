# -*- coding: utf-8 -*-
import json
import MySQLdb

from odoo import models, fields, api, _
from odoo.exceptions import Warning, except_orm, UserError


class SaasServerFeaturesInherits(models.Model):
    _name = 'saas_portal.server.features'
    _inherit = ['saas_portal.server.features','update.wp_db']

    @api.model
    def create(self, vals) :
        res = super(SaasServerFeaturesInherits, self).create(vals)
        feature_master_data = self.get_saas_portal_server_features_data(res)
        feature_list_rel_data = self.get_feature_list_rel_data(res)
        self.create_update_data(res, feature_master_data)
        self.create_update_data(res, feature_list_rel_data)
        return res

    @api.multi
    def write(self, vals):
        result = super(SaasServerFeaturesInherits, self).write(vals)
        res = self
        feature_master_data = self.get_saas_portal_server_features_data(res)
        feature_list_rel_data = self.get_feature_list_rel_data(res)
        self.create_update_data(res, feature_master_data)
        self.create_update_data(res, feature_list_rel_data)
        return result

    @api.multi
    def unlink(self):
        res = self
        feature_master_data = self.get_saas_portal_server_features_data(res)
        feature_list_rel_data = self.get_feature_list_rel_data(res)
        self.create_update_data(res, feature_master_data, unlink=True)
        self.create_update_data(res, feature_list_rel_data, unlink=True)
        result = super(SaasServerFeaturesInherits, self).unlink()
        return result

    @api.multi
    def get_saas_portal_server_features_data(self, res = False):
        if res:
            rec_ids = res.ids
            feature_master_query = """select *
                       from saas_portal_server_features"""
            if len(rec_ids) == 1:
                feature_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1:
                rec_ids = str(tuple(rec_ids))
                feature_master_query += """ where id in %s""" % rec_ids

            self.env.cr.execute(feature_master_query)
            feature_master_data = self._cr.dictfetchall()
            return feature_master_data

    @api.multi
    def get_feature_list_rel_data(self, res = False) :
        if res:
            rec_ids = res.ids
            feature_list_rel_query = """select * from feature_list_rel"""
            if len(rec_ids) == 1:
                feature_list_rel_query += """ where feature_id = %s""" % rec_ids[0]
            if len(rec_ids) > 1:
                rec_ids = str(tuple(rec_ids))
                feature_list_rel_query += """ where feature_id in %s""" % rec_ids

            self.env.cr.execute(feature_list_rel_query)
            feature_list_rel_data = self._cr.dictfetchall()
            return feature_list_rel_data


class ServerFeatureListinherits(models.Model):
    _name = 'server.feature.list'
    _inherit = ['server.feature.list','update.wp_db']

    @api.model
    def create(self, vals):
        res =super(ServerFeatureListinherits, self).create(vals)
        server_feature_list_data = self.get_server_feature_list_data(res)
        self.create_update_data(res, server_feature_list_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(ServerFeatureListinherits, self).write(vals)
        res = self
        server_feature_list_data = self.get_server_feature_list_data(res)
        self.create_update_data(res, server_feature_list_data)
        return result

    @api.multi
    def unlink(self):
        res = self
        server_feature_list_data = self.get_server_feature_list_data(res)
        self.create_update_data(res, server_feature_list_data, unlink = True)
        result = super(ServerFeatureListinherits, self).unlink()
        return result

    @api.multi
    def get_server_feature_list_data(self, res = False):
        if res:
            rec_ids = res.ids
            server_feature_list_query = """select * from server_feature_list """
            if len(rec_ids) == 1:
                server_feature_list_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1:
                rec_ids = str(tuple(rec_ids))
                server_feature_list_query += """ where id in %s""" % rec_ids
            self.env.cr.execute(server_feature_list_query)
            server_feature_list_data = self._cr.dictfetchall()
            return server_feature_list_data
