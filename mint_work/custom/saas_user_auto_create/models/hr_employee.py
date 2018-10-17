# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2017 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import fields, api, models

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    res_group_id = fields.Many2one('res.groups', string = "Empower Group")

    @api.model
    def create(self, vals):
        res = super(hr_employee, self).create(vals)
        user_dic = {}
        user_dic.update({'name': vals.get('name'),
                'login': vals.get('work_email'),
                'email' : vals.get('work_email')
            })
        if vals.get('res_group_id'):
            user_dic.update({
                         'groups_id' : [(6, 0, [vals.get('res_group_id')])]
            })
        created_user_id = self.env['res.users'].create(user_dic)
        created_user_id.action_reset_password_custom()
        res.user_id = created_user_id
        return res
