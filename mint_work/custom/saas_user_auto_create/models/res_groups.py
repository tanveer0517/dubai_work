# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models

class EmpowerGroup(models.Model):

    _inherit = 'res.groups'

    empower_group = fields.Boolean('Empower', help="If checked, this group is "
                                             "usable as a empower new "
                                                   "employee.")