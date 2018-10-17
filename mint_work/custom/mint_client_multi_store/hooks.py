# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_multi_company import hooks
except ImportError:
    _logger.info('Cannot find `base_multi_company` module in addons path.')


def post_init_hook(cr, registry):
    hooks.post_init_hook(
        cr,
        'mint_client_multi_store.product_catelog_multi_store_rule',
        'product.catelog',
    )


def uninstall_hook(cr, registry):
    hooks.uninstall_hook(
        cr,
        'mint_client_multi_store.product_catelog_multi_store_rule',
    )
