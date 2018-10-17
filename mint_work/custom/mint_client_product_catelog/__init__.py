# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from . import models
from . import wizard
from odoo import api, SUPERUSER_ID

def _update_product_category_client(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # pro_id = env.ref('point_of_sale.product_product_consumable')
    # if pro_id:
    #     pro_id.unlink()
    # categ_id = env.ref('product.product_category_1')
    # if categ_id:
    #     categ_id.unlink()
    # categ_all = env.ref('product.product_category_all')
    # if categ_all:
    #     categ_all.unlink()
