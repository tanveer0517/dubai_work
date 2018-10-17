# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class BistaPlanSubscription(http.Controller):
    @http.route(['/plan_subscription'], type='http', auth='user',
                website=True)
    def plan_subscription(self, **post):
        # List down the plan information on subscription page for portal user.
        saas_portal_plan = request.env['saas_portal.plan']
        user_data = request.env['res.users']
        price_list_obj = request.env['product.pricelist']
        current_plan = False
        domain = [('state', 'in', ['confirmed']),
                  ('plan_type', 'in', ['subscription'])]
        plans = saas_portal_plan.sudo().search(
            domain,
            order='id asc'
        )
        if plans:
            if post.get('select_plan_type'):
                current_plan = post.get('select_plan_type')
            else:
                current_plan = plans[0].id
            price_data = {}
            saas_plan_data = saas_portal_plan.sudo().browse(int(
                current_plan)).plan_subscription_ids
            final_total = 0.0
            price_list = price_list_obj.sudo().search([])
            for product in saas_plan_data:
                new_price = price_list[0].price_get(product.product_id.id, 1, None)
                n_price = new_price.get(
                    price_list[0].id)
                price_data.update({product.product_id.id: n_price})
                final_total += n_price
            values = {
                'subscription': saas_portal_plan.sudo().browse(
                    int(current_plan)).plan_subscription_ids,
                'user_id': user_data.browse(request.uid),
                'plans' :plans,
                'final_total' : final_total,
                'current_selection' : int(current_plan),
                'price_list': price_list,
                'price_data' : price_data
            }

            return http.request.render(
                "saas_plan_subscription.client_subscription_form", values)
        else:
            values = {
                'subscription' : 0,
                'user_id' : user_data.browse(request.uid),
                'plans' : plans,
                'final_total' : 0.0,
                'current_selection' : int(),
            }
            return http.request.render(
                "saas_plan_subscription.client_subscription_form", values)


    @http.route(['/confirm_order'], type='json', auth='user', website=True)
    def confirm_order(self, **post):
        # Generate contract from portal user login by clicking on Confirm
        # button.
        res_users = request.env['res.users']
        line_dict = []
        analytic_account = request.env['account.analytic.account']
        if post.get('partner_id'):
            users_data = res_users.browse(int(post.get('partner_id')))
            post.update({'partner_id' : users_data.partner_id.id,
                         'name': 'Contract for ' +
                                 users_data.partner_id.name,
                         'client_id' :users_data.partner_id.id })
            for data in post.get('recurring_invoice_line_ids'):
                data.update({'uom_id':1})
                line_dict.append((0,0,data))
            post.update({'recurring_invoice_line_ids':line_dict})
            analytic_id = analytic_account.sudo().create(post)
            analytic_id.sudo().recurring_create_invoice()
        return True

    @http.route(['/redirect_confirm'], type='http', auth='user', website=True)
    def redirect_confirm(self, **post):
        # Redirect on successfull message template after contract generate
        # successfully.
        return http.request.render(
            "saas_plan_subscription.client_subscription_done")
