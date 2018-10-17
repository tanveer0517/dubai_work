odoo.define('mint_pos.models', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var _t = core._t;

    //Loads the product pricelist which has type sale.
    models.load_models({
        model: 'product.pricelist',
        fields: [],
        context: [
            ['type', '=', 'sale']
        ],
        loaded: function(self, prod_pricelists) {
            self.prod_pricelists = [];
            self.prod_pricelists = prod_pricelists;
        },
    });
    //Loads the states info.
    models.load_models({
        model: 'res.country.state',
        fields: [],
        context: [],
        loaded: function(self, states) {
            self.states = [];
            _.each(states, function(state) {
                self.states.push({
                    id: state.id,
                    value: state.name
                });
            });
        },
    });
  //Loads the country info.
    // models.load_models({
    //     model: 'res.country',
    //     fields: [],
    //     context: [],
    //     loaded: function(self, countries) {
    //         self.countries = [];
    //         _.each(countries, function(country) {
    //             self.countries.push({
    //                 id: country.id,
    //                 value: country.name
    //             });
    //         });
    //     },
    // });

    //Loads the property_product_pricelist field from partner object.
    models.load_fields("res.partner", ['property_product_pricelist']);
  //Loads the type and invoice policy field from product object.
    models.load_fields("product.product", ['type', 'invoice_policy']);

    // Overridden the Order class and set the helped methods for setting sale order information.
    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attr, options) {
            var self = this;
            var res = _super_Order.initialize.call(this, attr, options);
            this.set({
                'sale_order_name': false,
                'order_id': false,
                'shipping_address': false,
                'shipping_address_text': false,
                'invoice_address': false,
                'sale_note': false,
                'inv_id': false,
                'sale_order_date': false,
                'edit_quotation': false,
                'paying_sale_order': false,
                'sale_order_pay': false,
            });
            $('.js_edit_quotation').hide();
            $('#price_list').val('');
            $('#price_list').trigger('change', this);
        },
        set_sale_order_name: function(name) {
            this.set('sale_order_name', name);
        },
        get_sale_order_name: function() {
            return this.get('sale_order_name');
        },
        export_for_printing: function() {
            var orders = _super_Order.export_for_printing.call(this);
            var new_val = {
                sale_order_name: this.get_sale_order_name() || false,
                sale_note: this.get_sale_note() || '',

            };
            $.extend(orders, new_val);
            return orders;
        },
        set_sequence: function(sequence) {
            this.set('sequence', sequence);
        },
        get_sequence: function() {
            return this.get('sequence');
        },
        set_order_id: function(order_id) {
            this.set('order_id', order_id);
        },
        get_order_id: function() {
            return this.get('order_id');
        },
        set_amount_paid: function(amount_paid) {
            this.set('amount_paid', amount_paid);
        },
        get_amount_paid: function() {
            return this.get('amount_paid');
        },
        set_amount_return: function(amount_return) {
            this.set('amount_return', amount_return);
        },
        get_amount_return: function() {
            return this.get('amount_return');
        },
        set_amount_tax: function(amount_tax) {
            this.set('amount_tax', amount_tax);
        },
        get_amount_tax: function() {
            return this.get('amount_tax');
        },
        set_amount_total: function(amount_total) {
            this.set('amount_total', amount_total);
        },
        get_amount_total: function() {
            return this.get('amount_total');
        },
        set_company_id: function(company_id) {
            this.set('company_id', company_id);
        },
        get_company_id: function() {
            return this.get('company_id');
        },
        set_date_order: function(date_order) {
            this.set('date_order', date_order);
        },
        get_date_order: function() {
            return this.get('date_order');
        },
        set_pos_reference: function(pos_reference) {
            this.set('pos_reference', pos_reference)
        },
        set_pricelist_val: function(client_id) {
            var self = this;
            if (client_id) {
                new Model("res.partner").get_func("read")(parseInt(client_id), ['property_product_pricelist']).pipe(
                    function(result) {
                        if (result && result[0].property_product_pricelist) {
                            self.set('pricelist_val', result[0].property_product_pricelist[0] || '');
                            $('#price_list').val(result[0].property_product_pricelist[0]);
                            $('#price_list').trigger('change', this);
                        }
                    }
                );
            }
        },
        manual_set_pricelist_val: function(pricelist_id) {
            this.set('pricelist_val', pricelist_id);
        },
        get_pricelist: function() {
            return this.get('pricelist_val');
        },
        add_product: function(product, options) {
            var partner = this.get_client();
            var pricelist_id = parseInt($('#price_list').val()) || this.get_pricelist();
            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            var options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new models.Orderline({}, {
                pos: this.pos,
                order: this,
                product: product
            });
            var self = this;

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }
            if (options.price !== undefined) {
                line.set_unit_price(options.price);
            }
            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }

            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            var orderlines = [];
            if (this.orderlines) {
                orderlines = this.orderlines.models;
            }
            var found = false;
            var qty = line.get_quantity();
            for (var i = 0; i < orderlines.length; i++) {
                var _line = orderlines[i];
                if (_line && _line.can_be_merged_with(line) &&
                    options.merge !== false) {
                    _line.merge(line);
                    this.select_orderline(_line);
                    found = true;
                    break;
                }
            }
            if (!found) {
                this.orderlines.add(line);
                this.select_orderline(line);
            }
            if (partner) {
                if (pricelist_id) {
                    var added_line = this.get_selected_orderline();
                    var qty = this.get_selected_orderline().get_quantity();
                    new Model("product.pricelist").get_func('price_get')([pricelist_id], product.id, qty).pipe(
                        function(res) {
                            if (res[pricelist_id]) {
                                var pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                                if (pricelist_value) {
                                    added_line.set_unit_price(pricelist_value);
                                    added_line.set_is_pricelist_apply(true);
                                }
                            }
                        }
                    );
                }
            }
            if (line.has_product_lot) {
                this.display_lot_popup();
            }
        },
        set_client: function(client) {
            _super_Order.set_client.apply(this, arguments);
            if (client) {
                this.set_pricelist_val(client.id);
            } else {
                this.set_pricelist_val(0);
                $('#price_list').val("");
                $('#price_list').trigger('change', this);
            }
        },
        set_shipping_address: function(val) {
            this.set('shipping_address', val);
        },
        get_shipping_address: function() {
            return this.get('shipping_address');
        },
        set_shipping_address_text: function(val) {
            this.set('shipping_address_text', val);
        },
        get_shipping_address_text: function() {
            return this.get('shipping_address_text');
        },
        set_invoice_address: function(val) {
            this.set('invoice_address', val);
        },
        get_invoice_address: function() {
            return this.get('invoice_address');
        },
        set_sale_note: function(val) {
            this.set('sale_note', val);
        },
        get_sale_note: function() {
            return this.get('sale_note');
        },
        set_inv_id: function(inv_id) {
            this.set('inv_id', inv_id)
        },
        get_inv_id: function() {
            return this.get('inv_id');
        },
        set_sale_order_date: function(sale_order_date) {
            this.set('sale_order_date', sale_order_date)
        },
        get_sale_order_date: function() {
            return this.get('sale_order_date');
        },
        set_edit_quotation: function(edit_quotation) {
            this.set('edit_quotation', edit_quotation)
        },
        get_edit_quotation: function() {
            return this.get('edit_quotation');
        },
        set_paying_sale_order: function(paying_sale_order) {
            this.set('paying_sale_order', paying_sale_order)
        },
        get_paying_sale_order: function() {
            return this.get('paying_sale_order');
        },
        set_sale_order_pay: function(sale_order_pay) {
            this.set('sale_order_pay', sale_order_pay)
        },
        get_sale_order_pay: function() {
            return this.get('sale_order_pay');
        },
        get_total_quantity: function(){
            var currentOrderLines = this.get_orderlines();
            var total_qty = 0;
            _.each(currentOrderLines, function(line){
                total_qty += line.get_quantity();
            })
            return total_qty;
        },
    });

    //Overridden this method to set helper methods for pricelist.
    //Right now this methods are not used.
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_is_pricelist_apply: function(val) {
            this.is_pricelist_apply = val;
        },
        get_is_pricelist_apply: function() {
            return this.is_pricelist_apply;
        },
        set_manual_price: function(state) {
            this.manual_price = state;
        },
        can_be_merged_with: function(orderline) {
            var result = _super_orderline.can_be_merged_with.call(this, orderline);
            if (!result) {
                if (!this.manual_price) {
                    return (
                        this.get_product().id === orderline.get_product().id
                    );
                } else {
                    return false;
                }
            }
            return true;
        },
    });

    //Overridden POSModel class.
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        //Bind the update sale order count on pos sale order list.
        initialize: function(session, attributes) {
            _super_posmodel.prototype.initialize.call(this, session, attributes);
            var self = this
            function update_count_total() {
                self.update_count()
            }
            this.bind('change:pos_sale_order_list', update_count_total, this);
        },
        //Updates the count and set it on the sale order button.
        update_count: function(){
            var self = this;
            self.pending_orders_count = 0;
            _.each(self.get('pos_sale_order_list'), function(order){
                if(order.delivery_status == 'pending'){
                    self.pending_orders_count += 1;
                }
            })
            var order_count_value = document.getElementById('order_count');
            if(order_count_value){
                order_count_value.innerHTML = self.pending_orders_count;
            }
        },
        load_server_data: function() {
            var self = this;
            //Add domains on product and partner before loading the data.
            _.find(self.models, function(model) {
                if (model.model == "product.product") {
                    var new_domain = []
                    _.each(model.domain, function(o) {
                        if (o[0] !== _t("available_in_pos")) {
                            new_domain.push(o)
                        }
                    });
                    model.domain = new_domain;
                }
                if (model.model == "res.partner") {
                    var new_domain = []
                    _.each(model.domain, function(o) {
                        if ($.isArray(o)) {
                            if (o[0] !== _t("customer") && o[1] !== _t("=") && o[2] !== _t("true")) {
                                new_domain.push(o)
                            }
                        }
                    });
                    model.domain = new_domain;
                }
            })
            var loaded = _super_posmodel.prototype.load_server_data.call(this);
            loaded = loaded.then(function() {
                var date = new Date();
                var domain = [];
                var start_date;
                //Set the sale order last days.
                self.domain_sale_order = [];
                if (date) {
                    if (self.config.sale_order_last_days) {
                        date.setDate(date.getDate() - self.config.sale_order_last_days);
                    }
                    start_date = date.toJSON().slice(0, 10);
                    self.domain_sale_order.push(['create_date', '>=', start_date]);
                }
                //Add domain of sale order last days and fetch the sale order and add it into cache.
                var fields, offset, limit, order, context;
                self.domain_sale_order.push(['state', 'not in', ['cancel']])
                return new Model('sale.order').get_func('search_read')
                    (domain = self.domain_sale_order, fields = [], offset = 0, limit = 0, order = 'id desc', context = {
                        'show_address': true
                    })
                    .then(function(orders) {
                        self.db.add_sale_orders(orders);
                        self.set({
                            'pos_sale_order_list': orders
                        });
                    });
            });
            return loaded;
        },
        //Used to update the pricelist value of order if client is set on order.
        //Not used right now.
        set_order: function(order) {
            _super_posmodel.prototype.set_order.call(this, order);
            var order = this.get_order();
            if (order && order.get_client()) {
                order.set_pricelist_val(order.get_client().id);
                $('#price_list').val(order.get_pricelist());
            } else {
                $('#price_list').val('');
            }
        },
        //Helper method used to get the sale order data from the order.
        //Sends data to the server to update/pay the sale order.
        create_sale_order: function() {
            var self = this;
            var order = this.get_order();
            var currentOrderLines = order.get_orderlines();
            var customer_id = order.get_client().id;
            var location_id = false;
            var paymentlines = false;
            var paid = false;
            var confirm = false;
            var orderLines = [];
            for (var i = 0; i < currentOrderLines.length; i++) {
                orderLines.push(currentOrderLines[i].export_as_JSON());
            }
            if (self.config.sale_order_operations === "paid" || order.get_order_id() || order.get_edit_quotation()) {
                location_id = self.config.stock_location_id ? self.config.stock_location_id[0] : false;
                paymentlines = [];
                _.each(order.get_paymentlines(), function(paymentline) {
                    paymentlines.push({
                        'journal_id': paymentline.cashregister.journal_id[0],
                        'amount': paymentline.get_amount(),
                    })
                });
                paid = true
            }
            if (self.config.sale_order_operations === "confirm" && !order.get_edit_quotation()) {
                confirm = true;
            }
            var vals = {
                orderlines: orderLines,
                customer_id: customer_id,
                location_id: location_id,
                journals: paymentlines,
                pricelist_id: parseInt($('#price_list').val()) || order.get_pricelist() || false,
                partner_shipping_id: order.get_shipping_address() || customer_id,
                partner_invoice_id: order.get_invoice_address() || customer_id,
                note: order.get_sale_note() || "",
                inv_id: order.get_inv_id() || false,
                order_date: order.get_sale_order_date() || false,
                sale_order_id: order.get_order_id() || false,
                edit_quotation: order.get_edit_quotation() || false,
                amount_return: order.get_change(),
            }
            new Model('sale.order').call('create_sales_order', [vals,
                    {
                        'confirm': confirm,
                        'paid': paid
                    }
                ], {}, {
                    async: false
                })
                .then(function(sale_order) {
                    if (sale_order && sale_order[0]) {
                        sale_order = sale_order[0];
                        if (paid && order.get_paying_sale_order()) {
                            $('#btn_so').show();
                            if (sale_order) {
                                order.set_sale_order_name(sale_order.name);
                            }
                            self.gui.show_screen('receipt');
                        } else {
                            var edit = order.get_edit_quotation();
                            var url = window.location.origin + '/web#id=' + sale_order.id + '&view_type=form&model=sale.order';
                            self.gui.show_popup('saleOrder', {
                                'url': url,
                                'name': sale_order.name,
                                'edit': edit
                            });

                        }
                        var record_exist = false;
                        _.each(self.get('pos_sale_order_list'), function(existing_order) {
                            if (existing_order.id === sale_order.id) {
                                _.extend(existing_order, sale_order);
                                record_exist = true;
                            }
                        });
                        if(record_exist){
                            if (paid && order.get_paying_sale_order()) {
                                var defined_orders = self.get('pos_sale_order_list');
                                var new_orders = _.filter(defined_orders, function(so){
                                    return so.id != sale_order.id
                                })
                                self.db.add_sale_orders(new_orders);
                                self.set({
                                    'pos_sale_order_list': new_orders
                                })
                            }
                        }
                        if (!record_exist) {
                            var exist = _.findWhere(self.get('pos_sale_order_list'), {
                                id: sale_order.id
                            });
                            if (!exist) {
                                var defined_orders = self.get('pos_sale_order_list');
                                var new_orders = [sale_order].concat(defined_orders);
                                self.db.add_sale_orders(new_orders);
                                self.set({
                                    'pos_sale_order_list': new_orders
                                })
                            }

                        }
                    }
                }).fail(function(err, event) {
                    if (paid) {
                        $('#btn_so').show();
                    }
                    self.gui.show_popup('error', {
                        'title': _t('Error: Could not Save Changes'),
                    });
                    event.preventDefault();
                });
        },
    });
});
