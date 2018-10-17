 #-*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.exceptions import  Warning


class project_case_version(models.Model):
    _name = "project.case.version"
    _order = "name desc"
    name = fields.Char(string="student Name")
    active = fields.Boolean(string="student Name",default=True)
#    _columns = {
#        'name': fields.char('Version Number', required=True),
#        'active': fields.boolean('Active', required=False),
#    }
#    _defaults = {
#        'active': 1,
#    }
#from openerp.osv import fields, osv, orm
class project_case(models.Model):
    _name = "project.case"
    _description = "Project Case"
    _order = "priority desc, create_date desc"
    _inherit = ['mail.thread', 'mail.template', 'ir.needaction_mixin']

    _mail_post_access = 'read'

    STATE = [('draft','Draft'),('open_task', 'Open Task'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'), ('done', 'Done'),
             ('suspended', 'Suspended'), ('reopen', 'Reopen')]

    FOLDED_STATES = ['reopen']

    @api.model
    def stage_id_groups(self, ids, domain, **kwargs):
        """
        group by stage show all stages in kanban view.
        ----------------------------------------------
        :param ids: ids
        :param domain: domain
        :param kwargs:
        :return:
        """
        folded = {key: (key in self.FOLDED_STATES) for key in self.STATE}
        return self.STATE[:], folded

    _group_by_full = {
        'stage_id': stage_id_groups,
    }

    @api.model
    def _read_group_fill_results(self,  domain, groupby,
                                 remaining_groupbys, aggregated_fields,
                                 count_field, read_group_result,
                                 read_group_order=None):
        """
        The method seems to support grouping using m2o fields only,
        while we want to group by a simple status field.
        it replaces simple status values
        with (value, name) tuples.
        """
        if groupby == 'stage_id':
            STATES_DICT = dict(self.STATE)
            for result in read_group_result:
                state = result['stage_id']
                result['stage_id'] = (state, STATES_DICT.get(state))

        return super(project_case, self)._read_group_fill_results(
            domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result, read_group_order
        )

    @api.v7
    def _get_default_partner(self, cr, uid, context=None):
        project_id = self._get_default_project_id(cr, uid, context)
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, project_id, context=context)
            if project and project.partner_id:
                return project.partner_id.id
        return False

    @api.v7
    def _get_default_project_id(self, cr, uid, context=None):
        """ Gives default project by checking if present in the context """
        return self._resolve_project_id_from_context(cr, uid, context=context)

