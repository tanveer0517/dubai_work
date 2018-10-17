# -*- coding: utf-8 -*-

import itertools
import logging
import operator


from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import WebClient
_logger = logging.getLogger(__name__)


class WebClient(WebClient):

    @http.route('/web/webclient/translations', type='json', auth="none")
    def translations(self, mods=None, lang=None):
        request.disable_db = False
        if mods is None:
            mods = [x['name'] for x in request.env[
                'ir.module.module'].sudo().search_read(
                [('state', '=', 'installed')], ['name'])]
        if lang is None:
            lang = request.context["lang"]
        langs = request.env['res.lang'].sudo().search([("code", "=", lang)])
        lang_params = None
        if langs:
            lang_params = langs.read([
                "name", "direction", "date_format", "time_format",
                "grouping", "decimal_point", "thousands_sep"])[0]

        # Regional languages (ll_CC) must inherit/override their parent lang
        # (ll), but this is
        # done server-side when the language is loaded, so we only need to
        # load the user's lang.
        translations_per_module = {}
        messages = request.env['ir.translation'].sudo().search_read([
            ('module', 'in', mods), ('lang', '=', lang),
            ('comments', 'like', 'openerp-web'), ('value', '!=', False),
            ('value', '!=', '')],
            ['module', 'src', 'value', 'lang'], order='module')
        get_source = False
        if not messages and request.context.get(
            'get_source', False) and (
                lang != request.context.get('lang', '') or lang == 'en_US'):

            messages = request.env['ir.translation'].sudo().search_read([
                ('module', 'in', mods),
                ('lang', '=', request.context.get('lang', False)),
                ('comments', 'like', 'openerp-web'), ('value', '!=', False),
                ('value', '!=', '')],
                ['module', 'src', 'value', 'lang'], order='module')
            get_source = messages and True or False
        for mod, msg_group in itertools.groupby(messages,
                                                key=operator.itemgetter(
                                                    'module')):
            translations_per_module.setdefault(mod, {'messages': []})
            translations_per_module[mod]['messages'].extend({
                'id': not get_source and m['src'] or m['value'],
                'string': not get_source and m['value'] or m['src']}
                for m in msg_group)
        return {
            'lang_parameters': lang_params,
            'modules': translations_per_module,
            'multi_lang': len(
                request.env['res.lang'].sudo().get_installed()) > 1,
        }
