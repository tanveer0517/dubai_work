
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import  now

class res_users(models.Model):
    _inherit = 'res.users'

    # This function will send mail template which will have user database
    # set password
    @api.multi
    def action_reset_password_custom(self):
        """ create signup token for each user, and send their signup url by
        email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset",
                                                 expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email',
                                        raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref(
                'saas_custom_mail_config.action_set_password_email')
        assert template._name == 'mail.template'
        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: "
                                  "user %s has no email address.") % user.name)
            template.with_context(lang=user.lang).send_mail(user.id,
                                                            force_send=True,
                                                            raise_exception=\
                                                            True)