#     def _get_default_stage_id(self, cr, uid, context=None):
#         """ Gives default stage_id """
#         project_id = self._get_default_project_id(cr, uid, context=context)
#         return self.stage_find(cr, uid, [], project_id, [('fold', '=', False)], context=context)

    @api.v7
    def _resolve_project_id_from_context(self, cr, uid, context=None):
        """ Returns ID of project based on the value of 'default_project_id'
            context key, or None if it cannot be resolved to a single
            project.
        """
        if context is None:
            context = {}
        if type(context.get('default_project_id')) in (int, long):
            return context.get('default_project_id')
        if isinstance(context.get('default_project_id'), basestring):
            project_name = context['default_project_id']

            project_ids = self.pool.get('project.project').name_search(cr, uid, name=project_name, context=context)
            if len(project_ids) == 1:
                return int(project_ids[0][0])
        return None

    @api.v7
    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        access_rights_uid = access_rights_uid or uid
        stage_obj = self.pool.get('project.task.type')
        order = stage_obj._order
        # lame hack to allow reverting search, should just work in the trivial case
        if read_group_order == 'stage_id desc':
            order = "%s desc" % order
        # retrieve section_id from the context and write the domain
        # - ('id', 'in', 'ids'): add columns that should be present
        # - OR ('case_default', '=', True), ('fold', '=', False): add default columns that are not folded
        # - OR ('project_ids', 'in', project_id), ('fold', '=', False) if project_id: add project columns that are not folded
        search_domain = []
        project_id = self._resolve_project_id_from_context(cr, uid, context=context)
        if project_id:
            search_domain += ['|', ('project_ids', '=', project_id)]
        search_domain += [('id', 'in', ids)]
        # perform search
        stage_ids = stage_obj._search(cr, uid, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
        # restore order of the search
        result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = stage.fold or False
        return result, fold

    @api.v7
    def _compute_day(self, cr, uid, ids, fields, args, context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of Openday’s IDs
        @return: difference between current date and log date
        @param context: A standard dictionary for contextual values
        """
        Calendar = self.pool['resource.calendar']

        res = dict((res_id, {}) for res_id in ids)
        for case in self.browse(cr, uid, ids, context=context):
            values = {
                'day_open': 0.0, 'day_close': 0.0,
                'working_hours_open': 0.0, 'working_hours_close': 0.0,
                'days_since_creation': 0.0, 'inactivity_days': 0.0,
            }
            # if the working hours on the project are not defined, use default ones (8 -> 12 and 13 -> 17 * 5), represented by None
            calendar_id = None
            if case.project_id and case.project_id.resource_calendar_id:
                calendar_id = case.project_id.resource_calendar_id.id

            dt_create_date = datetime.strptime(case.create_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if case.date_open:
                dt_date_open = datetime.strptime(case.date_open, DEFAULT_SERVER_DATETIME_FORMAT)
                values['day_open'] = (dt_date_open - dt_create_date).total_seconds() / (24.0 * 3600)
                values['working_hours_open'] = Calendar._interval_hours_get(
                    cr, uid, calendar_id, dt_create_date, dt_date_open,
                    timezone_from_uid=case.user_id.id or uid,
                    exclude_leaves=False, context=context)

            if case.date_closed:
                dt_date_closed = datetime.strptime(case.date_closed, DEFAULT_SERVER_DATETIME_FORMAT)
                values['day_close'] = (dt_date_closed - dt_create_date).total_seconds() / (24.0 * 3600)
                values['working_hours_close'] = Calendar._interval_hours_get(
                    cr, uid, calendar_id, dt_create_date, dt_date_closed,
                    timezone_from_uid=case.user_id.id or uid,
                    exclude_leaves=False, context=context)

            days_since_creation = datetime.today() - dt_create_date
            values['days_since_creation'] = days_since_creation.days
            if case.date_action_last:
                inactive_days = datetime.today() - datetime.strptime(case.date_action_last, DEFAULT_SERVER_DATETIME_FORMAT)
            elif case.date_last_stage_update:
                inactive_days = datetime.today() - datetime.strptime(case.date_last_stage_update, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                inactive_days = datetime.today() - datetime.strptime(case.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
            values['inactivity_days'] = inactive_days.days

            # filter only required values
            for field in fields:
                res[case.id][field] = values[field]

        return res

    @api.v7
    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        task_pool = self.pool.get('project.task')
        res = {}
        for case in self.browse(cr, uid, ids, context=context):
            progress = 0.0
            if case.task_id:
                progress = task_pool._hours_get(cr, uid, [case.task_id.id], field_names, args, context=context)[case.task_id.id]['progress']
            res[case.id] = {'progress' : progress}
        return res

    @api.multi
    def on_change_state(self,stage_id):
        res = {}
        if stage_id == 'done':
            call_attended = self.call_attended
            call_deadline = self.call_deadline
            if call_attended < call_deadline:
                res['value'] = {'make_green' : True}
            if call_attended > call_deadline:
                res['value'] = {'make_red' : True}
            return res

    @api.multi
    def on_change_project(self,analytic_id):
        if analytic_id:
            analytic = self.env['account.analytic.account'].browse(analytic_id)
            project_id = self.env['project.project'].search([('analytic_account_id', '=', analytic.id)])
            res = {}
            res_values = {}
            if project_id:
                task_ids = self.env['project.task'].search([('project_id', '=', project_id.id)])
                res['domain'] = {'task_id':[('id','in',task_ids.ids)]}

            if analytic and analytic.partner_id:
                res_values['partner_id'] = analytic.partner_id.id
                res['value'] = res_values

                if analytic.sla_id:
                    res_values['sla_id'] = analytic.sla_id.id
                    res['value'] = res_values
            return res

        return {'value': {}}

    @api.multi
    def on_change_partner(self,partner_id):
        res_values = {}
        if partner_id:
            analytic_ids = self.env['account.analytic.account'].search([('partner_id', '=', partner_id)])
            res_values['domain'] = {'analytic_id':[('id','in',analytic_ids.ids)]}
        return res_values

    @api.multi
    def _get_case_task(self):
        cases = []
        case_pool = self.env['project.case']
        for task in self.env['project.task'].browse(self._cr, self._uid, self._ids, context=self._context):
            cases += case_pool.search([('task_id','=',task.id)])
        return cases

    @api.multi
    def _get_case_work(self):
        cases = []
        case_pool = self.env['project.case']
        for work in self.env['project.task.work'].browse(self._cr, self._uid, self._ids, context=self._context):
            if work.task_id:
                cases += case_pool.search([('task_id','=',work.task_id.id)])
        return cases

    @api.multi
    def send_mail(self):
       for case in self:
           template = self.env['ir.model.data'].get_object('project_case', 'email_template_case')
           if template:
             template.send_mail(case.id, force_send=True)
       return True


    @api.multi
    def _task_lines_cal(self):
        if self._context is None:self._context = {}
        res={}
        cases = ''

        task_obj = self.env['project.task']
        for id in self._ids:
            for case_mast in self.case_task_ids:
                for case_m_id in case_mast:
                    task_id = self.env['project.task'].search([('case_mast_id', '=', case_m_id.id)])
                    for tsk_id in task_id:
                        task_brw = task_obj.browse(tsk_id.id)
                        for work_id in task_brw.timesheet_ids:
    #                         cases += 'Summary : ' + work_id.name +','+'  Hours Spent : '+ str(work_id.hours) +','+'  Date : '+ work_id.date +','+'  Done By : '+ work_id.user_id.name+'\n'
                            cases += 'Summary : ' + work_id.name +'\n'
        self.action_taken = cases


    @api.multi
    def _call_deadline(self):
        res = {}
        for obj in self:

            case_recvd = obj.call_received
            if case_recvd:
                sla_deadline = obj.sub_sla_id.deadline_hrs
                date_deadline = datetime.strptime(case_recvd, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=sla_deadline or 0.0)
                date = date_deadline.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                res[obj.id] =  date
        return res

    @api.multi
    def _check_attended_date(self):
        for obj in self:
            call_received = obj.call_received
            call_attended = obj.call_attended

            if call_received and call_attended:
                if call_attended < call_received:
                    return False
        return True

    _constraints = [
            (_check_attended_date, 'Call Attended should be greater than call received', ['call_received','call_attended']),
        ]
#
    id = fields.Integer(string="ID",readonly=True)
    name = fields.Char(string="Case",required=True)
    message_summary=fields.Char('Message Summary')
    case_name = fields.Char(string="Case",required=True)
    active = fields.Boolean(string="Active",required=False,default=True)
    create_date = fields.Datetime(string="Creation Date",readonly=True, index=True)
    write_date = fields.Datetime(string="Update Date",readonly=True)
    date_deadline = fields.Date(string="Deadline")
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    contact_id = fields.Many2one('res.partner', 'Contact', required=False)
    company_id = fields.Many2one('res.company', 'Company')
    description = fields.Text(string="Private Note")
    action_taken = fields.Text(compute='_task_lines_cal', string='Action Taken')
    re_open = fields.Text(string="Reopen")
    kanban_state= fields.Selection([('normal','Normal'),('blocked','Blocked'),('done','Ready for next stage'),\
            ],string = 'Kanban State', track_visibility='onchange',help="A Case's kanban state indicates special situations affecting it:\n"
                                              " * Normal is the default situation\n"
                                              " * Blocked indicates something is preventing the progress of this case\n"
                                              " * Ready for next stage indicates the case is ready to be pulled to the next stage",required=False)
    email_from = fields.Char(string="Email",size=128, help="These people will receive email.", index=1)
    email_cc = fields.Char(string="Watchers Emails",size=256, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    date_open =  fields.Datetime(string='Assigned', readonly=True, index=True)
    date_closed =  fields.Datetime(string='Closed', readonly=True, index=True)
    channel =  fields.Char(string='Channel', help="Communication channel.")
    date_last_stage_update = fields.Datetime('Last Stage Update', index=True)
    channel = fields.Char('Channel', help="Communication channel.")
    categ_ids = fields.Many2many('project.tags', string='Tags')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority', index=True)
    case_origin = fields.Selection([('phone','Phone'), ('email','Email'), ('fax','Fax'), ('web_form','Web Form')], 'Case Origin', required=True)
    reported_by_id =  fields.Many2one('res.partner', 'Reported By', index=1)
    call_type = fields.Selection([('problem','Problem'), ('inquiry','Inquiry'), ('preventive_maint','Preventive Maintenance'), ('request','Request a Service')], 'Call Type', required=True)
    call_received = fields.Datetime(string='Case Received', required=True)
    call_attended = fields.Datetime(string='Case Attended')
    call_closed = fields.Datetime('Case Closed')
    call_deadline = fields.Datetime(compute='_call_deadline', string='Case Response Time')
    make_green = fields.Boolean(string='Green')
    make_red = fields.Boolean(string='Red')
    version_id = fields.Many2one('project.case.version', 'Version')
    case_task_ids = fields.One2many('case.task.mast','case_id', 'Tasks')
    stage_id = fields.Selection(STATE, 'Stage', track_visibility='onchange', domain="[('project_ids', '=', project_id)]",copy=False,default='open_task')
    project_id = fields.Many2one('project.project', 'Project', track_visibility='onchange', index=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Contract',required=False)
    sla_id =fields.Many2one('sla.main.mast','SLA', required=False)
    sub_sla_id = fields.Many2one('sub.sla','Sub SLA', required=False)
    duration = fields.Float(string='Duration')
    task_id = fields.Many2one('project.task', 'Task')
    day_open = fields.Float(compute='_compute_day', string='Days to Assign',
                                    multi='compute_day',
                                    store=True)
    day_close = fields.Float(compute='_compute_day', string='Days to Close',
                                     multi='compute_day',
                                     store=True)
    user_id  = fields.Many2one('res.users', 'Assigned to', required=False, index=1, track_visibility='onchange')
    working_hours_open = fields.Float(compute='_compute_day', string='Working Hours to assign the Case',
                                              multi='compute_day',
                                              store=True)
    working_hours_close = fields.Float(compute='_compute_day', string='Working Hours to close the case',
                                               multi='compute_day', type="float",
                                               store=True)
    inactivity_days = fields.Integer(compute='_compute_day', string='Days since last action',
                                           multi='compute_day',  help="Difference in days between last action and current date")
    color = fields.Integer(string='Color Index')
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True)
    date_action_last = fields.Datetime(string='Last Action', readonly=1)
    date_action_next = fields.Datetime(string='Next Action', readonly=1)
    progress = fields.Float(compute='_hours_get', string='Progress (%)', multi='hours', group_operator="avg", help="Computed as: Time Spent / Total Time.",
            store = True)
    ticket_group = fields.Many2one('ticket.group', string="Ticket Group")

    @api.model
    def create(self,vals):
        context = dict(self._context or {})
        vals['name'] = self.env['ir.sequence'].get('case')
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals.update(self.onchange_stage_id(vals.get('stage_id')))

        # context: no_log, because subtype already handle this
        create_context = dict(context, mail_create_nolog=True)
        case_id = super(project_case, self.with_context(create_context)).create(vals)
        return case_id

    @api.multi
    def write(self,vals):
        # stage change: update date_last_stage_update
        # if vals and vals.get('stage_id'):
            # if not self.analytic_id.id:
            #     raise Warning("Contract should be required !")
            # if not self.contact_id.id:
            #     raise Warning("Contact should be required !")
            # if not self.sla_id:
            #     raise Warning("SLA should be required !")
            # if not self.sub_sla_id:
            #     raise Warning("SLA should be required !")

        if self.stage_id == 'done':
            if vals.has_key('stage_id') and vals['stage_id'] != 'reopen':
                 raise Warning("You can't change the state once the case is done")

        if self.stage_id == 'suspended':
            if vals.has_key('stage_id') and vals['stage_id'] != 'reopen':
                raise Warning("You can't change the state once the case is suspended.")

        if 'stage_id' in vals:
            vals.update(self.onchange_done(vals.get('stage_id')))
            vals['date_last_stage_update'] = fields.Datetime.now()
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'

            if vals['stage_id'] == 'done':
                 vals['call_closed'] = fields.Datetime.now()
        # user_id change: update date_start
        if vals.get('user_id'):
            vals['date_open'] = fields.Datetime.now()

        return super(project_case, self).write(vals)

    @api.multi
    def onchange_done(self,stage_id):
        if stage_id == 'done':
            return {'value': {'date_time_closed': fields.Datetime.now()}}
        return {'value': {'date_time_closed': False}}

    @api.multi
    def onchange_contact_id(self,contact_id):
        """ This function returns value of contact email address based on partner
            :param part: Partner's id
        """
        result = {}
        if contact_id:
            partner = self.env['res.partner'].browse(contact_id)
            result['reported_by_id'] = partner.id
            result['email_from'] = partner.email
        return {'value': result}

    @api.multi
    def onchange_stage_id(self, stage_id):
        if not stage_id:
            return {'value': {}}
        if stage_id:
            return {'value': {'date_closed': fields.Datetime.now()}}
        return {'value': {'date_closed': False}}


class project(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_alias_models(self):
        res = super(project, self)._get_alias_models()
        res.append([('project.task', "Tasks"), ("project.case", "Cases")])
        return res

    @api.multi
    def _case_count(self):
        Case = self.env['project.case']
        return {
            project_id: Case.search_count([('project_id', '=', project_id)])
            for project_id in self._ids
        }

    project_escalation_id = fields.Many2one('project.project', 'Project Escalation',
            help='If any case is escalated from the current Project, it will be listed under the project selected here.',
            states={'close': [('readonly', True)], 'cancelled': [('readonly', True)]})
    case_count = fields.Integer(compute='_case_count',string="Cases")
    case_ids = fields.One2many('project.case', 'project_id')

    def _check_escalation(self, cr, uid, ids, context=None):
        project_obj = self.browse(cr, uid, ids[0], context=context)
        if project_obj.project_escalation_id:
            if project_obj.project_escalation_id.id == project_obj.id:
                return False
        return True

    _constraints = [
        (_check_escalation, 'Error! You cannot assign escalation to the same project!', ['project_escalation_id'])
    ]


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    @api.multi
    def _case_count(self):
        Case = self.env['project.case']
        return {
            analytic_id: Case.search_count([('analytic_id', '=', analytic_id)])
            for analytic_id in self._ids
        }
    use_cases = fields.Boolean('Cases', help="Check this field if this project manages cases")
    case_count = fields.Integer(compute='_case_count',string="Cases")
    sla_id = fields.Many2one('sla.main.mast', 'Case SLA')
    @api.multi
    def on_change_template(self,template_id, date_start=False):
        res = super(account_analytic_account, self).on_change_template(template_id, date_start=date_start)
        if template_id and 'value' in res:
            template = self.browse(cr, uid, template_id, context=context)
            res['value']['use_cases'] = template.use_cases
        return res

    @api.model
    def _trigger_project_creation(self, vals):
        res = super(account_analytic_account, self)._trigger_project_creation(vals)
        return res or (vals.get('use_issues') and not 'project_creation_in_progress' in self.env.context)



    # @api.v7
    # def _trigger_project_creation(self, cr, uid, vals, context=None):
    #     if context is None:
    #         context = {}
    #     res = super(account_analytic_account, self)._trigger_project_creation(cr, uid, vals, context=context)
    #     return res or (vals.get('use_cases') and not 'project_creation_in_progress' in context)


class project_project(models.Model):
    _inherit = 'project.project'

    _defaults = {
        'use_cases': True
    }
    @api.multi
    def _check_create_write_values(self,vals):
        """ Perform some check on values given to create or write. """
        # Handle use_tasks / use_cases: if only one is checked, alias should take the same model
        if vals.get('use_tasks') and not vals.get('use_cases'):
            vals['alias_model'] = 'project.task'
        elif vals.get('use_cases') and not vals.get('use_tasks'):
            vals['alias_model'] = 'project.case'
    @api.multi
    def on_change_use_tasks_or_cases(self,use_tasks, use_cases):
        values = {}
        if use_tasks and not use_cases:
            values['alias_model'] = 'project.task'
        elif not use_tasks and use_cases:
            values['alias_model'] = 'project.case'
        return {'value': values}
    @api.model
    def create(self,vals):
        self._check_create_write_values(vals)
        return super(project_project, self).create(vals)
    @api.multi
    def write(self,vals):
        self._check_create_write_values(vals)
        return super(project_project, self).write(vals)



class res_partner(models.Model):
    @api.multi
    def _case_count(self):
        Case = self.env['project.case']
        return {
            partner_id: Case.search_count([('partner_id', '=', partner_id)])
            for partner_id in self._ids
        }

    """ Inherits partner and adds case information in the partner form """
    _inherit = 'res.partner'

    case_count = fields.Integer(compute='_case_count',string='# Cases')


class case_type(models.Model):
    _name = 'case.type'

    name = fields.Char(string='Name',required=True)



class case_sla(models.Model):
    _name = 'case.sla'

    name = fields.Char(string='Name',required=True)
    code = fields.Selection([('p1','P1'), ('p2','P2'), ('p3','P3') , ('p4','P4')], 'Code', index=True)
    deadline_hrs = fields.Float(string='Deadline Hours')
    description = fields.Text(string='Description')


class case_task_mast(models.Model):
    _name = 'case.task.mast'

    @api.one
    def _hours_spent(self):
        if self._context is None:self._context = {}
        res={}
        task_obj = self.env['project.task']

        for case_m_id in self._ids:
            count = 0
            task_id = self.env['project.task'].search([('case_mast_id', '=', case_m_id)])
            for tsk_id in task_id:
                task_brw = task_obj.browse(tsk_id.id)
                for work_id in task_brw.timesheet_ids:
                    count+= work_id.unit_amount
        self.hours_spent=count



    case_task =fields.Integer(string='Task')
    assigned_to = fields.Many2one('res.users','Assigned to',required=True)
    department_id = fields.Many2one('hr.department','Department')
    case_id = fields.Many2one('project.case','Case')
    make_invisible = fields.Boolean(string='Invisible')
    hours_spent = fields.Float(compute='_hours_spent',string='Hours Spent')



    @api.multi
    def on_change_user(self,assigned_to):
        if assigned_to:
            user = self.env['res.users'].browse(assigned_to)
            employee_id = self.env['hr.employee'].search([('user_id', '=', user.id)])
            emp_brw = self.env['hr.employee'].browse(employee_id.id)
            res = {}
            res_values = {}
#
            if user:
                res_values['department_id'] = emp_brw.department_id.id
                res['value'] = res_values
            return res
#
        return {'value': {}}

    @api.multi
    def create_task(self):
        analytic = self.case_id.analytic_id
        task_obj = self.env['project.task']
        project_id = self.env['project.project'].search( [('analytic_account_id', '=', analytic.id)])
        vals = {}
        if project_id:
            task_ids = self.env['project.task'].search([('project_id', '=', project_id.id),  ('name', '=', self.department_id.name )])
            if task_ids:
                vals = {
                    'name': self.case_id.case_name +' '+'['+ self.case_id.name +']',
                    'project_id': project_id.id or False,
                    'user_id': self.assigned_to.id,
                    'reviewer_id': self.department_id.manager_id.user_id.id,
                    'sequence': 11,
                    'case_mast_id': self._ids[0],
                    'parent_ids':  [(6, 0, task_ids)],

                }

            else:
                vals = {
                    'name': self.case_id.case_name +' '+'['+ self.case_id.name +']',
                    'project_id': project_id.id or False,
                    'user_id': self.assigned_to.id,
                    'reviewer_id': self.department_id.manager_id.user_id.id,
                    'sequence': 11,
                    'case_mast_id': self._ids[0],

                }

        new_task_id = task_obj.create(vals)

        return {
            'name': _('Tasks'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'project.task',
            'res_id': new_task_id.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

class task(models.Model):
    _inherit = "project.task"

    case_mast_id = fields.Integer('IDs')


class sla_main_mast(models.Model):
    _name='sla.main.mast'

    name = fields.Char(string='SLA')


class sub_sla(models.Model):
    _name='sub.sla'

    name = fields.Char(string="Name",required=True)
    sla_id =fields.Many2one('sla.main.mast','SLA')
    code = fields.Char(string='Code')
    deadline_hrs = fields.Float(string='Deadline Hours')
    description = fields.Text(string='Description')


class TicketGroup(models.Model):

    _name = "ticket.group"

    name = fields.Char('Name')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
