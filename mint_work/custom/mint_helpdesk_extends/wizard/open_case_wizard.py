# -*- coding: utf-8 -*-

from datetime import datetime
from lxml import etree
from odoo.osv.orm import setup_modifiers
from openerp import netsvc, SUPERUSER_ID, api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class open_case_wizard(models.TransientModel):
    _name = "open.case.wizard"

    category_id = fields.Many2one(
        comodel_name="ticket.category",
        string="Category",
        required=True,
        default=lambda self={}: ("case_id" in self.env.context) \
                                and self.env["project.case"].browse(
            self._context["case_id"]
        ).category.id or None,
        translate=True
    )
    case_id = fields.Many2one('project.case', string='Case', default=lambda self={}: ("case_id" in self.env.context) \
                                and self.env["project.case"].browse(
            self._context["case_id"]
        ).id or None)

    support_team_id = fields.Many2one('saas_portal.support_team',
                                      string="Support Team")

    sub_team_member = fields.Many2one(
        comodel_name="res.users",
        string="Assign to",
        required=True,
        translate=True
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client",
        translate=True
    )
    department_id = fields.Many2one('hr.department', string="Department")



    @api.multi
    def apply(self):
        vals = {}
        for record in self:
            vals.update({
                'assigned_to' : record.sub_team_member.id or False,
                'department_id' : record.department_id.id or False,
                'support_team_id' : record.support_team_id.id or False,
                'case_id' : record.case_id.id or False
                         })
            record.case_id.write({'stage_id':'open_task'})

            if vals:
                return self.env['case.task.mast'].create(vals)
                record.case_id.stage_id = 'open_task'
        return True

    # @api.model
    # def fields_view_get(self, view_id=None, view_type="form", toolbar=False):
    #     res = super(ibs_ticket_open_wizard, self).fields_view_get(
    #         view_id=view_id,
    #         view_type=view_type,
    #         toolbar=toolbar,
    #         submenu=False
    #     )
    #
    #     if self._context.get("ticket_id") == False:
    #         client = self.env["ibs.ticket"].browse(
    #             self._context["ticket_id"]
    #         ).client.id or None
    #
    #         doc = etree.XML(res["arch"])
    #         nodes = doc.xpath("//field[@name='client']")
    #
    #         for node in nodes:
    #             node.set("invisible", "0" if not client else "1")
    #             setup_modifiers(node, res["fields"]["client"])
    #
    #         res["arch"] = etree.tostring(doc)
    #
    #     return res
    #
    # @api.onchange("category")
    # def onchange_category_agents(self):
    #     category_obj = self.env["ibs.ticket.category"]
    #     agents = category_obj._get_agent_ids(self.category.id)
    #
    #     return {
    #         "domain": {"agent": [("id", "in", agents["ids"])]},
    #         "value": {"agent": agents["least_busy"]}
    #     }
    #
    # @api.model
    # def create(self, values):
    #     agent_obj = self.env["res.users"]
    #     ticket_obj = self.env["ibs.ticket"]
    #
    #     if "ticket_id" in self.env.context:
    #         agent_obj.check_ticket_capacity(values["agent"])
    #
    #         # getting the record
    #         ticket = ticket_obj.browse([self._context["ticket_id"]])
    #
    #         to_save = {
    #             "category": values["category"],
    #             "agent": values["agent"]
    #         }
    #
    #         if "client" in values and values["client"]:
    #             to_save["client"] = values["client"]
    #
    #         # Writing to record
    #         ticket.write(to_save)
    #         ticket.signal_workflow("open")
    #
    #     return super(ibs_ticket_open_wizard, self).create(values)
