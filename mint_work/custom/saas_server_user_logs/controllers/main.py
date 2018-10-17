# -*- coding: utf-8 -*-
from odoo import http
import functools
import datetime
from odoo import api, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.http import request
from odoo.sql_db import db_connect
from odoo.api import Environment
from datetime import datetime
import simplejson
from odoo.addons.saas_server.controllers.main import SaasServer

import logging
_logger = logging.getLogger(__name__)


def webservice(f):

    @functools.wraps(f)
    def wrap(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception as e:
            _logger.exception(str(e))
            return http.Response(response=str(e), status=500)

    return wrap


class SaasServerExtended(SaasServer):

    @http.route(['/saas_server/sync_server'], type='http', auth='public')
    @webservice
    def stats(self, **post):
        # Most useful method for data synchronization from portal instance
        # to client instance.
        # Update below data.
        # 1. Product.
        # 2. Creating product catelog.
        # 3. Product category.
        # 4. POS product category.
        # 5. Account tax.
        # 6. Product brand
        _logger.info('sync_server post: %s', post)
        state = simplejson.loads(post.get('state'))
        client_id = state.get('client_id')
        updating_client_ID = state.get('updating_client_ID')
        db = state.get('d')
        access_token = post['access_token']
        saas_oauth_provider = request.env.ref('saas_server.saas_oauth_provider').sudo()

        user_data = request.env['res.users'].sudo()._auth_oauth_rpc(saas_oauth_provider.validation_endpoint, access_token, local_host=saas_oauth_provider.local_host, local_port=saas_oauth_provider.local_port)
        if user_data.get("error"):
            raise Exception(user_data['error'])
        # Keep the code commented for future purpose
        # if updating_client_ID:
        #     client_rec = request.env['saas_server.client'].sudo().search([('client_id', '=', updating_client_ID)])
        #     if not client_rec:
        #         rec = []
        #         rec.append({
        #             'client_uuid': str(updating_client_ID),
        #             'client_not_found': True,
        #         })
        #         return simplejson.dumps(rec)
        if updating_client_ID:
            request.env['saas_server.client'].sudo().search([('client_id', '=', updating_client_ID)]).update_one()
        else:
            request.env['saas_server.client'].update_all()
        res = []
        main_cr = db_connect(str(state.get('main_db'))).cursor()
        main_env = Environment(main_cr, SUPERUSER_ID, {})
        products = main_env['product.template'].search([('is_subscription',
                                                         '=', False)])
        category = main_env['product.category'].search([('is_subscription', '=', False)])
        pcategory = main_env['pos.category'].search([])
        prod_brand = main_env['product.brand'].search([])
        prod_brand_att_data = main_env['ir.attachment'].search([(
            'name', '=', 'brand_img')])
        main_chart_account = main_env['account.account'].search([])
        main_tax = main_env['account.tax'].search([])

        # Synchronization from Master DB to client instances for city, state, area and country records
        try:
            city_ids = main_env['city.city'].search([("gomart_city_id", "!=", False)])
            area_ids = main_env['city.area'].search([("gomart_location_id", "!=", False)])
            state_ids = main_env['res.country.state'].search([("gomart_state_id", "!=", False)])
            country_ids = main_env['res.country'].search([])
        except:
            _logger.warning("Master DB having issue.Could not find generated id.")

        main_cr.commit()
        if updating_client_ID:
            client_rec = request.env['saas_server.client'].sudo().search([
                ('client_id', '=', updating_client_ID),
                ('state', 'not in', ['draft', 'cancelled', 'deleted'])])
        else:
            client_rec = request.env['saas_server.client'].sudo().search([(
                'state', 'not in', ['draft', 'cancelled', 'deleted'])])

        for client in client_rec:
            client_module_lst = []
            if client.client_type == 'client':
                new_cr = db_connect(str(client.name)).cursor()
                cr = new_cr
                new_env = Environment(new_cr, SUPERUSER_ID, {})
                local_mail = new_env['ir.module.module'].search([('state', '=', 'installed')])
                client_module_lst.append(local_mail.ids)
                catelog_obj = new_env['product.catelog']
                client_id = main_env['saas_portal.client'].search([('name', '=', client.name)], limit=1)

                account_tax_lst = {new_tax_rec.master_db_acc_tax_id for new_tax_rec in new_env['account.tax'].search([])}
                chart_account_lst = {new_chart_account.code for new_chart_account in new_env['account.account'].search([])}
                category_product_lst = {new_category.master_db_pro_cat_id for new_category in new_env['product.category'].search([])}
                pos_category_lst = {client_pos_category.master_db_pos_cat_id for client_pos_category in new_env['pos.category'].search(['|', ('active', '=', True), ('active', '=', False)])}
                product_brand_lst = {new_brand.master_db_brand_id for new_brand in new_env['product.brand'].search([])}
                product_templates_master_ids = {rec.master_db_product_id for rec in new_env['product.template'].search([])}

                city_lst = {new_city_rec.master_db_city_id for new_city_rec in new_env['city.city'].search([])}
                area_lst = {new_area_rec.master_db_area_id for new_area_rec in new_env['city.area'].search([])}
                state_lst = {new_state_rec.master_db_state_id for new_state_rec in new_env['res.country.state'].search([])}
                country_lst = {new_country_rec.master_db_country_id for new_country_rec in new_env['res.country'].search([])}

                # Pavan Code Country
                try:
                    for res_country in country_ids:
                        update_country = new_env['res.country'].search(['|', ('master_db_country_id', '=', res_country.id), ('name', '=', res_country.name)], limit=1)
                        if update_country or res_country.id in country_lst:
                            if client_id.server_id.id == res_country.server_id.id:
                                update_country.write({'name':res_country.name, 'master_db_country_id':res_country.id, 'code':res_country.code, 'address_format':res_country.address_format})
                        else:
                            if res_country.id not in country_lst and client_id.server_id.id == res_country.server_id.id:
                                cr.execute('insert into res_country (name,master_db_country_id,code,address_format) values (%s,%s,%s,%s)',
                                    (res_country.name, res_country.id, res_country.code, res_country.address_format))
                                res_country_rec = new_env['res.country'].search([('name', '=', res_country.name)])
                                if res_country.image:
                                    res_country_rec.image = res_country.image
                                cr.commit()
                except:
                    _logger.warning("Issue come with Sync Country")

                # Synchronizing states from main portal to client instances
                try:
                    for res_state in state_ids:
                        update_state = new_env['res.country.state'].search(['|', '|', ('master_db_state_id', '=', res_state.id), ('name', '=', res_state.name), ('code', '=', res_state.code)], limit=1)
                        if update_state  or (res_state.id in state_lst):
                            if client_id.server_id.id == res_state.server_id.id:
                                update_state.write({'name':res_state.name, 'master_db_state_id':res_state.id, 'code':res_state.code, 'country_id':res_state.country_id.id})
                        else:
                            if res_state.id not in state_lst and client_id.server_id.id == res_state.server_id.id:
                                cr.execute('insert into res_country_state (name,master_db_state_id,code,country_id) values (%s,%s,%s,%s)',
                                    (res_state.name, res_state.id, res_state.code, res_state.country_id.id))
                                cr.commit()
                except:
                    _logger.warning("Issue come with Sync State")

                # Synchronizing City information from Main Portal to client instances
                try:
                    for citys in city_ids:
                        update_citys = new_env['city.city'].search(['|', '|', ('master_db_city_id', '=', citys.id), ('name', '=', citys.name), ('code', '=', citys.code)], limit=1)
                        state_ids = new_env['res.country.state'].search([('master_db_state_id', '=', citys.state_id.id)], limit=1)
                        if update_citys or citys.id in city_lst:
                            if client_id.server_id.id == citys.server_id.id:
                                if state_ids:
                                    update_citys.write({'name':citys.name,
                                                        'master_db_city_id':citys.id,
                                                        'state_id':state_ids.id,
                                                        'code':citys.code ,
                                                        'country_id':citys.country_id.id })

                        else:
                            if citys.id not in city_lst and client_id.server_id.id == citys.server_id.id:
                                if state_ids:
                                    cr.execute('insert into city_city (name,master_db_city_id,code,state_id,country_id) values (%s,%s,%s,%s,%s)',
                                        (citys.name, citys.id, citys.code , state_ids.id , citys.country_id.id))
                                    cr.commit()
                except:
                    _logger.warning("Issue come with Sync City")

                # Synchronizing Area from main portal to client instances
                try:
                    for areas in area_ids:
                        update_areas = new_env['city.area'].search(['|', ('master_db_area_id', '=', areas.id), ('name', '=', areas.name)], limit=1)
                        city_ids = new_env['city.city'].search([('master_db_city_id', '=', areas.city_id.id)], limit=1)
                        if update_areas or areas.id in area_lst:
                            if client_id.server_id.id == areas.server_id.id:
                                if city_ids:
                                    update_areas.write({'name':areas.name, 'master_db_area_id':areas.id, 'city_id':city_ids.id})

                        else:
                                if areas.id not in area_lst and client_id.server_id.id == areas.server_id.id:
                                    if city_ids:
                                        cr.execute('insert into city_area (name,master_db_area_id,city_id) values (%s,%s,%s)',
                                            (areas.name, areas.id, city_ids.id))
                                        cr.commit()

                except:
                    _logger.warning("Issue come with Sync Area")

                try:
                    for new_tax in main_tax:
                        company_id = new_env['res.company'].search([], limit=1)
                        try:
                            if new_tax.id not in account_tax_lst and client_id.server_id.id == new_tax.server_id.id:
                                cr.execute(
                                    'insert into account_tax (name, type_tax_use, tax_code, amount_type, amount,description,tax_group_id, active, price_include,include_base_amount, tax_adjustment,sequence,company_id, master_db_acc_tax_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (new_tax.name, new_tax.type_tax_use, new_tax.tax_code, new_tax.amount_type, new_tax.amount, new_tax.description, new_tax.tax_group_id.id, new_tax.active, new_tax.price_include, new_tax.include_base_amount, new_tax.tax_adjustment, new_tax.sequence, company_id.id, new_tax.id))
                                cr.commit()
                                account_id = new_env['account.account'].search([('code', '=', new_tax.account_id.code)])
                                ref_account_id = new_env['account.account'].search(
                                    [('code', '=', new_tax.refund_account_id.code)])
                                new_ac_tax = new_env['account.tax'].search([('master_db_acc_tax_id', '=', new_tax.id)])
                                for update_account in account_id:
                                    if new_ac_tax:
                                        cr.execute("update account_tax set account_id=%s, refund_account_id=%s where id=%s",
                                                   (update_account.id, ref_account_id.id, new_ac_tax.id))
                                        cr.commit()
                        except:
                            _logger.warning("Issue come with the account tax creation in client db")

                        try:
                            if new_tax.id in account_tax_lst and client_id.server_id.id == new_tax.server_id.id:
                                update_tax = new_env['account.tax'].search([('master_db_acc_tax_id', '=', new_tax.id)])
                                if update_tax:
                                    cr.execute(
                                        "update account_tax set name=%s, type_tax_use=%s, tax_code=%s, amount_type=%s, amount=%s, description=%s, tax_group_id=%s, active=%s, price_include=%s, include_base_amount=%s, tax_adjustment=%s, sequence=%s, company_id=%s where id=%s",
                                        (new_tax.name, new_tax.type_tax_use, new_tax.tax_code, new_tax.amount_type, new_tax.amount, new_tax.description, new_tax.tax_group_id.id, new_tax.active, new_tax.price_include, new_tax.include_base_amount, new_tax.tax_adjustment, new_tax.sequence, company_id.id, update_tax.id))
                                    cr.commit()
                        except:
                            _logger.warning("Issue come with the account tax updation in client db")
                except :
                    _logger.warning("Issue Came with Account Tax Sync.")

                try:
                    for new_account in main_chart_account:
                        company_id = new_env['res.company'].search([], limit=1)
                        try:
                            if new_account.code not in chart_account_lst:
                                cr.execute(
                                      'insert into account_account (create_uid, create_date, code, name, user_type_id, company_id, reconcile, deprecated,internal_type) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (SUPERUSER_ID, datetime.now(), new_account.code, new_account.name, new_account.user_type_id.id, company_id.id, new_account.reconcile, new_account.deprecated, new_account.internal_type))
                                cr.commit()
                        except:
                            _logger.warning("Issue come with the account code creation in client db")

                        try:
                            if new_account.code in chart_account_lst:
                                upaccount = new_env['account.account'].search([('code', '=', new_account.code)])
                                for update_account in upaccount:
                                    if update_account:
                                        cr.execute("update account_account set code=%s, name=%s, user_type_id=%s, reconcile=%s, deprecated=%s, internal_type=%s where id=%s",
                                                   (new_account.code, new_account.name, new_account.user_type_id.id, new_account.reconcile, new_account.deprecated, new_account.internal_type, update_account.id))
                                        cr.commit()
                        except:
                            _logger.warning("Issue come with the account code Updation in client db")
                except :
                    _logger.warning("Issue Came with Chart of Account Sync.")

                try:
                    for my_category in category:
                        try:
                            if my_category.id not in category_product_lst and client_id.server_id.id == my_category.server_id.id:
                                remvoval = my_category.removal_strategy_id.id or None
                                cr.execute(
                                    'insert into product_category (name, type, category_id,removal_strategy_id, master_db_pro_cat_id) values (%s,%s,%s,%s, %s)',
                                    (my_category.name, my_category.type, my_category.category_id, remvoval, my_category.id))
                                cr.commit()
                        except:
                            _logger.warning("Issue came with Product Category while creating in client db")
                except :
                    _logger.warning("Issue Came wih Category Creation while Sync")

                try:
                    for my_category in category:
                        try:
                            if my_category.id not in category_product_lst and client_id.server_id.id == my_category.server_id.id:
                                if my_category.parent_id:
                                    parent_client = new_env['product.category'].search([('master_db_pro_cat_id', '=', my_category.parent_id.id)], limit=1)
                                    new_client_cate = new_env['product.category'].search([('master_db_pro_cat_id', '=', my_category.id)], limit=1)
                                    for update_parent in parent_client:
                                        if new_client_cate:
                                            cr.execute("update product_category set parent_id=%s where id=%s",
                                                       (update_parent.id, new_client_cate.id))
                                            cr.commit()
                        except:
                            _logger.warning("Issue came with Product Category while updation of parent category in client db")
                        try:
                            if my_category.id in category_product_lst:
                                update_category = new_env['product.category'].search([('master_db_pro_cat_id', '=', my_category.id)], limit=1)
                                update_category.write({
                                                        'master_db_pro_cat_id':my_category.id,
                                                        'name':my_category.name,
                                                        'type':my_category.type,
                                                        'category_id':my_category.category_id,
                                                        'removal_strategy_id':my_category.removal_strategy_id,
                                })
                        except:
                            _logger.warning("Issue came with Product Category while updation in client db")
                except :
                    _logger.warning("Issue Came with Updating Category while Sync")

                try:
                    for pos_category in pcategory:
                        try:
                            if pos_category.id not in pos_category_lst and client_id.server_id.id == pos_category.server_id.id:
                                cr.execute(
                                    'insert into pos_category (name, sequence, master_db_pos_cat_id, category_id,client_allow_product,active) values (%s,%s,%s,%s,%s,%s) RETURNING id',
                                    (pos_category.name, pos_category.sequence, pos_category.id, pos_category.category_id, pos_category.allow_product, False))
                                cr.commit()
                                master_db_pos_cat_id = cr.fetchall()[0][0]
                                new_pos_cate_rec = new_env['pos.category'].browse(master_db_pos_cat_id)
                                new_pos_cate_rec.image_medium = pos_category.image_medium
                        except:
                            _logger.warning("Issue came with the POS category creation in client db")
                except :
                    _logger.warning("Issue Came with POS Category Creation while Sync")

                try:
                    for pos_category in pcategory:
                        try:
                            if pos_category.id in pos_category_lst and client_id.server_id.id == pos_category.server_id.id:
                                if pos_category.parent_id:
                                    parent_clienteg = new_env['pos.category'].search([('master_db_pos_cat_id', '=', pos_category.parent_id.id), '|', ('active', '=', True), ('active', '=', False)], limit=1)
                                    pos_client_cate = new_env['pos.category'].search([('master_db_pos_cat_id', '=', pos_category.id), '|', ('active', '=', True), ('active', '=', False)],limit=1)
                                    for pos_update_parent in parent_clienteg:
                                        if pos_client_cate:
                                            cr.execute("update pos_category set parent_id=%s where id=%s",
                                                       (pos_update_parent.id, pos_client_cate.id))
                                            cr.commit()
                        except:
                            _logger.warning("Isssue came in POS category while updating the parent POS category in client db")
                        try:
                            if pos_category.id in pos_category_lst:
                                update_pos_category = new_env['pos.category'].search([('master_db_pos_cat_id', '=', pos_category.id), '|', ('active', '=', True), ('active', '=', False)], limit=1)
                                update_pos_category.write({
                                                            'name': pos_category.name,
                                                            'sequence': pos_category.sequence,
                                                            'category_id': pos_category.category_id,
                                                            'client_allow_product': pos_category.allow_product,
                                                            'image_medium': pos_category.image_medium,
                                                            'master_db_pos_cat_id':pos_category.id,
                                })
                        except:
                            _logger.warning("Isssue came in POS category while updating in client db")
                except :
                    _logger.warning("Issue Came with Updating POS Category while Sync")

                try:
                    for my_brand in prod_brand:
                        try:
                            if my_brand.id in product_brand_lst:
                                update_brand = new_env['product.brand'].search([('master_db_brand_id', '=', my_brand.id)], limit=1)
                                update_brand.write({
                                    'name':my_brand.name,
                                    'brand_img':my_brand.brand_img,
                                    'active':my_brand.active,
                                })
                        except :
                            _logger.warning("Issue Came with Updating Brand in client db")

                        try:
                            if my_brand.id not in product_brand_lst and client_id.server_id.id == my_brand.server_id.id:
                                cr.execute('insert into product_brand (name,active,master_db_brand_id) values (%s,%s,%s)',
                                    (my_brand.name, my_brand.active, my_brand.id))
                                brand_rec = new_env['product.brand'].search([('name', '=', my_brand.name)])
                                if my_brand.brand_img:
                                    brand_rec.brand_img = my_brand.brand_img
                                cr.commit()
                        except:
                            _logger.warning("Issue Came with creating Brand in client db")
                except :
                    _logger.warning("Issue Came with Product Brand Sync")


                model_product_category = new_env['product.category']
                model_pos_category = new_env['pos.category']
                model_account_account = new_env['account.account']
                model_account_tax = new_env['account.tax']
                model_product_template = new_env['product.template']
                model_product_image = new_env.get('product.image', None)
                model_product_brand = new_env['product.brand']

                sudo_catelog_obj = catelog_obj.sudo()
                sudo_product_tempalte = model_product_template.sudo()

                product_categories = model_product_category.search([(
                    'master_db_pro_cat_id', 'in', list({product.categ_id.id for product in products}))])
                pos_categories = model_pos_category.search([(
                    'master_db_pos_cat_id', 'in', list({product.pos_categ_id.id for product in products})), '|', ('active', '=', True), ('active', '=', False)])
                income_accounts = model_account_account.search([('code', 'in', list({product.property_account_income_id.code for product in products}))])
                expense_accounts = model_account_account.search([('code', 'in', list({product.property_account_expense_id.code for product in products}))])
                product_brands = model_product_brand.search([('master_db_brand_id', 'in', list({product.brand_id.id for product in products}))])

                product_categories_refs = {record.master_db_pro_cat_id:record for record in product_categories}
                pos_categories_refs = {record.master_db_pos_cat_id: record for record in pos_categories}
                income_accounts_refs = {record.code: record for record in income_accounts}
                expense_accounts_refs = {record.code: record for record in expense_accounts}
                prodcuct_brand_refs = {record.master_db_brand_id: record for
                                            record in product_brands}

                try:
                    for product in products:

                        if client_id in product.product_updated_on_clients_ids:
                            continue

                        if not client_id.server_id or not client_id.server_id.id == product.server_id.id:
                            continue

                        product_categ = product_categories_refs.get(product.categ_id.id, model_product_category)
                        pos_categ = pos_categories_refs.get(product.pos_categ_id.id, model_pos_category)
                        income_ac = income_accounts_refs.get(product.property_account_income_id.code, model_account_account)
                        expense_ac = expense_accounts_refs.get(product.property_account_expense_id.code, model_account_account)
                        product_brand = prodcuct_brand_refs.get(product.brand_id.id, model_product_brand)
                        # Taxes Synchronization from main portal to client instances
                        c_tax = model_account_tax.search([('master_db_acc_tax_id', 'in', list({c_tax.id for c_tax in product.taxes_id}))])
                        v_tax = model_account_tax.search([('master_db_acc_tax_id', 'in', list({v_tax.id for v_tax in product.supplier_taxes_id}))])
                        if product.id not in product_templates_master_ids:
                            try :
                                img_lst = []
                                for image_rec in product.image_ids:
                                    img_lst.append((0, 0, {'image': image_rec.image,
                                                           'name': image_rec.name,
                                                           'default': image_rec.default}))
                                product_vals = {'name': product.name,
                                                'master_db_product_id': product.id,
                                                'type': product.type,
                                                'categ_id': product_categ.id,
                                                'price': product.price,
                                                'default_code': product.default_code,
                                                'list_price': product.list_price,
                                                'image': product.image_medium,
                                                'sale_ok':product.sale_ok,
                                                'purchase_ok':product.purchase_ok,
                                                'property_stock_procurement':product.property_stock_procurement,
                                                'property_stock_production': product.property_stock_production,
                                                'property_stock_inventory': product.property_stock_inventory,
                                                'sale_delay':product.sale_delay,
                                                'available_in_pos':product.available_in_pos,
                                                'pos_categ_id':pos_categ.id,
                                                'to_weight':product.to_weight,
                                                'invoice_policy':product.invoice_policy,
                                                'description_sale':product.description_sale,
                                                'description_picking': product.description_picking,
                                                'barcode':product.barcode,
                                                'taxes_id':[(6, 0, c_tax.ids)],
                                                'supplier_taxes_id': [(6, 0, v_tax.ids)],
                                                'property_account_income_id':income_ac.id,
                                                'property_account_expense_id':expense_ac.id,
                                                'image_ids': img_lst,
                                                'brand_id' : product_brand.id
                                                }
                                client_product = sudo_product_tempalte.create(product_vals)
                                catelog_vals = {'pro_tmpl_ids': client_product.id, 'active': True,
                                                 'default_code': client_product.default_code,
                                                 'list_price': client_product.list_price,
                                                 'image': client_product.image_medium,
                                                 'categ_id':product_categ.id,
                                }
                                catelog_id = sudo_catelog_obj.create(catelog_vals)
                            except:
                                _logger.warning("Issue came with product creation in client db ")

                        elif product.id in product_templates_master_ids:
                            try:
                                update_products = model_product_template.search([('master_db_product_id', '=', product.id)])
                                image_ids = []
                                if model_product_image:
                                    for image_rec in product.image_ids:
                                        image_record = model_product_image.create({'image': image_rec.image,
                                                                         'name': image_rec.name,
                                                                         'default': image_rec.default})
                                        if image_record:
                                            image_ids.append(image_record.id)
                                if update_products:
                                    update_product_vals = {
                                        'name': product.name,
                                        'type': product.type,
                                        'categ_id': product_categ.id,
                                        'default_code': product.default_code,
                                        'image': product.image_medium,
                                        'sale_ok': product.sale_ok,
                                        'purchase_ok': product.purchase_ok,
                                        'property_stock_procurement': product.property_stock_procurement,
                                        'property_stock_production': product.property_stock_production,
                                        'property_stock_inventory': product.property_stock_inventory,
                                        'sale_delay': product.sale_delay,
                                        'available_in_pos': product.available_in_pos,
                                        'pos_categ_id': pos_categ.id,
                                        'to_weight': product.to_weight,
                                        'invoice_policy': product.invoice_policy,
                                        'description_sale': product.description_sale,
                                        'description_picking': product.description_picking,
                                        'barcode': product.barcode,
                                        'taxes_id': [(6, 0, c_tax.ids)],
                                        'supplier_taxes_id': [(6, 0, v_tax.ids)],
                                        'property_account_income_id': income_ac.id,
                                        'property_account_expense_id': expense_ac.id,
                                        'image_ids': [(6, 0, image_ids)],
                                        'brand_id' : product_brand.id
                                    }
                                    update_products.write(update_product_vals)
                                    for update_product in update_products:
                                        sudo_catelog_obj.search([('pro_tmpl_ids', '=', update_product.id)]).write({'image': update_product.image_medium})
                            except :
                                _logger.warning("Issue came with product updation in client db ")
                        # mark master db product as already updated for this client
                        product.product_updated_on_clients_ids = [(4, client_id.id, False)]
                except :
                    _logger.warning("Issue Came with Creation or Updation od Product")
                new_cr.commit()
                new_cr.close()

                main_cr.commit()
            res.append({
                'name': client.name,
                'state': client.state,
                'client_id': client.client_id,
                'users_len': client.users_len,
                'max_users': client.max_users,
                'state': client.state,
                'file_storage': client.file_storage,
                'db_storage': client.db_storage,
                'total_storage_limit': client.total_storage_limit,
                'installed_client_module_ids':[(6, 0, client_module_lst)]
            })
        main_cr.commit()
        main_cr.close()
        return simplejson.dumps(res)
