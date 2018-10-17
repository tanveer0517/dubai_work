# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import  models, fields, api, exceptions, _
from gomartapi import *
import logging

_logger = logging.getLogger(__name__)


class ProductGroup(models.Model):
    _inherit = "product.group"

    gomart_group_id = fields.Integer('GoMart Group id', readonly='True', help='This field will be generate by GoMart API.')

    @api.model
    def create(self, vals):
        rec = super(ProductGroup, self).create(vals)
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                # API setGroup
                group_API = setGroup(gomart_server.name, rec.id, rec.name)
                # Log
                _logger.warning("\n\n\n" + " Group API : " + 
                                "\n Data : " + str(group_API.get('data')) + 
                                "\n Status : " + str(group_API.get('status_code')) + 
                                "\n json_dump :" + str(group_API.get('json_dump'))
                                )
                if group_API.get('json_dump').get('code') == 200 :
                        rec.gomart_group_id = group_API.get('group_id')
                else:
                    _logger.warning('GoMart APi setGroup with invalid  code is %s' % 
                                    str(group_API.get('json_dump').get('code')) + ' '
                                    +'GoMart message %s' % str(group_API.get('json_dump').get('error'))
                                   )
            else:
                _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning("GoMart APi setGroup is not working or server Down.")
        return rec

    @api.multi
    def write(self, vals):
        try:
            gomart_server = self.env['gomart.server.api'].search([], limit=1)
            if gomart_server and gomart_server.name: 
                # API setGroup
                group_API = setGroup(gomart_server.name, self.id, vals.get('name') or self.name)
                # Log
                _logger.warning("\n\n\n" + " Group API : " + 
                                "\n Data : " + str(group_API.get('data')) + 
                                "\n Status : " + str(group_API.get('status_code')) + 
                                "\n json_dump :" + str(group_API.get('json_dump'))
                                )
                if  group_API.get('json_dump').get('code') == 200 :
                    vals.update({'gomart_group_id':group_API.get('group_id')})
                else:
                    _logger.warning('GoMart APi setGroup with invalid  code is %s' % 
                                    str(group_API.get('json_dump').get('code')) + ' '
                                    +'GoMart message %s' % str(group_API.get('json_dump').get('error'))
                                   )
            else:
                _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning("GoMart APi setGroup is not working or server Down.")
        return super(ProductGroup, self).write(vals)

