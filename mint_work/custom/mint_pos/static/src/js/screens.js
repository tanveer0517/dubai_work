odoo.define('mint_pos.screens', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var formats = require('web.formats');
    var time = require('web.time');

    var QWeb = core.qweb;
    var _t = core._t;

    //Sale Order button class.
    //On click it will open sale order popup.
    var SaleOrderButton = screens.ActionButtonWidget.extend({
        template: 'SaleOrderButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var currentOrderLines = order.get_orderlines();
            if (currentOrderLines.length <= 0) {
                alert('No product selected !');
            } else if (order.get_client() == null) {
                alert('Please select customer !');
            } else {
                self.gui.show_popup('sale_order_popup', {
                    'sale_order_button': self
                });
            }
        },
    });

    //Define update sale order button on screens.
    screens.define_action_button({
        'name': 'saleorder',
        'widget': SaleOrderButton,
        'condition': function() {
            return this.pos.config.sale_order_operations == "draft" || this.pos.config.sale_order_operations == "confirm" || this.pos.get_order().get_edit_quotation();
        },
    });

    //Sale Order button for displaying sale order screen.
    //On click it will redirect user to sale order list screen.
    var ViewSaleOrdersButton = screens.ActionButtonWidget.extend({
        template: 'ViewSaleOrdersButton',
        button_click: function() {
            this.gui.show_screen('saleorderlist');
        },
    });

    //Define sale order button on screens.
    screens.define_action_button({
        'name': 'viewsaleorder',
        'widget': ViewSaleOrdersButton,
        'condition': function(){
            return this.pos.config.allow_online_orders
        },
    });

    //Edit Quotation button class.
    //On button click open sale order popup.
    var EditQuotationButton = screens.ActionButtonWidget.extend({
        template: 'EditQuotationButton',
        button_click: function() {
            var self = this;
            var order = this.pos.get_order();
            var currentOrderLines = order.get_orderlines();
            if (currentOrderLines.length <= 0) {
                alert('No product selected !');
            } else if (order.get_client() == null) {
                alert('Please select customer !');
            } else {
                self.gui.show_popup('sale_order_popup', {
                    'sale_order_button': self
                });
            }
        },
    });

    //Edit Quotation button defination on screen.
    screens.define_action_button({
        'name': 'EditQuotationButton',
        'widget': EditQuotationButton,
    });

    //Inheritted payment screen for handling sale order validation.
    screens.PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            var order = self.pos.get_order();
            if (order) {
                var currentOrderLines = order.get_orderlines();
                //Bind click event of validate sale order.
                //On click open sale order popup and for payment.
                this.$('#btn_so').click(function() {
                    var paymentline_ids = [];
                    if (order.get_paymentlines().length > 0) {
                        if (currentOrderLines.length <= 0) {
                            alert('Empty order');
                        } else if (order.get_client() == null) {
                            alert('Please select customer !');
                        } else {
                            $('#btn_so').hide();
                            order.set_paying_sale_order(true);
                            if (!order.get_order_id() || order.get_edit_quotation()) {
                                self.gui.show_popup('sale_order_popup', {
                                    'payment_obj': self
                                });
                            } else {
                                self.pos.create_sale_order();
                            }
                        }
                    }
                });

            }
        },
        //Based on changes highlight sale order class.
        order_changes: function() {
            var self = this;
            var order = this.pos.get_order();
            var total = order ? order.get_total_with_tax() : 0;
            if (!order) {
                return;
            } else if (order.is_paid()) {
                self.$('.next').addClass('highlight');
            } else if (order.get_due() == 0 || order.get_due() == total) {
                self.$('#btn_so').removeClass('highlight');
            } else {
                self.$('.next').removeClass('highlight');
                self.$('#btn_so').addClass('highlight');
            }
        },
        click_set_customer: function() {
            var self = this;
            var order = this.pos.get_order();
            if (!order.get_sale_order_pay()) {
                self._super();
            }
        },
        click_back: function() {
            var self = this;
            var order = this.pos.get_order();
            if (order.get_sale_order_pay()) {
                this.gui.show_popup('confirm', {
                    title: _t('Discard Sale Order'),
                    body: _t('Do you want to discard the payment of sale order ' + order.get_sale_order_name() + ' ?'),
                    confirm: function() {
                        order.finalize();
                    },
                });
            } else {
                self._super();
            }
        }
    });


    /*--------------------------------------*\
    |         THE Sale Order LIST              |
   \*======================================*/

    // The sale order list displays the list of sale orders,
    // and allows the User to filter order based on payment status
    // Allow to accept, reject and review order.

    var SaleOrderListScreenWidget = screens.ScreenWidget.extend({
        filter: "all",
        date: "all",
        template: 'SaleOrderListScreenWidget',

        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
        },
        //Helper methods to show sale order screen.
        show: function() {
            var self = this;
            this._super();

            this.renderElement();
            this.details_visible = false;

            this.$('.back').click(function() {
                self.gui.back();
            });
            this.$('.reload').click(function() {
                self.reloading_orders();
            });

            self.reloading_orders();

            this.$('.sale-order-list-contents').delegate('.sale-line', 'click', function(event) {
                self.line_select(event, $(this), parseInt($(this).data('id')));
            });

            var search_timeout = null;

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress', function(event) {
                clearTimeout(search_timeout);

                var searchbox = this;

                search_timeout = setTimeout(function() {
                    self.perform_search(searchbox.value, event.which === 13);
                }, 70);
            });

            this.$('.searchbox .search-clear').click(function() {
                self.clear_search();
            });

            var orders = self.pos.get('pos_sale_order_list');
            $('input#datepicker').datepicker({
                dateFormat: 'yy-mm-dd',
                autoclose: true,
                closeText: 'Clear',
                showButtonPanel: true,
                onSelect: function(dateText, inst) {
                    var date = $(this).val();
                    if (date) {
                        self.date = date;
                        self.render_list(orders);
                    }
                },
                onClose: function(dateText, inst) {
                    if (!dateText) {
                        self.date = "all";
                        self.render_list(orders);
                    }
                }
            }).focus(function() {
                var thisCalendar = $(this);
                $('.ui-datepicker-close').click(function() {
                    thisCalendar.val('');
                    self.date = "all";
                    self.render_list(orders);
                });
            });

            //button draft
            this.$('.button.draft').click(function() {
                var orders = self.pos.get('pos_sale_order_list');
                if (self.$(this).hasClass('selected')) {
                    self.$(this).removeClass('selected');
                    $('.pay_button, .quotation_edit_button').show();
                    self.filter = "all";
                } else {
                    if (self.$('.button.paid').hasClass('selected')) {
                        self.$('.button.paid').removeClass('selected');
                    }
                    if (self.$('.button.confirm').hasClass('selected')) {
                        self.$('.button.confirm').removeClass('selected');
                    }
                    $('.pay_button, .quotation_edit_button').show();
                    self.$(this).addClass('selected');
                    self.filter = "draft";
                }
                self.render_list(orders);
            });

            this.$('.button.draft').click()
            //button paid
            this.$('.button.paid').click(function() {
                var orders = self.pos.get('pos_sale_order_list');
                if (self.$(this).hasClass('selected')) {
                    self.$(this).removeClass('selected');
                    $('.pay_button').show();
                    $('.quotation_edit_button').show();
                    self.filter = "all";
                } else {
                    if (self.$('.button.draft').hasClass('selected')) {
                        self.$('.button.draft').removeClass('selected');
                    }
                    if (self.$('.button.confirm').hasClass('selected')) {
                        self.$('.button.confirm').removeClass('selected');
                    }
                    self.$(this).addClass('selected');
                    $('.pay_button').hide();
                    $('.quotation_edit_button').hide();
                    self.filter = "done";
                }
                self.render_list(orders);
            });

            //button confirm
            this.$('.button.confirm').click(function() {
                var orders = self.pos.get('pos_sale_order_list');
                if (self.$(this).hasClass('selected')) {
                    self.$(this).removeClass('selected');
                    $('.pay_button, .quotation_edit_button').show();
                    self.filter = "all";
                } else {
                    if (self.$('.button.paid').hasClass('selected')) {
                        self.$('.button.paid').removeClass('selected');
                    }
                    if (self.$('.button.draft').hasClass('selected')) {
                        self.$('.button.draft').removeClass('selected');
                    }
                    $('.pay_button').show();
                    $('.quotation_edit_button').hide();
                    self.$(this).addClass('selected');
                    self.filter = "sale";
                }
                self.render_list(orders);
            });

            //Code Needs to be removed in future.
            this.$('.sale-order-list-contents').delegate('#pay_amount', 'click', function(event) {
                var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                if (result.state == "cancel") {
                    alert("Sorry, This order is cancelled");
                    return
                }
                if (result.state == "done") {
                    alert("Sorry, This Order is already locked");
                    return
                }

                var selectedOrder = self.pos.get_order();
                if (result && result.order_line.length > 0) {
                    var count = 0;
                    var currentOrderLines = selectedOrder.get_orderlines();
                    if (currentOrderLines.length > 0) {
                        selectedOrder.set_order_id('');
                        for (var i = 0; i <= currentOrderLines.length + 1; i++) {
                            _.each(currentOrderLines, function(item) {
                                selectedOrder.remove_orderline(item);
                            });
                        }
                    }
                    var partner = null;
                    if (result.partner_id && result.partner_id[0]) {
                        var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                    }
                    selectedOrder.set_client(partner);
                    selectedOrder.set_sale_order_name(result.name);
                    // Partial Payment
                    if (self.pos.config.paid_amount_product) {
                        var paid_amount = 0.00;
                        var first_invoice = false;
                        if (result.invoice_ids.length > 0) {
                            new Model('account.invoice').call('search_read', [
                                    [
                                        ['id', 'in', result.invoice_ids],
                                        ['state', 'not in', ['paid']]
                                    ]
                                ], {}, {
                                    async: false
                                })
                                .then(function(invoices) {
                                    if (invoices) {
                                        first_invoice = invoices[0];
                                        _.each(invoices, function(invoice) {
                                            paid_amount += invoice.amount_total - invoice.residual
                                        })
                                    }
                                });
                            if (paid_amount) {
                                var product = self.pos.db.get_product_by_id(self.pos.config.paid_amount_product[0]);
                                selectedOrder.add_product(product, {
                                    price: paid_amount,
                                    quantity: -1
                                });
                            }
                            if (first_invoice) {
                                selectedOrder.set_inv_id(first_invoice.id)
                            }
                        }
                    } else {
                        self.gui.show_popup('error-traceback', {
                            title: _t("Configuration Required"),
                            body: _t("Please configure dummy product for paid amount from POS configuration"),
                        });
                        return
                    }
                    // Partial Payment over
                    if (result.order_line) {
                        new Model('sale.order.line').call("search_read", [
                                [
                                    ['id', 'in', result.order_line]
                                ]
                            ], {}, {
                                async: false
                            })
                            .then(function(result_lines) {
                                _.each(result_lines, function(res) {
                                    count += 1;
                                    var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                                    if (product) {
                                        var line = new models.Orderline({}, {
                                            pos: self.pos,
                                            order: selectedOrder,
                                            product: product
                                        });
                                        line.set_quantity(res.product_uom_qty);
                                        line.set_unit_price(res.price_unit)
                                        selectedOrder.add_orderline(line);
                                        selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                                    }
                                });
                            });

                    }
                    selectedOrder.set_order_id(order_id);
                    selectedOrder.set_sequence(result.name);
                    selectedOrder.set_sale_order_pay(true);
                    self.gui.show_screen('payment');
                    self.pos.gui.screen_instances.payment.renderElement();
                    $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                }

            });

            /* Accept Order */
            this.$('.sale-order-list-contents').delegate('#order_accept', 'click', function(event) {
                var order_id = parseInt($(this).data('id'));
                var order = self.pos.db.get_sale_order_by_id(order_id);

                if(!order.partner_email){
                    self.gui.show_popup('error', {
                        'title': _t('Warning: Customer Email Not Found'),
                        'body': _t('Please add customer email.'),
                    });
                    return
                }
                var vals;
                new Model('sale.order').get_func('update_so')(vals = {
                    'order_id': order_id,
                    'is_accepted': true,
                    'pos_config_id': self.pos.config.id
                }).done(function(data) {
                    if(data && data.error){
                        self.gui.show_popup('error', {
                            'title': _t('Warning'),
                            'body': data.error,
                        });
                        return
                    }
                    if (data && !data.error) {
                        // Hide-Show buttons
                        var edit_quotation = document.querySelector('#edit_quotation[data-id="' + order_id + '"]')
                        $(edit_quotation).show();
                        if(order.state == 'sale'){
                            var print_quotation = document.querySelector('#print_quotation[data-id="' + order_id + '"]')
                            $(print_quotation).show();
                        }
                        order.is_accepted = data ? true : false;
                        var accept = document.querySelector('#order_accept[data-id="' + order_id + '"]');
                        var reject = document.querySelector('#order_reject[data-id="' + order_id + '"]');
                        $(accept).hide();
                        $(reject).hide();
                    }
                }).fail(function(err, eve){
                    eve.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (err.data) {
                        var except = err.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Warning: Could Accept Order.'),
                        'body': error_body,
                    });
                });
            });
            /* Reject Order */
            this.$('.sale-order-list-contents').delegate('#order_reject', 'click', function(event) {
                var order_id = parseInt($(this).data('id'));
                var order = self.pos.db.get_sale_order_by_id(order_id);
                if(!order.partner_email){
                    self.gui.show_popup('error', {
                        'title': _t('Warning: Customer Email Not Found'),
                        'body': _t('Please add customer email.'),
                    });
                    return
                }
                self.gui.show_popup('reject_so_popup', {
                    'order': order,
                    'sale_order_screen': self
                });
            });
            this.$('.sale-order-list-contents').delegate('#edit_quotation', 'click', function(event) {
                var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                if (result.state == "cancel") {
                    alert("Sorry, This order is cancelled");
                    return
                }
                if (result.state == "done") {
                    alert("Sorry, This Order is already locked");
                    return
                }
                if (result.state == "sale") {
                    alert("Sorry, This Order is confirmed");
                    return
                }
                var selectedOrder = self.pos.get_order();
                var partner = null;
                if (result.partner_id && result.partner_id[0]) {
                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                }
                selectedOrder.set_client(partner);
                selectedOrder.set_shipping_address(result.partner_shipping_id ? result.partner_shipping_id[0] : 0)
                selectedOrder.set_invoice_address(result.partner_invoice_id ? result.partner_invoice_id[0] : 0)
                selectedOrder.set_sale_order_name(result.name);
                selectedOrder.set_sale_order_date(result.date_order);
                if (result && result.order_line.length > 0) {
                    var count = 0;
                    var currentOrderLines = selectedOrder.get_orderlines();
                    if (currentOrderLines.length > 0) {
                        selectedOrder.set_order_id('');
                        for (var i = 0; i <= currentOrderLines.length + 1; i++) {
                            _.each(currentOrderLines, function(item) {
                                selectedOrder.remove_orderline(item);
                            });
                        }
                    }
                    new Model('sale.order.line').call("search_read", [
                            [
                                ['id', 'in', result.order_line]
                            ]
                        ], {}, {
                            async: false
                        })
                        .then(function(result_lines) {
                            _.each(result_lines, function(res) {
                                count += 1;
                                var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                                if (product) {
                                    var line = new models.Orderline({}, {
                                        pos: self.pos,
                                        order: selectedOrder,
                                        product: product
                                    });
                                    line.set_quantity(res.product_uom_qty);
                                    line.set_unit_price(res.price_unit);
                                    selectedOrder.add_orderline(line);
                                    selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                                }
                            });
                        });
                }
                selectedOrder.set_order_id(order_id);
                selectedOrder.set_sequence(result.name);
                self.pos.gui.screen_instances.payment.renderElement();
                $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                selectedOrder.set_edit_quotation(true);
                self.gui.show_screen('products');
            });
            this.$('.sale-order-list-contents').delegate('#print_quotation', 'click', function(event) {
                var order_id = parseInt($(this).data('id'));
                var result = self.pos.db.get_sale_order_by_id(order_id);
                var selectedOrder = self.pos.get_order();
                var partner = null;
                if (result.partner_id && result.partner_id[0]) {
                    var partner = self.pos.db.get_partner_by_id(result.partner_id[0])
                }
                selectedOrder.set_client(partner);
                selectedOrder.set_shipping_address(result.partner_shipping_id ? result.partner_shipping_id[0] : 0)
                selectedOrder.set_shipping_address_text(result.partner_shipping_id ? result.partner_shipping_id[1] : False)
                selectedOrder.set_invoice_address(result.partner_invoice_id ? result.partner_invoice_id[0] : 0)
                selectedOrder.set_sale_order_name(result.name);
                selectedOrder.set_sale_order_date(result.date_order);
                if (result && result.order_line.length > 0) {
                    var count = 0;
                    var currentOrderLines = selectedOrder.get_orderlines();
                    if (currentOrderLines.length > 0) {
                        selectedOrder.set_order_id('');
                        for (var i = 0; i <= currentOrderLines.length + 1; i++) {
                            _.each(currentOrderLines, function(item) {
                                selectedOrder.remove_orderline(item);
                            });
                        }
                    }
                    new Model('sale.order.line').call("search_read", [
                            [
                                ['id', 'in', result.order_line]
                            ]
                        ], {}, {
                            async: false
                        })
                        .then(function(result_lines) {
                            _.each(result_lines, function(res) {
                                count += 1;
                                var product = self.pos.db.get_product_by_id(Number(res.product_id[0]));
                                if (product) {
                                    var line = new models.Orderline({}, {
                                        pos: self.pos,
                                        order: selectedOrder,
                                        product: product
                                    });
                                    line.set_quantity(res.product_uom_qty);
                                    line.set_unit_price(res.price_unit);
                                    selectedOrder.add_orderline(line);
                                    selectedOrder.select_orderline(selectedOrder.get_last_orderline());
                                }
                            });
                        });
                }
                selectedOrder.set_order_id(order_id);
                selectedOrder.set_sequence(result.name);
                self.pos.gui.screen_instances.payment.renderElement();
                $(self.pos.gui.screen_instances.payment.el).find('.button.next, .button.js_invoice').hide();
                self.gui.show_screen('receipt');
            });
        },
        //Used to search the record based on query and display result in screen.
        perform_search: function(query, associate_result) {
            var self = this;
            if (query) {
                var orders = this.pos.db.search_order(query);
                if (associate_result && orders.length === 1) {
                    this.gui.back();
                }
                this.render_list(orders);
            } else {
                var orders = self.pos.get('pos_sale_order_list');
                this.render_list(orders);
            }
        },
        //Used to highlight the selected sale order line and display/hide sale order related information in top bar
        line_select: function(event, $line, id) {
            var order = this.pos.db.get_sale_order_by_id(id);
            this.$('.sale-order-list .lowlight').removeClass('lowlight');
            if ($line.hasClass('highlight')) {
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.display_order_details('hide', order);
            } else {
                this.$('.sale-order-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.display_order_details('show', order, y);
            }
        },
        //Helper method used to show/hide sale order information.
        display_order_details: function(visibility, order, clickpos) {
            var self = this;
            var searchbox = this.$('.searchbox input');
            var contents = this.$('.so-details-contents');
            var parent = this.$('.sale-order-list').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();

            if (visibility === 'show') {
                contents.empty();
                var order_lines = []
                if (order.order_line.length > 0) {
                    new Model('sale.order.line').call("search_read", [
                        [
                            ['id', 'in', order.order_line]
                        ]
                    ], {}, {
                        async: false
                    }).done(function(lines) {
                        order_lines = lines
                        contents.append($(QWeb.render('SaleOrderDetails', {
                            widget: self,
                            order: order,
                            order_lines: order_lines
                        })));

                        var new_height = contents.height();

                        if (!self.details_visible) {
                            // resize client list to take into account client details
                            parent.height('-=' + new_height);

                            if (clickpos < scroll + new_height + 20) {
                                parent.scrollTop(clickpos - 20);
                            } else {
                                parent.scrollTop(parent.scrollTop() + new_height);
                            }
                        } else {
                            parent.scrollTop(parent.scrollTop() - height + new_height);
                        }

                        self.details_visible = true;
                    })
                }

            } else if (visibility === 'hide') {
                contents.empty();
                parent.height('100%');
                if (height > scroll) {
                    contents.css({
                        height: height + 'px'
                    });
                    contents.animate({
                        height: 0
                    }, 400, function() {
                        contents.css({
                            height: ''
                        });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
            }
        },
        //Clears the search input.
        clear_search: function() {
            var orders = this.pos.get('pos_sale_order_list');
            this.render_list(orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        //Helper method used to render the list of orders.
        render_list: function(orders) {
            var self = this;
            self.display_order_details('hide')
            var contents = this.$el[0].querySelector('.sale-order-list-contents');
            contents.innerHTML = "";
            var temp = [];
            if (self.filter !== "" && self.filter !== "all") {
                orders = $.grep(orders, function(order) {
                    //return order.state === self.filter;
                    return self.filter === 'draft' ? order.payment_status == 'unpaid' : order.payment_status == 'paid';
                });
            }
            if (self.date !== "" && self.date !== "all") {
                var x = [];
                for (var i = 0; i < orders.length; i++) {
                    var date_order = $.datepicker.formatDate("yy-mm-dd", new Date(orders[i].date_order));
                    if (self.date === date_order) {
                        x.push(orders[i]);
                    }
                }
                orders = x;
            }
            for (var i = 0, len = Math.min(orders.length, 1000); i < len; i++) {
                var order = orders[i];
                order.amount_total = parseFloat(order.amount_total).toFixed(2);
                if (order.partner_id && order.partner_id.length >= 2) {
                    order.partner_id[1] = order.partner_id[1].split(' ')[0]
                }
                var partner = this.pos.db.partner_by_id[order.partner_id[0]];
                if(partner){
                    if (order.partner_shipping_id && order.partner_shipping_id.length >= 2) {
                        var address = partner.address;
                        address = order.partner_shipping_id[1].replace(partner.name, '');
                        address = address.replace(/[^a-zA-Z0-9 ]/, '');
                    }
                    if (order.date_order) {
                        var display_order_date = '';
                        try {
                            display_order_date = formats.format_value(order.date_order, {
                                "widget": 'datetime'
                            });
                        } catch (e) {
                            display_order_date = order.date_order
                        }
                    }
                    var clientline_html = QWeb.render('SaleOrderlistLine', {
                        display_order_date: display_order_date,
                        widget: this,
                        order: order,
                        partner_shipping_address: address,
                        partner: partner
                    });
                    var clientline = document.createElement('tbody');
                    clientline.innerHTML = clientline_html;
                    clientline = clientline.childNodes[1];
                    contents.appendChild(clientline);
                }
            }
            self.$el.find('.sale-order-list').simplePagination({
                previousButtonClass: "btn btn-danger",
                nextButtonClass: "btn btn-danger",
                previousButtonText: '<i class="fa fa-angle-left fa-lg"></i>',
                nextButtonText: '<i class="fa fa-angle-right fa-lg"></i>',
                perPage: self.pos.config.sale_order_record_per_page > 0 ? self.pos.config.sale_order_record_per_page : 10
            })
        },
        //Helper methods to reload the list on screen.
        reload_orders: function() {
            var self = this;
            var orders = self.pos.get('pos_sale_order_list');
            this.render_list(orders);
        },
        //Helper methods used to fetch the sale order from server and update the sale order list screen.
        reloading_orders: function() {
            var self = this;
            var domain, fields, offset, limit, order, context;
            return self.pos.load_new_partners().then(function(){
                return new Model('sale.order').get_func('search_read')(self.pos.domain_sale_order, fields = [], offset = 0, limit = 0, order = 'id desc', context = {
                        'show_address': true
                })
                .then(function(result) {
                    self.pos.db.add_sale_orders(result);
                    self.pos.set({
                        'pos_sale_order_list': result
                    });
                    self.reload_orders();
                    return self.pos.get('pos_sale_order_list');
                }).fail(function(error, event) {
                    if (error.code === 200) { // Business Logic Error, not a connection problem
                        self.gui.show_popup('error-traceback', {
                            message: error.data.message,
                            comment: error.data.debug
                        });
                    }
                    // prevent an error popup creation by the rpc failure
                    // we want the failure to be silent as we send the orders in the background
                    event.preventDefault();
                    console.error('Failed to fetch sale orders.');
                    var orders = self.pos.get('pos_sale_order_list');
                    self.reload_orders();
                    return orders
                });
            });
        },
        renderElement: function() {
            var self = this;
            var pending_orders_count = 0;
            _.each(self.pos.get('pos_sale_order_list'), function(order){
                if(order.delivery_status == 'pending'){
                    pending_orders_count += 1;
                }
            })
            var order_count_value = document.getElementById('order_count');
            if(order_count_value){
                order_count_value.innerHTML = pending_orders_count;
            }
            self._super();
        },
    });
    //Define sale order list screen in gui class.
    gui.define_screen({
        name: 'saleorderlist',
        widget: SaleOrderListScreenWidget
    });

    //Overridden Product screen widget to add support for price list and button visibility.
    screens.ProductScreenWidget.include({
        //As of now this code is not used. Needs to remove in future.
        start: function() {
            var self = this;
            this._super();
            var pricelist_list = this.pos.prod_pricelists;
            var new_options = [];
            new_options.push('<option value="">Select Pricelist</option>\n');
            if (pricelist_list.length > 0) {
                for (var i = 0, len = pricelist_list.length; i < len; i++) {
                    new_options.push('<option value="' + pricelist_list[i].id + '">' + pricelist_list[i].display_name + '</option>\n');
                }
                $('#price_list').html(new_options);
                var order = self.pos.get_order();
                if (order && order.get_client() && order.get_client().property_product_pricelist && order.get_client().property_product_pricelist[0]) {
                    $('#price_list').val(order.get_client().property_product_pricelist[0]);
                }
                $('#price_list').selectedIndex = 0;
            }
            $('#price_list').on('change', function() {
                var order = self.pos.get_order();
                var partner_id = self.pos.get_order().get_client() && parseInt(self.pos.get_order().get_client().id);
                if (!partner_id && $(this).val()) {
                    $('#price_list').html(new_options);
                    alert('Pricelist will not work as customer is not selected !');
                    return;
                } else {
                    var products = self.pos.db.get_all_product();
                    if (products) {
                        if ($(this).val()) {
                            order.manual_set_pricelist_val($(this).val());
                            var new_products = [];
                            var product_ids = products.map(function(o) {
                                return o.id;
                            })
                            if (product_ids.length > 0) {

                                new Model("product.product").call('get_product_price', [parseInt($(this).val()), product_ids], {}, {
                                        async: false
                                    })
                                    .then(function(result) {
                                        if (result) {
                                            // Products
                                            var orderlines = order.get_orderlines() || false;
                                            _.each(result, function(res) {
                                                var product = self.pos.db.get_product_by_id(res.product_id);
                                                if (product) {
                                                    if (orderlines) {
                                                        _.each(orderlines, function(orderline) {
                                                            if (orderline.get_product().id === product.id) {
                                                                orderline.set_unit_price(res.new_price);
                                                            }
                                                        });
                                                    }
                                                }
                                            })
                                        }
                                    });
                            }
                        } else {
                            var orderlines = order.get_orderlines() || false;
                            if (orderlines) {
                                _.each(orderlines, function(orderline) {
                                    orderline.set_unit_price(orderline.get_product().price);
                                });
                            }
                        }
                    }
                }
            });
        },
        //Toggle sale order buttons based on sale order quotation mode.
        show: function(reset) {
            var self = this;
            self._super(reset);
            var order = self.pos.get_order();
            if (order.get_edit_quotation()) {
                $('.js_edit_quotation').show()
                $('.js_saleorder').hide()
            } else {
                $('.js_saleorder').show()
            }
        },
    });

    //Overridden Order widget to add support for price list.
    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            if (order && order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if (mode === 'quantity') {
                    order.get_selected_orderline().set_quantity(val);
                    var partner = order.get_client();
                    var pricelist_id = parseInt($('#price_list').val()) || order.get_pricelist();
                    if (pricelist_id && order.get_selected_orderline() && (val != 'remove')) {
                        var qty = order.get_selected_orderline().get_quantity();
                        var p_id = order.get_selected_orderline().get_product().id;
                        if (!val) {
                            val = 1;
                        }
                        new Model("product.pricelist").get_func('price_get')([pricelist_id], p_id, qty).pipe(
                            function(res) {
                                if (res[pricelist_id]) {
                                    var pricelist_value = parseFloat(res[pricelist_id].toFixed(2));
                                    if (pricelist_value) {
                                        order.get_selected_orderline().set_unit_price(pricelist_value);
                                        order.get_selected_orderline().set_is_pricelist_apply(true);
                                    }
                                }
                            });
                    }
                } else if (mode === 'discount') {
                    order.get_selected_orderline().set_discount(val);
                } else if (mode === 'price') {
                    order.get_selected_orderline().set_unit_price(val);
                    order.get_selected_orderline().set_manual_price(true);
                }
            }
        },
    });

    //Overridden Client Screen to add support for price list.
    screens.ClientListScreenWidget.include({
        display_client_details: function(visibility, partner, clickpos) {
            var self = this;
            self._super(visibility, partner, clickpos);
            if (partner && partner.property_product_pricelist) {
                $('#readonly_pricelist').text(partner.property_product_pricelist[1]);
            }
        },
    });

});
