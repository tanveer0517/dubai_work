# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools, _
from odoo.modules.module import get_module_resource


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _default_image(self) :
        image_path = get_module_resource('web_favicon', 'static/src/img', 'favicon.ico')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))


    favicon_backend = fields.Binary(default=_default_image)
    favicon_backend_mimetype = fields.Selection(
        selection=[('image/x-icon', 'image/x-icon'),
                   ('image/gif', 'image/gif'),
                   ('image/png', 'image/png')],
        help='Set the mimetype of your file.', default='image/x-icon')
