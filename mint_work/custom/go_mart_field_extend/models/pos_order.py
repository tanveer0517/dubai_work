# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import api, models, fields
import logging
_logger = logging.getLogger(__name__)


class PosOrderInherited(models.Model):
    _inherit = 'pos.order'

    partner_id =  fields.Many2one("res.partner", "Partner" )
    phone = fields.Char(related="partner_id.phone", string="Phone", store=True)
    mobile = fields.Char(related="partner_id.mobile",string='Mobile')
    street2 = fields.Char(related="partner_id.street2",string='Street2')
    street = fields.Char(related="partner_id.street",string='Street')