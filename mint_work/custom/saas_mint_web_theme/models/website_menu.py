from odoo import api, fields, models, _

class Website_Menu_Inherit(models.Model):
    _inherit = 'website.menu'

    show_menu = fields.Boolean(string='Show Menu', default=True)
