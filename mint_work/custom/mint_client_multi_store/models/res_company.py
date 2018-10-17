# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import _, api, models, fields
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from lxml import etree


class store_time_schedule(models.Model):
    _name = "store.time.schedule"
    _order = 'dayofweek, hour_from'
    _rec_name = 'store_status'

    store_status = fields.Selection([('one', 'Open'),('zero', 'Close')],
                                  string="Store Status", default = 'one')
    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=True, index=True, default='0')
    # date_from = fields.Date(string='Starting Date')
    # date_to = fields.Date(string='End Date')
    hour_from = fields.Float(string='Work from', required=True, index=True, help="Start and End time of working.")
    hour_to = fields.Float(string='Work to', required=True)
    store_id = fields.Many2one('res.company')

    # _sql_constraints = [('unique_work_day', 'unique(store_id,dayofweek)',
    #                             _(" Deplicated employee in overtime ")), ]




class res_company(models.Model):
    _inherit = 'res.company'

    store_type = fields.Selection([('single', 'Single Store'),
                                   ('multi', 'Chained Store')],
                                  string="Store Type")
    number_of_outlets = fields.Integer('Number of Outlets')
    store_created = fields.Boolean('store ctreated')
    merchant_type = fields.Selection([('grocery', 'Grocery'),
                              ('restaurant', 'Restaurant')],
                                     string="Merchant Type")
    commission =  fields.Integer('Commission')
    password = fields.Char("Password")
    parent_comp_id = fields.Many2one('res.company', 'Child comp id')
    chain_store_ids = fields.One2many('res.company', 'parent_comp_id',
                                      'Chain Stores')
    other_prefix = fields.Char('Order Prefix')
    min_order_amt = fields.Float("Min. Order Amt")
    delivery_charge = fields.Float('Delivery Charge')
    delivery_charge_below = fields.Boolean('Delivery charge')
    deli_charge_below_order = fields.Float('Charge Amount')
    min_del_order_message = fields.Char('Charge Message')
    delivery_duration = fields.Integer('Delivery Duration')
    store_time_ids = fields.One2many(
        'store.time.schedule', 'store_id', string='Store Time',)
    payment_option = fields.Many2many('account.journal', string="Payment "
                                                               "Option")
    terms_and_conditions = fields.Text('Terms & Conditions')
    country_id = fields.Many2one('res.country', 'Country')
    loc_state_id = fields.Many2one('res.country.state', 'State')
    loc_city_id = fields.Many2one('city.city','City')
    location_ids = fields.Many2many('stock.location', string="Location")



    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        # Inherit this method for hide create button from tree view and form view
        # when we have single store. We can see effect in menu Store Setting ->
        # Store

        res = super(res_company, self).fields_view_get(view_id=view_id,
                                                        view_type=view_type,
                                                        toolbar=toolbar,
                                                        submenu=submenu)
        if self._context.get('company_id_custom'):
            if self.browse(1).store_type == 'single':
                doc = etree.XML(res['arch'])
                for node in doc.xpath(
                        "//form[@string='Company']"):
                    node.set('create', 'false')
                for node in doc.xpath(
                        "//tree[@string='Companies']"):
                    node.set('create', 'false')
                res['arch'] = etree.tostring(doc)
        return res

    @api.onchange('store_time_ids')
    @api.constrains('store_time_ids')
    def prevent_dupe_day(self):
        # This method add the constraiint on store time ids, We can assign
        # seven days for store time.
        if self.store_time_ids:
            if len(self.store_time_ids) > 7:
                raise UserError(_("You can assign only seven days for store "
                                  "time"))
            record_size = len(self.store_time_ids)
            day_count = len(set(self.store_time_ids.mapped('dayofweek')))
            if record_size != day_count:
                warning = {
                    'title': _('Duplicated Week of day'),
                    'message': _('Weekday already exist!')}
                return {'warning': warning}


    @api.onchange('delivery_charge_below')
    def onchange_below_delivery(self):
        # Onchange method for hide or show/hide charge related field
        if not self.delivery_charge_below:
            self.deli_charge_below_order = False
            self.min_del_order_message = False

