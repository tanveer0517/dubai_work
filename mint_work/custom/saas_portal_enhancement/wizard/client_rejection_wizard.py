# -*- coding: utf-8 -*-
from odoo import _, api, models, fields
from odoo.exceptions import Warning

class New_Client_Rejection(models.TransientModel):
    _name = 'new.client.rejection.wizard'

    # Params values in thier variable
    name = fields.Text('Rejection Reason', requred = True,
                       help = """Give A Ecommerce Name""")

    @api.multi
    def confirm_rejection(self):
        context = self.env.context
        vals = {}
        rec = self.env['saas_portal.new.client'].browse(context.get('active_id'))
        vals.update({
            'client_rejection_note' : self.name,
            'state' : 'rejected',
        })
        rec.write(vals)
        template = self.env.ref(
            'saas_portal_enhancement.action_client_request_rejected')
        rec.send_user_info_mail(template)
        rec.client_id.write({'active' : False})
        return True

    # Mailing Function which will be called from Several other Function
    @api.multi
    def send_user_info_mail(self, template = None) :
        # client_id = self.client_id.id
        rec = self.env['saas_portal.new.client']
        mail_configured = rec.check_outgoing_mail()
        if mail_configured and template != None :
            template.send_mail(self.id, force_send = True)
            return True
        else :
            raise Warning(_("Mail Template is Not Define or Not Found"))

