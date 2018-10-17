# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    support_team_id = fields.Many2one(
        'saas_portal.support_team', 'Support Team',
        help='Sales Team the user is member of. Used to compute the members of a sales team through the inverse one2many')
