# -*- coding: utf-8 -*-
from odoo import _, api, models, fields
from odoo import http, SUPERUSER_ID
from odoo.api import Environment
from odoo.sql_db import db_connect
from odoo.exceptions import Warning

class saas_plan_changed(models.TransientModel):
    _name = 'saas.plan.changed'

    exist_plan_id = fields.Many2one("saas_portal.plan",
                                    string="Existing Plan", readonly=True)
    plan_type = fields.Selection(
        [('trial', 'Trial'),('subscription', 'Subscription'),
         ], string = 'Existing Type')
    plan_changed = fields.Selection([('is_upgrade', 'Upgrade'),
                                     ('is_downgrade', 'Downgrade')],
                                    string="Upgrade Type")
    new_plan_id = fields.Many2one("saas_portal.plan", string="Choose Plan")

    @api.onchange('plan_changed')  # if these fields are changed, call method
    def plan_change(self):
        plan_obj = self.env['saas_portal.plan']
        if self.plan_changed == 'is_upgrade':
            new_plan_ids = plan_obj.search([('plan_wages','>',
                               self.exist_plan_id.plan_wages)])
        else:
            new_plan_ids = plan_obj.search(
                [('plan_wages', '<', self.exist_plan_id.plan_wages)])
        if new_plan_ids:
            return {'domain': {'new_plan_id': [('id', 'in', new_plan_ids.ids)]}}
        else:
            raise Warning(_("You can't Downgrade/Upgrade this plan!"))

    @api.one
    def plan_changed_process(self):
        if self.new_plan_id:
            if self.new_plan_id == self.exist_plan_id:
                raise Warning(_("Please select a new plan!"))
        if self.plan_changed == 'is_upgrade':
            if self._context.get('active_id'):
                client_id = self.env['saas_portal.client'].browse(self._context.get('active_id'))
                client_id.write({'plan_id':self.new_plan_id.id})
                list_process = {'install_addons':['point_of_sale']}
                config_id = self.env['saas.config'].create(list_process)
                config_id.do_upgrade_database(payload = list_process, database_record = client_id)
        else:
            if self._context.get('active_id'):
                module_in_db = self.env['ir.module.module']
                client_id = self.env['saas_portal.client'].browse(self._context.get('active_id'))
                client_id.write({'plan_id': self.new_plan_id.id})

                exi_plan_moduls = module_in_db.browse(
                    self.exist_plan_id.installed_module_ids.ids)
                down_plan_moduls = module_in_db.browse(
                    self.new_plan_id.installed_module_ids.ids)

                exi_mod,down_mod = [],[]
                [exi_mod.append(x.name)  for x in exi_plan_moduls]
                [down_mod.append(x.name) for x in down_plan_moduls]

                downgrade_module_list = list(set(exi_mod) - set(down_mod))

                new_cr = db_connect(str(client_id.name)).cursor()
                new_env = Environment(new_cr, SUPERUSER_ID, {})

                model_obj = new_env['ir.model']
                module_obj = new_env['ir.module.module']
                ir_model_acc_obj = new_env['ir.model.access']
                res_users = new_env['res.users'].search([])

                downgrade_module_ids = module_obj.search([('name','in',
                                                           downgrade_module_list)])

                down_group = new_env.ref(
                    'client_plan_upgrade.group_plan_downgrade')
                if res_users and down_group:
                    down_group.write({'users': [(4, res_users.ids)]})
                for every_user in res_users:
                    every_user.sudo().write(
                        {'client_module_ids': [(6, 0,
                                                downgrade_module_ids.ids)]})
                    new_cr.commit()
                client_module_ids = module_obj.search([('id','in',
                                                        downgrade_module_ids.ids)])
                for client_id in client_module_ids:
                    model_data = models.MetaModel.module_to_models.get(
                        client_id.name, [])
                    if model_data:
                        model_ids = []
                        for model in model_data:
                            model_obj_data =  model_obj.search([('model', '=',
                                               model._name)],
                                             limit=1)
                            if model_obj_data:
                                ir_model_acc_obj.sudo().create({
                                'name' : 'down_' + model_obj_data.name,
                                'model_id' : model_obj_data.id,
                                'group_id': down_group.id,
                                'perm_read': True,
                                })
                                access_data = ir_model_acc_obj.search([('model_id','=',model_obj_data.id)])
                                access_data.sudo().write({'perm_read': 1,
                                                          'perm_write':0,
                                                          'perm_create':0,
                                                          'perm_unlink':0})
                            model_ids.append(model_obj_data.id)
                            client_id.sudo().write({'model_ids': [(6, 0, filter
                            (None, model_ids))]})
                new_cr.commit()
                new_cr.close()


