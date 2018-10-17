from openerp import models, fields, api, _


class website_support_project_case(models.Model):
    _inherit = "project.case"

    attachment = fields.Binary(string="Attachments")
    attachment_filename = fields.Char(string="Attachment Filename")
    conversation_history = fields.One2many('page.case.ticket.message', 'project_case_id',
                                           string="Conversation History")


class WebsiteSupportTicketMessage(models.Model):

    _name = "page.case.ticket.message"

    project_case_id = fields.Many2one('project.case', string='Ticket ID')
    content = fields.Text(string="Message")
    mesage_from = fields.Text(string="From", default=lambda self: self.env.user.name)
    filename = fields.Char(string="File Name")
    attachment = fields.Binary(string='Attachment')
    attachment_id = fields.Many2one('ir.attachment',string='Attachment')

    @api.model
    def create(self, vals):
        """
        :param vals:
        :return:
        """
        if vals.get('attachment'):
            Attachments = self.env['ir.attachment']
            attachment_id = Attachments.create({
                'name': vals.get('filename', ''),
                'datas': vals.get('attachment'),
                'datas_fname': vals.get('filename', ''),
                'public': True,
                'res_model': 'ir.ui.view',
            })
            vals['attachment_id'] = attachment_id.id
        res = super(WebsiteSupportTicketMessage, self).create(vals)
        return res
