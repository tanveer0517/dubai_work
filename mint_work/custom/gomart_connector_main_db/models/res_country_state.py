# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, exceptions
from gomartapi import *
import logging

_logger = logging.getLogger(__name__)


class CountryState(models.Model):
    _inherit = 'res.country.state'

    server_id = fields.Many2one('saas_portal.server', 'Server name')
    gomart_state_id = fields.Integer(string="GoMart State ID", readonly="True", help="This will be generate by the GoMart API.")
    is_active = fields.Boolean(string="Active", default="True", help="This is for the active or inactive status.")

    @api.model
    def create(self, vals):
        _active = {True:1, False:2}
        rec = super(CountryState, self).create(vals)
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        if rec.country_id.name == "United Arab Emirates":
                if gomart_server and gomart_server.name:
                    try: 
                        state_API = setState(gomart_server.name,
                                             rec.name,
                                             rec.id,
                                             _active.get(rec.is_active)
                                            )
                        # Log
                        _logger.warning("\n\n\n" + " State API : " + 
                                            "\n Data : " + str(state_API.get('data')) + 
                                            "\n Status : " + str(state_API.get('status_code')) + 
                                            "\n json_dump :" + str(state_API.get('json_dump')))
                        if state_API.get('json_dump').get('code') == 200:
                            rec.gomart_state_id = state_API.get('state_id')
                        else:
                            _logger.warning("GoMart APi setState,Invalid status code %s" % 
                                             str(state_API.get('json_dump').get('code')) + 
                                             ' ' + 'GoMart error message : %s' % 
                                              str(state_API.get('json_dump').get('error') or 'None.'))
                    except:
                        _logger.warning("GoMart APi setState not working or server Down.")
                else:
                    _logger.warning("Please configure correct GoMart APi server.")
        return rec

    @api.multi
    def write(self, vals):
        _active = {True:1, False:2}
        is_active = ''
        if _active.get(vals.get('is_active')):
            is_active = _active.get(vals.get('is_active'))
        else:
            is_active = _active.get(self.is_active)
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        if self.country_id.name == "United Arab Emirates":
                if gomart_server and gomart_server.name:

                    try:
                        state_API = setState(gomart_server.name,
                                             vals.get('name') or self.name,
                                             self.id,
                                             is_active)
#                                              _active.get(vals.get('is_active') or self.is_active))
                        # Log
                        _logger.warning("\n\n\n" + " State API : " + 
                                        "\n Data : " + str(state_API.get('data')) + 
                                        "\n Status : " + str(state_API.get('status_code')) + 
                                        "\n json_dump :" + str(state_API.get('json_dump')))
                        if state_API.get('json_dump').get('code') == 200:
                            vals.update({"gomart_state_id":state_API.get('state_id')})
                        else:
                            _logger.warning("GoMart APi setState,Invalid status code %s" % 
                                             str(state_API.get('json_dump').get('code')) + 
                                             ' ' + 'GoMart error message : %s' % 
                                              str(state_API.get('json_dump').get('error') or 'None.'))
                    except:
                        _logger.warning("GoMart APi setState not working or server Down.")
                else:
                    _logger.warning("Please configure correct GoMart APi server.")
        return super(CountryState, self).write(vals)
