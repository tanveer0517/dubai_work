# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, Warning
import odoo.addons.decimal_precision as dp

import simplejson
import werkzeug

import requests
from odoo.addons.saas_base.exceptions import MaximumDBException, \
    MaximumTrialDBException
from odoo.http import request
from odoo.sql_db import db_connect
from odoo.api import Environment,SUPERUSER_ID
import ast

class saas_portal_plan_enhancement_Inherit(models.Model):
    _name = 'saas_portal.plan'
    _inherit = ['saas_portal.plan', 'update.wp_db']

    @api.model
    def create(self, vals) :
        res = super(saas_portal_plan_enhancement_Inherit, self).create(vals)
        plan_master_data = self.get_plan_features_data(res)
        self.create_update_data(res, plan_master_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(saas_portal_plan_enhancement_Inherit, self).write(vals)
        res = self
        plan_master_data = self.get_plan_features_data(res)
        self.create_update_data(res, plan_master_data)
        return result

    @api.multi
    def unlink(self):
        res = self
        plan_master_data = self.get_plan_features_data(res)
        self.create_update_data(res, plan_master_data, unlink=True)
        result = super(saas_portal_plan_enhancement_Inherit, self).unlink()
        return result

    @api.multi
    def get_plan_features_data(self, res = False) :
        if res :
            rec_ids = res.ids
            server_master_query = """select id, sequence,plan_price, name, 
            create_uid, write_uid, server_id, state, website_description, 
            summary, total_storage_limit, plan_type, sub_period, 
            recurring_rule_type, button_text, active from saas_portal_plan"""
            if len(rec_ids) == 1 :
                server_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                rec_ids = str(tuple(rec_ids))
                server_master_query += """ where id in %s""" % rec_ids
            self.env.cr.execute(server_master_query)
            server_master_data = self._cr.dictfetchall()
            for rec in server_master_data:
                button_text = str(rec.get('button_text'))
                if button_text == 'select_plan':
                    rec['button_text'] = 'Select Plan'
                if button_text == 'select_free_trial':
                    rec['button_text'] = 'Select Free Trial'
            return server_master_data


class PlanFeaturesMasterInherit(models.Model):
    _name = 'plan.features.master'
    _inherit = ['plan.features.master', 'update.wp_db']

    @api.model
    def create(self, vals):
        res = super(PlanFeaturesMasterInherit, self).create(vals)
        plan_feature_master_data = self.get_plan_features_master_data(res)
        self.create_update_data(res, plan_feature_master_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(PlanFeaturesMasterInherit, self).write(vals)
        res = self
        if not res:
            pass
        else:
            plan_feature_master_data = self.get_plan_features_master_data(res)
            self.create_update_data(res, plan_feature_master_data)
        return result

    @api.multi
    def unlink(self) :
        res = self
        plan_feature_master_data = self.get_plan_features_master_data(res)
        self.create_update_data(res, plan_feature_master_data, unlink = True)
        result = super(PlanFeaturesMasterInherit, self).unlink()
        return result

    @api.multi
    def get_plan_features_master_data(self, res = False) :
        if res :
            rec_ids = res.ids
            feature_master_query = """select *
                           from plan_features_master"""
            if len(rec_ids) == 1 :
                feature_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                rec_ids = str(tuple(rec_ids))
                feature_master_query += """ where id in %s""" % rec_ids

            self.env.cr.execute(feature_master_query)
            feature_master_data = self._cr.dictfetchall()
            return feature_master_data


class PlanFeatureListInherit(models.Model):
    _name = 'plan.feature.list'
    _inherit = ['plan.feature.list', 'update.wp_db']

    @api.model
    def create(self, vals) :
        res = super(PlanFeatureListInherit, self).create(vals)
        plan_feature_list_data = self.get_plan_features_list_data(res)
        self.create_update_data(res, plan_feature_list_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(PlanFeatureListInherit, self).write(vals)
        res = self
        if not res:
            pass
        else:
            plan_feature_list_data = self.get_plan_features_list_data(res)
            self.create_update_data(res, plan_feature_list_data)
        return result

    @api.multi
    def unlink(self) :
        res = self
        plan_feature_list_data = self.get_plan_features_list_data(res)
        self.create_update_data(res, plan_feature_list_data, unlink = True)
        result = super(PlanFeatureListInherit, self).unlink()
        return result

    @api.multi
    def get_plan_features_list_data(self, res = False):
        if res:
            rec_ids = res.ids
            feature_master_query = """select id, name, plan_feature_id, 
                        pfeature_list_id, checked, is_there, description,
                        write_uid, create_uid from plan_feature_list"""
            if len(rec_ids) == 1:
                feature_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1:
                rec_ids = str(tuple(rec_ids))
                feature_master_query += """ where id in %s""" % rec_ids

            self.env.cr.execute(feature_master_query)
            feature_master_data = self._cr.dictfetchall()
            for rec in feature_master_data:
                checked = rec.get('checked')
                if checked:
                    new_checked = str(rec.get('checked'))
                if not checked:
                    new_checked = str(rec.get('checked'))
                rec['checked'] = new_checked
            return feature_master_data
