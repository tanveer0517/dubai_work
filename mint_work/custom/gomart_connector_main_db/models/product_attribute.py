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


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    gomart_attribute_id = fields.Integer('GoMart Attribute ID',
                                         readonly='True',
                                         help='This field will generate by GoMart.')
    _field_type = [
                    ('1', _('Characters')),
                    ('2', _('Numeric')),
                    ('3', _('Date')),
                    ('4', _('Time')),
                    ('5', _('Currency'))
                  ]
    _field_data_type = [
                        ('1', _('Free Text')),  # (For field_type Characters, Numeric or Currency),
                        ('2', _('Fixed'))  # (For field_type Characters, Numeric or Currency)
                      ]
    _fixed_values = [
                       ('1', _('Dropdown')),
                       ('2', _('Checkbox')),
                       ('3', _('Radio'))
                   ]
    no_charater = fields.Integer(string="No. of Characters")
    decimal_places = fields.Boolean(string="Decimal Places")
    interval_allowed = fields.Boolean(string="Interval Allowed ")
    measure_unit = fields.Boolean(string="Unit of Measure ")
    currency_type = fields.Boolean(string="Currency type")
    field_type = fields.Selection(selection=_field_type, string="Field Type")
    field_data_type = fields.Selection(selection=_field_data_type, string="Data Type ", default='1')
    group_id = fields.Many2one("product.group", string="Product Group")
    fixed_field_type = fields.Selection(selection=_fixed_values, string="Fixed Field Type ")

    @api.model
    def create(self, vals):
        rec = super(ProductAttribute, self).create(vals)
        _decimal_places = {True:1, False:0}
        _interval_allowed = {True:1, False:0}
        _measure_unit = {True:1, False:0}
        _currency_type = {True:1, False:0}
        _fixed_values = {True:1, False:2}
        fixed_vlued = [x.name for x in rec.value_ids]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        try:
            if gomart_server and gomart_server.name: 
                GroupFields_API = setGroupFields(
                                            gomart_server.name,
                                            rec.group_id.id,  # erp_group_id
                                            rec.id,  # erp_field_id
                                            rec.name,  # field_label
                                            rec.field_type,  # field_type
                                            rec.field_data_type,  # field_data_type
                                            rec.no_charater,  # no_of_chars
                                            _decimal_places.get(rec.decimal_places),  # decimal_places
                                            _interval_allowed.get(rec.interval_allowed),  # interval_allowed
                                            _measure_unit.get(rec.measure_unit),  # measure_unit
                                            _currency_type.get(rec.currency_type),  # currency_type
                                            rec.fixed_field_type,  # fixed_field_type
                                            fixed_vlued  # _fixed_values.get(rec.fixed_values)  # fixed_values
                                            )
                # Log
                _logger.warning("\n\n\n" + " Group Fields : " + 
                                "\n Data : " + str(GroupFields_API.get('data')) + 
                                "\n Status : " + str(GroupFields_API.get('status_code')) + 
                                "\n json_dump :" + str(GroupFields_API.get('json_dump'))
                                )
                if GroupFields_API.get('json_dump').get('code') == 200:
                        rec.gomart_attribute_id = GroupFields_API.get('field_id')
                else:
                    _logger.warning('GoMart APi setGroupFields,Invalid code %s' % 
                                    str(GroupFields_API.get('json_dump').get('code')) + 
                                     ' ' + 'GoMart error message %s' % 
                                     str(GroupFields_API.get('json_dump').get('error') or 'None.'))
            else:
                _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning('GoMart APi setGroupFields is not working or Server down.')
        return rec

    @api.multi
    def write(self, vals):
        rec = super(ProductAttribute, self).write(vals)
        _decimal_places = {True:1, False:0}
        _interval_allowed = {True:1, False:0}
        _measure_unit = {True:1, False:0}
        _currency_type = {True:1, False:0}
        _fixed_values = {True:1, False:2}
        fixed_vlued = [x.name for x in self.value_ids]

#         print "\n\n\n Fixed Valed  : ", fixed_vlued,        
#         print "\n Values : ",self.value_ids
#         print "Vales ::::::: ", vals
        gomart_server = self.env['gomart.server.api'].search([], limit=1)

#         currency_type = ''
#         if vals.get('currency_type'):
#             currency_type = _currency_type.get(vals.get('currency_type'))
#         else:
#             currency_type = _currency_type.get(self.currency_type)
# 
#         measure_unit = ''
#         if vals.get('measure_unit'):
#            measure_unit = _measure_unit.get(vals.get('measure_unit'))
#         else:
#            measure_unit = _measure_unit.get(self.measure_unit)
# 
#         interval_allowed = ''
#         if vals.get('interval_allowed'):
#             interval_allowed = _interval_allowed.get(vals.get('interval_allowed'))
#         else:
#             interval_allowed = _interval_allowed.get(self.interval_allowed)
# 
#         decimal_places = ''
#         if vals.get('decimal_places'):
#             decimal_places = _decimal_places.get(vals.get('decimal_places'))
#         else:
#             decimal_places = _decimal_places.get(self.decimal_places)

        try:
            if gomart_server and gomart_server.name: 
                # API setGroupFields
                GroupFields_API = setGroupFields(
                                            gomart_server.name,
#                                             vals.get('group_id') or 
                                            self.group_id.id,  # erp_group_id
                                            self.id,  # erp_field_id
#                                             vals.get('name') or 
                                            self.name,  # field_label
#                                             vals.get('field_type') or 
                                            self.field_type,  # field_type
#                                             vals.get('field_data_type') or 
                                            self.field_data_type,  # field_data_type
#                                             vals.get('no_charater') or 
                                            self.no_charater,  # no_of_chars

#                                             decimal_places,
                                            _decimal_places.get(self.decimal_places),  # decimal_places
#                                                 vals.get('decimal_places') or 
                                                                
#                                             interval_allowed,
                                            _interval_allowed.get(self.interval_allowed),  # interval_allowed
#                                                 vals.get('interval_allowed') or 
                                                                  
#                                             measure_unit,
                                            _measure_unit.get(self.measure_unit),  # measure_unit
#                                                 vals.get('measure_unit') or 
                                                              
#                                             currency_type,
                                            _currency_type.get(self.currency_type),  # currency_type
#                                                 vals.get('currency_type') or  
                                                               
#                                             vals.get('fixed_field_type') or 
                                            self.fixed_field_type,  # fixed_field_type
                                            fixed_vlued  # _fixed_values.get(vals.get('fixed_values') or self.fixed_values)  # fixed_values
                                            )
                # Log
                _logger.warning("\n\n\n" + " Group Fields : " + 
                                "\n Data : " + str(GroupFields_API.get('data')) + 
                                "\n Status : " + str(GroupFields_API.get('status_code')) + 
                                "\n json_dump :" + str(GroupFields_API.get('json_dump'))
                                )
#                 if GroupFields_API.get('json_dump').get('code') == 200:
#                     if GroupFields_API.get('field_id') != self.gomart_attribute_id:
#                         self.write({'gomart_attribute_id':GroupFields_API.get('field_id')})
                if GroupFields_API.get('json_dump').get('code') != 200:
                    _logger.warning('GoMart APi setGroupFields,Invalid code %s' % 
                        str(GroupFields_API.get('json_dump').get('code')) + 
                        ' ' + 'GoMart error message %s' % 
                        str(GroupFields_API.get('json_dump').get('error') or 'None.'))
            else:
                _logger.warning("Please configure correct GoMart APi server.")
        except:
            _logger.warning('GoMart APi setGroupFields is not working or Server down.')
        return rec
#     super(ProductAttribute, self).write(vals)

