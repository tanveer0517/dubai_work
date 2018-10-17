# -*- coding: utf-8 -*-
from odoo import _, api, models, fields
from odoo.exceptions import Warning

class New_Client_Rejection(models.TransientModel):
    _name = 'new.client.document.rejection.wizard'

    # Params values in thier variable
    client_id = fields.Many2one('saas_portal.new.client', string = "Client ID")
    name = fields.Text('Rejection Reason', requred = True,
                       help = """Give A Ecommerce Name""")
    file_name = fields.Char('File Name')
    document = fields.Char('Document', required=True)

    @api.model
    def default_get(self, fields):
        res = super(New_Client_Rejection, self).default_get(fields)
        context = self.env.context or {}
        if not context.get('default_file_name'):
            raise Warning(_('Sorry!!, The Operation cannot be  Perform '
                            'as No File is Found.'))
        else:
            res.update({
                'client_id' : context.get('active_id'),
                'file_name' : context.get('default_file_name'),
                'document' : context.get('default_document')
            })
        return res

    @api.multi
    def confirm_rejection(self):
        context = self.env.context
        vals = {}
        rec = self.env['saas_portal.new.client'].browse(context.get('active_id'))
        rejection_rec = {
            'client_id' : self.client_id.id,
            'name' : self.name,
            'document' : self.document,
            'file_name' : self.file_name,
            'state' : 'rejected',
        }
        vals.update({
            'rejection' : [(0, 0, rejection_rec)],
            'state' : 'document_rejected',
        })

        if rec.emirates_id_card_name == self.file_name:
            vals.update({'emirates_id_card_rejected' : True,
                         'emirates_id_card_rejected_state': 'rejected'})
        if rec.passport_and_poa_name == self.file_name:
            vals.update({'passport_and_poa_rejected' : True,
                         'passport_and_poa_rejected_state': 'rejected'})
        if rec.vat_num_name == self.file_name :
            vals.update({'vat_num_rejected' : True,
                         'vat_num_rejected_state': 'rejected'})
        if rec.visa_and_poa_name == self.file_name :
            vals.update({'visa_and_poa_rejected' : True,
                         'visa_and_poa_rejected_state': 'rejected'})
        if rec.operating_address_uae_name == self.file_name :
            vals.update({'operating_address_uae_rejected' : True,
                         'operating_address_uae_rejected_state': 'rejected'})
        if rec.trade_license_name == self.file_name :
            vals.update({'trade_license_rejected' : True,
                         'trade_license_rejected_state': 'rejected'})
        rec.write(vals)
        template = self.env.ref(
            'saas_portal_enhancement.action_client_document_rejected')
        self.send_user_info_mail(template)

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

