# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp

class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_code = fields.Char(string='Tax code')
    master_db_acc_tax_id = fields.Integer('Master DB ID', readonly = True)

    # Removing the constraint as this is not required
    # Can be enable it in future if required by business team.
    # _sql_constraints = [
    #     ('category_uniq', 'unique(tax_code)', _("A Tax code can only be assigned to one Tax !")),
    # ]

