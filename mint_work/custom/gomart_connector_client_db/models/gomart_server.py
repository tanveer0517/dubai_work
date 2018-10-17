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
import re

_logger = logging.getLogger(__name__)

data_dict = {}


class GomartServerAPI(models.Model):
    _name = 'gomart.server.api'

    name = fields.Char(string="GoMart API URL", \
                        help="Enter the Valid API URL")

    @api.model
    def create(self, vals):
        recs = self.env['gomart.server.api'].search([])
        if len(recs) >= 1:
            msg = "You can not create more then one record." 
            _logger.warning(msg)
            raise exceptions.Warning(msg)
        else:
            if re.search('http', vals.get('name')):
                if re.search('api', vals.get('name')):
                    rec = super(GomartServerAPI, self).create(vals)
                    data_dict.update({'server':rec.name})
                    return rec
                else:
                    msg = "Please enter correct url with end 'api/'." 
                    _logger.warning(msg)
                    raise exceptions.Warning(msg)
            else:
                msg = "Please enter correct url with 'http'." 
                _logger.warning(msg)
                raise exceptions.Warning(msg)

    @api.multi
    def write(self, vals):
        recs = self.env['gomart.server.api'].search([])
        if len(recs) > 1:
            msg = "You can not create more then one record." 
            _logger.warning(msg)
            raise exceptions.Warning(msg)
        else:
            if re.search('http', vals.get('name')):
                if re.search('api', vals.get('name')):
                    rec = super(GomartServerAPI, self).write(vals)
                    data_dict.update({'server':self.name})
                    return rec
                else:
                    msg = "Please enter correct url with end 'api/'." 
                    _logger.warning(msg)
                    raise exceptions.Warning(msg)
            else:
                msg = "Please enter correct url with 'http'." 
                _logger.warning(msg)
                raise exceptions.Warning(msg)

