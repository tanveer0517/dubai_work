# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from odoo.sql_db import db_connect
from odoo.http import request
from odoo import http, SUPERUSER_ID
from odoo.api import Environment

class project_case(models.Model):
    _inherit = 'project.case'

    @api.model
    def fields_view_get(self, view_id = None, view_type = 'form',
                        toolbar = False, submenu = False) :
        context = self._context
        new_stage = context.get('in_new_stage', False)
        open_stage = context.get('in_open_stage', False)
        progress_stage = context.get('in_progress_stage', False)
        print "\n\n\n\n context ---------",context, view_type
        res = super(project_case, self).fields_view_get(view_id = view_id,
                                                  view_type = view_type,
                                                  toolbar = toolbar,
                                                  submenu = submenu)
        doc = etree.XML(res['arch'])
        if (open_stage or progress_stage):
            for node_form in doc.xpath("//form"):
                node_form.set("create", 'false')
            for node_form in doc.xpath("//tree"):
                node_form.set("create", 'false')
            for node_form in doc.xpath("//kanban"):
                node_form.set("create", 'false')
        res['arch'] = etree.tostring(doc)

        return res

    @api.multi
    def _calculate_timesheet_ids(self):
        if self._context is None:self._context = {}
        res={}
        time_sheet = []

        task_obj = self.env['project.task']
        for id in self._ids:
            for case_mast in self.case_task_ids:
                for case_m_id in case_mast:
                    task_id = self.env['project.task'].search([('case_mast_id', '=', case_m_id.id)])
                    for tsk_id in task_id:
                        task_brw = task_obj.browse(tsk_id.id)
                        for work_id in task_brw.timesheet_ids:
                            time_sheet.append((4,work_id.id))
        self.timesheet_ids = time_sheet

    partner_id = fields.Many2one('res.partner', 'Customer', required=False)
    # client_id = fields.Many2one('saas_server.client', string='Client Details')
    case_origin = fields.Selection(
        [('phone', 'Phone'), ('email', 'Email'), ('fax', 'Fax'),
         ('web_form', 'Web Form')], 'Case Origin',required=False)
    call_type = fields.Selection(
        [('problem', 'Problem'), ('inquiry', 'Inquiry'),
         ('preventive_maint', 'Preventive Maintenance'),
         ('request', 'Request a Service')], 'Call Type', required=False)
    call_received = fields.Datetime(string='Case Received', required=False)
    source_id = fields.Many2one(
        comodel_name = "case.source",
        string       = "Source",
        readonly     = False,
        translate    = True
    )
    category = fields.Many2one(
        comodel_name="ticket.category",
        string="Category",
        readonly=False,
        ondelete="restrict",
        translate=True
    )
    call_type_id = fields.Many2one(
        comodel_name="ticket.call.type",
        string="Call type",
        readonly=False,
        ondelete="restrict",
        translate=True
    )
    timesheet_ids = fields.One2many('account.analytic.line', 'case_task_id',
                                    compute="_calculate_timesheet_ids",
                                    string="Task Entry")
    stage_id = fields.Selection(selection_add=[('open_task', 'Open')],
                                default= 'draft')

    @api.model
    def create(self, vals):
        # Write contract / subscription on helpdesk ticket.
        if vals.get('partner_id'):
            contract_id = self.env['account.analytic.account'].search([(
                'partner_id','=',vals.get('partner_id'))], limit=1)
            if contract_id:
                vals.update({'analytic_id':contract_id.id})
        res = super(project_case, self).create(vals)
        return res

    @api.multi
    def open_case(self):
        mod_obj_data = self.env["ir.model.data"]
        act_obj_data = self.env["ir.actions.act_window"]
        case = self.browse(self.ids[0])

        if case.stage_id != "draft":
            raise Warning(_("This case has already been opened."))

        result = mod_obj_data.get_object_reference('mint_helpdesk_extends'
            ,
            "action_case__open_wizard"
        )

        id = result and result[1] or False
        action = act_obj_data.browse([id])
        result = action.read()[0]
        result["target"] = "new"
        result["nodestroy"] = True
        new_context = dict(self.env.context).copy()
        new_context.update({"case_id": case.id})

        result["context"] = new_context
        return result

    @api.multi
    def case_inprogress(self):
        for rec in self:
            rec.stage_id = 'in_progress'

    @api.multi
    def case_onhold(self):
        for rec in self:
            rec.stage_id = 'on_hold'

    @api.multi
    def case_done(self):
        for rec in self:
            rec.stage_id = 'done'

    @api.multi
    def case_suspended(self):
        for rec in self:
            rec.stage_id = 'suspended'

    @api.multi
    def case_reopen(self):
        for rec in self:
            rec.stage_id = 'reopen'


class support_team(models.Model):
    _inherit = 'saas_portal.support_team'

    user_id = fields.Many2one('res.users', string='Support Manager')
    member_ids = fields.One2many('res.users', 'support_team_id',
                                 string='Team Members')

class case_source(models.Model):
    _name = "case.source"

    name = fields.Char("Name" , size=32)

class account_analytic_line(models.Model):
    _inherit="account.analytic.line"

    case_task_id = fields.Many2one('case.task.mast', string="Case Task")



class case_task_mast(models.Model):
    _inherit = 'case.task.mast'

    support_team_id = fields.Many2one('saas_portal.support_team',
                                      string="Support Team")



