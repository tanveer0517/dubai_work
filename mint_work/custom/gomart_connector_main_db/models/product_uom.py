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


class ProductUnit(models.Model):
    _inherit = "product.uom"

    server_id = fields.Many2one('saas_portal.server', 'Server name')
    go_mart_unit_id = fields.Integer("GoMart Unit ID", readonly=True, help="Unit ID will be generated by GoMart API.")

    @api.model
    def create(self, vals):
        _active = {True:1, False:2}
        uom = super(ProductUnit, self).create(vals)
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name:
                uom_API = setUnit(gomart_server.name, uom.id, uom.name, _active.get(uom.active))
                # Log
                _logger.warning("\n\n\n" + " Unit : " + 
                                "\n Data : " + str(uom_API.get('data')) + 
                                "\n Status : " + str(uom_API.get('status_code')) + 
                                "\n json_dump :" + str(uom_API.get('json_dump'))
                                )
                if (uom_API.get('json_dump').get('code')) == 200:
                        uom.go_mart_unit_id = uom_API.get('unit_id')
                else:
                    _logger.warning("GoMart API setUnit, Invalid code %s" % 
                            str(uom_API.get('json_dump').get('code'))  
                            +' ' + 'Error Message is %s' % 
                            str(uom_API.get('json_dump').get('error')))
            else:
                    _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning("GoMart APi setUnit not working or Server Down")
        return uom

    @api.multi
    def write(self, vals):
        vals_dict = {}
        _active = {True:1, False:2}
        is_active = ''
        if _active.get(vals.get('active')):
            is_active = _active.get(vals.get('active'))
        else:
            is_active = _active.get(self.active)

        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                unit_API = setUnit(gomart_server.name,
                                   self.id,
                                   vals.get('name') or self.name,
                                   is_active)
                # Log
                _logger.warning("\n\n\n" + " Unit : " + 
                                "\n Data : " + str(unit_API.get('data')) + 
                                "\n Status : " + str(unit_API.get('status_code')) + 
                                "\n json_dump :" + str(unit_API.get('json_dump'))
                                )
                if (unit_API.get('json_dump').get('code')) == 200:
                    vals.update({'go_mart_unit_id':unit_API.get('unit_id')})
                else:
                    _logger.warning("GoMart APi setUnit, Invalid status code %s" % 
                                    str(unit_API.get("json_dump").get("code")) + 
                                "  " + "GoMart error Message : %s" % 
                                str(unit_API.get("json_dump").get("error") or 'None'))
            else:
                _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning("GoMart APi setUnit not working or Server Down.")

        return super(ProductUnit, self).write(vals)
