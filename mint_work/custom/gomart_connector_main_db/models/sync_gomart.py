# * coding: utf8 *
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

    @api.multi
    def state_sync_gomart(self):
        _active = {True:1, False:2}
        state_obj = self.env["res.country.state"]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        for rec in state_obj.search([]):
            if not rec.gomart_state_id and (rec.country_id.name == 'United Arab Emirates') and (rec.id and rec.name and rec.is_active):
                try:
                    if gomart_server and gomart_server.name: 
                        state_API = setState(gomart_server.name, rec.name, rec.id, _active.get(rec.is_active))
                        # Log
                        _logger.warning("\n\n\n" + " State API : \n" + " Data : " + str(state_API.get('data')) + "\n Status : " + str(state_API.get('status_code')) + "\n json_dump :" + str(state_API.get('json_dump')))
                        if state_API.get('status_code') == 200 and state_API.get('state_id'): 
                            if state_API.get('state_id'):
                                rec.write({"gomart_state_id":state_API.get('state_id')})
                        else:
                            msg = "GoMart setState API having issue %s \n\n Json Dump %s" % str(state_API.get('status_code'), state_API.get('json_dump'))
                            _logger.warning(msg)
                    else:
                        msg = "Please update correct GoMart APi server."
                        _logger.warning(msg)
                except:
                    msg = "GoMart APi setState is not working or server down."
                    _logger.warning(msg)
        return True


class CityCity(models.Model):
    _inherit = 'city.city'

    @api.multi
    def city_sync_gomart(self):
        _active = {True:1, False:2}
        city_obj = self.env["city.city"]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        for rec in city_obj.search([]):
            if (not rec.gomart_city_id) and (rec.id and rec.name and rec.code and rec.state_id.id and rec.is_active) and (rec.state_id.country_id.name == 'United Arab Emirates'):
                    try:
                        if gomart_server and gomart_server.name: 
                            city_recs = setCity(gomart_server.name, rec.id, rec.name, rec.code, rec.state_id.id, _active.get(rec.is_active))
                            _logger.warning("\n\n\n" + " City API : \n" + " Data : " + str(city_API.get('data')) + "\n Status : " + str(city_API.get('status_code')) + "\n json_dump :" + str(city_API.get('json_dump')))
                            if (city_recs.get("city_status") and city_recs.get('json_dump').get('code')) == 200:
                                if city_API.get("city_id"):
                                    rec.write({"gomart_city_id":city_API.get("city_id")})
                            else:
                                msg = "GoMart API setCity having invalid status code %s" % str(city_recs.get("city_status") or city_recs.get("status_code"))
                                _logger.warning(msg)
                        else:
                            msg = "Please update correct GoMart APi server."
                            _logger.warning(msg)
                    except:
                        msg = "GoMart API setCity is not working or server down."
                        _logger.warning(msg)
        return True


class CityArea(models.Model):
    _inherit = 'city.area'

    @api.multi
    def area_sync_gomart(self):
        _active = {True:1, False:2}
        locality_obj = self.env["city.area"]
        gomart_server = self.env['gomart.server.api'].search([], limit=1)
        for rec in locality_obj.search([]):
#             country_ids = (locality_obj.search([('United Arab Emirates', '=', rec.city_id.state_id.country_id.name)], limit=1))
            if (not rec.gomart_location_id) and (rec.id and rec.name and rec.city_id.state_id.id and rec.city_id.id and (rec.city_id.state_id.country_id.name == 'United Arab Emirates')):
                self.write(rec)
                try:
                    if gomart_server and gomart_server.name: 
                        loc_API = setLocation(
                                         gomart_server.name,
                                         rec.city_id.state_id.id ,  # erp_state_id
                                         rec.city_id.id,  # erp_city_id
                                         rec.id,  # erp_location_id
                                         rec.name,  # erp_location_name
                                         _active.get(rec.is_active)  # active
                                         )
                        # Log
                        _logger.warning("\n\n\n" + " Location API : \n" + " Data : " + str(loc_API.get('data')) + "\n Status : " + str(loc_API.get('status_code')) + "\n json_dump :" + str(loc_API.get('json_dump')))
                        if (loc_API.get("status_code") and loc_API.get('json_dump').get('code')) == 200:
                            if loc_API.get("location_id"):
                                rec.write({"gomart_location_id":loc_API.get("location_id")})
                        else:
                            msg = "GoMart APi setLocation having invalid status code %s " % str(loc_API.get('json_dump').get('code')) + "\n Message: %s" % str(loc_API.get('json_dump').get('error'))
                            _logger.warning(msg)
                    else:
                        msg = "Please update correct GoMart APi server."
                        _logger.warning(msg)
                except:
                    msg = "GoMart API setLocation is not working or server down."
                    _logger.warning(msg)
        return True

