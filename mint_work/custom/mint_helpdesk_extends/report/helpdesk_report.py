# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class HelpdeskReport(models.Model):
    _name = "helpdesk.report"
    _description = "Helpdesk Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    STATE = [('draft', 'Draft'), ('open_task', 'Open'),
             ('in_progress', 'In Progress'), ('on_hold', 'On Hold'),
             ('done', 'Done'),
             ('suspended', 'Suspended'), ('reopen', 'Reopen')]

    name = fields.Char('Case')
    date = fields.Datetime('Date Order')
    team_member_id = fields.Many2one('res.users', 'Support User', )
    support_team_id = fields.Many2one('saas_portal.support_team', 'Support '
                                                                 'Team',
                                readonly=True)
    stage_id = fields.Selection(STATE, 'Stage', track_visibility='onchange',
                                domain="[('project_ids', '=', project_id)]",
                                copy=False, default='open_task')
    company_id = fields.Many2one('res.company', 'Company', )
    analytic_id = fields.Many2one('account.analytic.account', 'Contract')
    partner_id = fields.Many2one('res.partner', 'Client')


    def _select(self):
        select_str = """SELECT min(pc.id) as id,
                    pc.name as name,
                    rs.id as team_member_id,
                    spst.id as support_team_id,
                    pc.stage_id as stage_id,
                    pc.call_received as date,
                    pc.company_id as company_id,
                    pc.analytic_id as analytic_id,
                    pc.partner_id as partner_id
        """
        return select_str

    def _from(self):
        from_str = """
                project_case pc
                join case_task_mast tcm  on (pc.id=tcm.case_id)
                join res_users rs on (tcm.assigned_to=rs.id)
                join saas_portal_support_team spst on (tcm.support_team_id = spst.id)
                join account_analytic_account aaa on (aaa.id = pc.analytic_id)
                join res_partner rp on (rp.id = pc.partner_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY pc.id,
                    rs.id,
                    spst.id,
                    pc.company_id,
                    pc.analytic_id,
                    pc.partner_id

        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
