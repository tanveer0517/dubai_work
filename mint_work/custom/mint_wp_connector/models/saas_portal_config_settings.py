# -*- coding: utf-8 -*-
import json
import MySQLdb

from odoo import models, fields, api, _
from odoo.exceptions import Warning, except_orm, UserError

class SaasPortalConfigWizardInherit(models.TransientModel):
    _name = 'saas_portal.config.settings'
    _inherit = ['saas_portal.config.settings', 'update.wp_db']

    def update_config_setting(self):
        config_setting_query = """select id, base_saas_domain
                    from saas_portal_config_settings
                    where id = %s""" % self.id
        self.env.cr.execute(config_setting_query)
        config_setting_data = self._cr.dictfetchall()
        res = self
        self.create_update_data(res, config_setting_data)
        return True

class SaasBusinessMasterInherit(models.Model):
    _name = 'business.type'
    _inherit = ['business.type', 'update.wp_db']

    @api.model
    def create(self, vals) :
        res = super(SaasBusinessMasterInherit, self).create(vals)
        business_master_data = self.get_business_master_data(res)
        self.create_update_data(res, business_master_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(SaasBusinessMasterInherit, self).write(vals)
        res = self
        business_master_data = self.get_business_master_data(res)
        self.create_update_data(res, business_master_data)
        return result

    @api.multi
    def unlink(self) :
        res = self
        business_master_data = self.get_business_master_data(res)
        self.create_update_data(res, business_master_data, unlink = True)
        result = super(SaasBusinessMasterInherit, self).unlink()
        return result

    @api.multi
    def get_business_master_data(self, res = False) :
        if res :
            rec_ids = res.ids
            business_master_query = """select id, name, active from 
            business_type """
            if len(rec_ids) == 1 :
                business_master_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                rec_ids = str(tuple(rec_ids))
                business_master_query += """ where id in %s""" % rec_ids
            self.env.cr.execute(business_master_query)
            business_master_data = self._cr.dictfetchall()
            return business_master_data

class ResBankInherit(models.Model):
    _name = 'res.bank'
    _inherit = ['res.bank', 'update.wp_db']

    @api.model
    def create(self, vals) :
        res = super(ResBankInherit, self).create(vals)
        res_bank_data = self.get_res_bank_data(res)
        self.create_update_data(res, res_bank_data)
        return res

    @api.multi
    def write(self, vals) :
        result = super(ResBankInherit, self).write(vals)
        res = self
        res_bank_data = self.get_res_bank_data(res)
        self.create_update_data(res, res_bank_data)
        return result

    @api.multi
    def unlink(self) :
        res = self
        res_bank_data = self.get_res_bank_data(res)
        self.create_update_data(res, res_bank_data, unlink = True)
        result = super(ResBankInherit, self).unlink()
        return result

    @api.multi
    def get_res_bank_data(self, res = False) :
        if res :
            rec_ids = res.ids
            res_bank_query = """select id, name, bic, active from res_bank """
            if len(rec_ids) == 1 :
                res_bank_query += """ where id = %s""" % rec_ids[0]
            if len(rec_ids) > 1 :
                rec_ids = str(tuple(rec_ids))
                res_bank_query += """ where id in %s""" % rec_ids
            self.env.cr.execute(res_bank_query)
            res_bank_data = self._cr.dictfetchall()
            return res_bank_data
