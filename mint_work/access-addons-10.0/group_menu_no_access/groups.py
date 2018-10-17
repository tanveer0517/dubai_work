# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID


class ResGroups(models.Model):
    _inherit = 'res.groups'

    menu_no_access = fields.Many2many('ir.ui.menu', 'ir_ui_menu_no_group_rel',
                                      'group_id', 'menu_id', 'No Access Menu')


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    no_groups = fields.Many2many('res.groups', 'ir_ui_menu_no_group_rel',
                                 'menu_id', 'group_id', 'No Groups')

    @api.multi
    @api.returns('self')
    def _filter_visible_menus(self):
        menus = super(IrUiMenu, self)._filter_visible_menus()

        if self.env.user.id != SUPERUSER_ID:
            groups = self.env.user.groups_id
            menus = menus.filtered(lambda menu: not(menu.no_groups & groups))
        return menus
