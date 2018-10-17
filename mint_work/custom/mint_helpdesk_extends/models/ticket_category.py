# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ticket_category( models.Model):
    _name = "ticket.category"

    name = fields.Char(
        string    = "Name",
        size      = 32,
        required  = True,
        translate = True
    )

class ticket_call_type(models.Model):
        _name = "ticket.call.type"

        name = fields.Char(
            string="Name",
            size=32,
            required=True,
            translate=True
        )

    # deadline = fields.Many2one(
    #     comodel_name = "ticket.deadline",
    #     string       = "Deadline",
    #     required     = True,
    #     translate    = True
    # )
    #
    # agent_ids = fields.Many2many(
    #     comodel_name = "res.users",
    #     relation     = "agent_category_rel",
    #     column1      = "ticket_category_id",
    #     column2      = "helpdesk_agent_id",
    #     string       = "Agents",
    #     translate    = True
    # )
    #
    # @api.multi
    # def write( self, values ):
    #     # Clear record rules cache so that users can see appropriate tickets
    #     # if we change agents list.
    #     self.env[ "ir.rule" ].clear_caches()
    #
    #     return super( ibs_ticket_category, self ).write( values )
    #
    # @api.multi
    # def _get_agent_ids( self, category_id ):
    #     agent_obj = self.env[ "res.users" ]
    #     results   = {
    #         "ids"       : [],
    #         "least_busy": None
    #     }
    #
    #     if category_id:
    #         agent_ids = [
    #             agent.id for agent in self.browse( [
    #                 category_id
    #             ] ).agent_ids
    #         ]
    #
    #         least_busy = False
    #
    #         # Find the agent with the lowest number of open tickets.
    #         if len( agent_ids ):
    #             least_busy = agent_obj.browse( [ agent_ids[ 0 ] ] )
    #
    #             for agent in agent_obj.browse( agent_ids ):
    #                 if agent.open_tickets_number < least_busy.open_tickets_number:
    #                     least_busy = agent
    #
    #             results[ "least_busy" ] = least_busy.id
    #
    #         results[ "ids" ] = agent_ids
    #
    #     return results