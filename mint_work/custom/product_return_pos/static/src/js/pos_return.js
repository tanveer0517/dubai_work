odoo.define('product_return_pos',function(require){
"use strict";

    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var models = require('point_of_sale.models');
    var pos_screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var Model = require('web.DataModel');
    var QWeb = core.qweb;
    var _t = core._t;

    var packlot_line = _.findWhere(gui.Gui.prototype.popup_classes, {name: "packlotline"});

    //Load POS order information for return order management.
    models.load_models({
        model: 'pos.order',
        fields: ['id', 'name', 'session_id', 'pos_reference', 'partner_id', 'amount_total','lines', 'amount_tax','return_ref', 'date_order', 'return_status'],
        loaded: function (self, pos_orders) {
            self.pos_orders = pos_orders;
            self.db.add_pos_orders(pos_orders);
        },
    });

    models.PosModel = models.PosModel.extend({
        // reload the list of pos order, returns as a deferred that resolves if there were
        // updated pos orders, and fails if not
        load_new_pos_orders: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.models,function(model){ return model.model === 'pos.order'; }).fields;
            new Model('pos.order')
                .query(fields)
                .filter([['write_date','>',this.db.get_pos_order_write_date()]])
                .all({'timeout':3000, 'shadow': true})
                .then(function(pos_orders){
                    if (self.db.add_pos_orders(pos_orders)) {   // check if the pos orders we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(err,event){ event.preventDefault(); def.reject(); });
            return def;
        },
    });

    // Display Return Order button above numpad.
    var ReturnButton = pos_screens.ActionButtonWidget.extend({
        template: 'ReturnButton',
        button_click: function(){
            if (!this.pos.get_order().return_ref && this.pos.get_order().get_orderlines().length === 0){
                this.gui.show_screen('ReturnOrdersWidget');
            }
            else if(!this.pos.get_order().return_ref && this.pos.get_order().get_orderlines().length) {
                this.gui.show_popup('error',{
                    title :_t('Warning'),
                    body  :_t('Please complete or clear the current order to create a return order.'),
                });
            }else if(this.pos.get_order().return_ref){
                this.gui.show_popup('error',{
                    title :_t('Warning: Return Order'),
                    body  :_t('You can process only one return at a time.'),
                });
            }
        },
    });

    //Define Return Order button.
    pos_screens.define_action_button({
        'name': 'Return',
        'widget': ReturnButton,
        'condition': function(){
            return this.pos;
        },
    });

    /*--------------------------------------*\
    |         THE POS Order LIST              |
   \*======================================*/

   // The posorderlist displays the list of pos orders,
   // and allows the user to return the order.

    var ReturnOrdersWidget = pos_screens.ScreenWidget.extend({
        template: 'ReturnOrdersWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.pos_order_cache = new pos_screens.DomCache();
        },

        auto_back: true,

        //Helper  method used to handle return order.
        show: function(){
            var self = this;
            this._super();

            this.renderElement();
            this.details_visible = false;

            this.$('.back').click(function(){
                self.gui.back();
            });

            var pos_orders = this.pos.db.get_pos_order_sorted(1000);
            this.render_list(pos_orders);

            this.reload_pos_orders();

            this.$('.order-list-lines').delegate('.return-button','click',function(event){
                self.return_order(event,$(this),parseInt($(this).closest('tr').data('id')));
            });
            var search_timeout = null;

            if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress',function(event){
                clearTimeout(search_timeout);

                var searchbox = this;

                search_timeout = setTimeout(function(){
                    self.perform_search(searchbox.value, event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
        },

        // This method fetches order changes on the server, and in case of changes,
        // rerenders the affected views
        reload_pos_orders: function(){
            var self = this;
            return this.pos.load_new_pos_orders().then(function(){
                self.render_list(self.pos.db.get_pos_order_sorted(1000));
            });
        },

        //Search Order from the cache and display result according to query.
        perform_search: function(query, associate_result){
            var pos_orders;
            if(query){
                pos_orders = this.pos.db.search_pos_orders(query);
                this.render_list(pos_orders);
            }else{
                pos_orders = this.pos.db.get_pos_order_sorted();
                this.render_list(pos_orders);
            }
        },

        //Clear the search box and render the order list.
        clear_search: function(){
            var pos_orders = this.pos.db.get_pos_order_sorted(1000);
            this.render_list(pos_orders);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },

        //Used to render the list of orders.
        render_list: function(pos_orders){

            var contents = this.$el[0].querySelector('.order-list-lines');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(pos_orders.length,1000); i < len; i++) {
                if (pos_orders[i]) {
                    var posorder = pos_orders[i];
                    var orderline = this.pos_order_cache.get_node(posorder.id);
                    var clientline_html = QWeb.render('OrderLines', {widget: this, order: posorder});
                    var orderline = document.createElement('tbody');
                    orderline.innerHTML = clientline_html;
                    orderline = orderline.childNodes[1];
                    this.pos_order_cache.cache_node(posorder.id,orderline);
                    contents.appendChild(orderline);
                }
            }
        },

        //Open return order dialog and check for the restrict return
        //Restrict Return is days defined in pos config to allow return to be processed
        //withing defined days.
        return_order: function(event,$line,id){
            var self = this;
            var pos_order = self.pos.db.get_pos_order_by_id(id);
            if(self.pos.config.restrict_return){
                var date = new Date();
                var date_order = new Date(pos_order.date_order.slice(0, 10))
                if (self.pos.config.return_accepted_in_days) {
                    date.setDate(date.getDate() - self.pos.config.return_accepted_in_days);
                }
                var return_accepted_date = new Date(date.toJSON().slice(0, 10))
                if(date_order <= return_accepted_date){
                    self.gui.show_popup('error',{
                        title :_t('Return Order Warning'),
                        body  :_t('You can only return order within ')+ self.pos.config.return_accepted_in_days +' days !',
                    });
                    return;
                }
            }
            if (pos_order.return_ref){
                  self.gui.show_popup('error',_t('This is a returned order'));
                  self.gui.show_popup('error',{
                    title :_t('Return Order Warning!'),
                    body  :_t('Already a return order, Can not process a return order Again!'),
                });
            }else{
                new Model('pos.order').call('get_status',[pos_order.pos_reference]).done(function(result){
                    if (result){
                        self.gui.show_popup('OrderReturnWidget',{
                            'pos_order': pos_order,
                        });
                    }else{
                        self.gui.show_popup('error',{
                            title :_t('Fully Returned Order'),
                            body  :_t('This order is fully returned'),
                        });
                    }
                }).fail(function(err, eve){
                    eve.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (err.data) {
                        var except = err.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Warning: Could not process return order'),
                        'body': error_body,
                    });
                });
            }
        }
    });

    //Fetch orderlines to be returned and display orderlines in popup.
    var OrderReturnWidget = PopupWidget.extend({
        template: 'OrderReturnWidget',

        show: function(options){
            var self = this;
            this._super(options);
            var options = options || {};
            this.pos_order = options.pos_order || false
            self.renderElement();
            $("#table-body tr").empty();
            var lines = [];
            if(!self.pos_order){
                return
            }
            new Model('pos.order').call('get_lines',[self.pos_order.pos_reference]).done(function(result){
                lines = result[0];
                this.client = result[1];
                for(var j=0;j < lines.length; j++){
                    var product_line = lines[j];
                    var rows = "";
                    var id = product_line.product_id
                    var price_unit = product_line.price_unit;
                    var name =product_line.product;
                    var qty = product_line.qty;
                    var line_id = product_line.line_id;
                    var discount = product_line.discount;
                    rows += "<tr><td>" + id + "</td><td>" + price_unit +" </td><td>" + name + "</td><td>" + qty + "</td><td>" + discount + "</td><td>" + line_id + "</td></tr>";
                    $(rows).appendTo("#list tbody");
                    var rows = document.getElementById('list').rows;
                    for (var row = 0; row < rows.length; row++) {
                        var cols = rows[row].cells;
                        cols[0].style.display = 'none';
                        cols[1].style.display = 'none';
                        cols[5].style.display = 'none';
                    }
                }

                var table = document.getElementById('list');
                var tr = table.getElementsByTagName("tr");
                for (var i = 1; i < tr.length; i++) {
                    var td = document.createElement('td');
                    var input = document.createElement('input');
                    input.setAttribute("type", "text");
                    input.setAttribute("value", 0);
                    input.setAttribute("id", "text"+i);
                    td.appendChild(input);
                    tr[i].appendChild(td);
                }
            }).fail(function(err, eve){
                eve.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (err.data) {
                    var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Warning: Could not fetch order information.'),
                    'body': error_body,
                });
            });;
        },

        //Validate the order qty and return qty and display the return order in screen.
        click_confirm: function(){
            var self = this;
            var myTable = document.getElementById('list').tBodies[0];
            var count  = 0
            var c = 1
            for (var r=0, n = myTable.rows.length; r < n; r++) {
                var row = myTable.rows[r]
                var return_qty = document.getElementById("text"+c).value
                if (Number(row.cells[3].innerHTML) < Number(return_qty)){
                    count +=1
                }
                c = c+1
            }
            if (count > 0){
                alert(_t('Can not proceed. Returned qty is is higher than purchased qty.'))
                return;
            }else {
                var c = 1
                for (var r=0, n = myTable.rows.length; r < n; r++) {
                    row = myTable.rows[r]
                    var return_qty = document.getElementById("text"+c).value
                    var product   = this.pos.db.get_product_by_id(row.cells[0].innerHTML);
                    if (!product) {
                        return;
                    }
                    if(return_qty > 0) {
                        this.pos.get_order().add_product(product, {
                            price: row.cells[1].innerHTML,
                            quantity: -(return_qty),
                            discount:row.cells[4].innerHTML,
                            merge: false,
                            extras: {pos_ref: self.pos_order.pos_reference,
                                label:row.cells[5].innerHTML},
                        });
                    }
                    c = c+1
                }
            }
            self.gui.close_popup();
            self.gui.show_screen('products');
        },
        click_cancel: function(){
            this.gui.close_popup();
        },
    });

    gui.define_screen({name:'ReturnOrdersWidget', widget: ReturnOrdersWidget});
    gui.define_popup({name:'OrderReturnWidget', widget: OrderReturnWidget});

    //Initialized parameters and helper methods in order to process the return order.
    var OrderSuper = models.Order;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var order = OrderSuper.prototype.initialize.call(this, attributes,options);
            var self = this;
            self.return_ref = '';
            this.orderlines.on('remove',   function(){
                if (this.return_ref && this.get_orderlines().length === 0){
                    this.return_ref = ''
                }
                this.save_to_db("orderline:remove");
            }, this);
            return order;
        },
        init_from_JSON: function(json) {
            OrderSuper.prototype.init_from_JSON.call(this, json);
            this.return_ref = json.return_ref;
        },
        export_as_JSON: function() {
            var json_new = OrderSuper.prototype.export_as_JSON.call(this);
            json_new.return_ref = this.get_return_ref();
            return json_new;
        },
        get_return_ref: function(){
            return this.return_ref;
        },
        add_product: function (product, options) {
            OrderSuper.prototype.add_product.call(this, product, options);
            var order    = this.pos.get_order();
            var last_orderline = this.get_last_orderline();
            if (options !== undefined){
                if(options.extras !== undefined){
                    for (var prop in options.extras) {
                        if (prop ==='pos_ref'){
                            this.return_ref = options.extras['pos_ref']
                            this.trigger('change',this);
                            var self = this;
                            var curr_client = order.get_client();
                            if (!curr_client) {
                                new Model('pos.order').call('get_client',[options.extras['pos_ref']]).then(function(result){
                                    if (result){
                                        var partner = self.pos.db.get_partner_by_id(result);
                                        order.set_client(partner);
                                    }
                                });
                            }
                        }else if(prop ==='label'){
                            order.selected_orderline.set_order_line_id(options.extras['label']);
                        }
                    }
                }
            }
        },
    });

  //Initialized parameters and helper methods in orderline to process the return order.
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr,options){
            OrderlineSuper.prototype.initialize.call(this, attr,options);
            this.line_id = '';
        },
        init_from_JSON: function(json) {
            OrderlineSuper.prototype.init_from_JSON.call(this, json);
            this.line_id  = json.line_id
        },
        clone: function(){
            var orderline = OrderlineSuper.prototype.clone.call(this);
            orderline.line_id = this.line_id;
            return orderline;
        },
        get_line_id: function(){
            return this.line_id;
        },
        set_order_line_id:function(id){
            this.line_id = id;
            this.trigger('change',this);
        },
        export_as_JSON: function(){
            var json = OrderlineSuper.prototype.export_as_JSON.apply(this,arguments);
            if (this.order.return_ref){
                json.line_id = this.get_line_id();
            }
            return json;
        },
        compute_lot_lines: function(){
            if(this.order.return_ref){
                var pack_lot_lines = this.pack_lot_lines;
                var lines = pack_lot_lines.length;
                var qty = Math.abs(this.quantity);
                if(qty > lines){
                    for(var i=0; i<qty - lines; i++){
                        pack_lot_lines.add(new models.Packlotline({}, {'order_line': this}));
                    }
                }
                if(qty < lines){
                    var to_remove = lines - qty;
                    var lot_lines = pack_lot_lines.sortBy('lot_name').slice(0, to_remove);
                    pack_lot_lines.remove(lot_lines);
                }
                return this.pack_lot_lines;
            }else{
                return OrderlineSuper.prototype.compute_lot_lines.apply(this,arguments);
            }
        },
        has_valid_product_lot: function(){
            if(!this.order.return_ref){
                return OrderlineSuper.prototype.has_valid_product_lot.apply(this,arguments);
            }
            if(!this.has_product_lot){
                return true;
            }
            var valid_product_lot = this.pack_lot_lines.get_valid_lots();
            return this.quantity === (-valid_product_lot.length);
        },
    });

    //Allow user to add serial number in return mode.
    packlot_line.widget.include({
        renderElement: function(){
            this._super();
            if (this.options && this.options.order && this.options.order.return_ref){
                this.$el.find(".remove-lot").hide()
            }
        },
        click_confirm: function(){
            if (!this.options.order.return_ref){
                return this._super()
            }
            var pack_lot_lines = this.options.pack_lot_lines;
            var is_empty = false;
            this.$('.packlot-line-input').each(function(index, el){
                var cid = $(el).attr('cid'),
                lot_name = $(el).val();
                if(!lot_name){
                    alert(_t("Lot/Serial Can not be empty."))
                    is_empty = true;
                    return false;
                }
                if(!is_empty){  
                    var pack_line = pack_lot_lines.get({cid: cid});
                    pack_line.set_lot_name(lot_name);
                }
            });
            if(!is_empty){
                var valid_lots = pack_lot_lines.get_valid_lots();
                pack_lot_lines.order_line.set_quantity(-valid_lots.length);
                this.options.order.save_to_db();
                this.gui.close_popup();
            }
        },
        add_lot: function(ev) {
            if (!this.options.order.return_ref){
                return this._super(this, arguments)
            }
        },
    })

    //Restrict User to add product when order is in return mode.
    pos_screens.ProductScreenWidget.include({
        click_product: function(product) {
            if(!this.pos.get_order().return_ref){
                return this._super(product)
            }
            var self = this;
            self.gui.show_popup('error',{
                title :_t('Warning: Return Order'),
                body  :_t('You can not add product on return order.'),
            });
         },
    })
});
