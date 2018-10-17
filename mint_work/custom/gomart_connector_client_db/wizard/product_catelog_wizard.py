# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class addtocatalog(models.TransientModel):
    _name = 'product.catelog.wizard'

    @api.multi
    def store_product_catalog_gomart(self):
        if self._context and self._context.get('active_ids'):
            for pro in self._context.get('active_ids'):
                catalog_rec = self.env['product.template'].browse(pro)
                catalog_rec.add_to_catelog_gomart()
