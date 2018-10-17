# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaasServerFeatures(models.Model):
    _name = 'saas_portal.server.features'

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Master feature name Already Exist!'),
    ]

    name = fields.Char('Name', required=True, help="""Define the Feature 
    for which the server is Define.""")
    feature_list_ids = fields.Many2many('server.feature.list',
                                        'feature_list_rel', 'feature_id',
                                        'list_id',
                                        string="Feature List", required=True,
                                        help="""List down the Feature list
                                       related to this Server Feature.""")
    active = fields.Boolean('Active', default=True)


class ServerFeatureList(models.Model):
    _name = 'server.feature.list'

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'Master feature list name Already Exist!'),
    ]

    name = fields.Char('Feature Name', required=True, help="""Define the 
    Feature name for which this Feature is related to.""")
    active = fields.Boolean('Active', default=True)
