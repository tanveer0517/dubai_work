odoo.define('mint_pos.popups', function (require) {
"use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var Model = require('web.DataModel');
    var _t = core._t;

    //Template used to show Sale order confirmation with SO Reference.
    var SaleOrderConfirmPopupWidget = PopupWidget.extend({
        template: 'SaleOrderConfirmPopupWidget',
    });
    gui.define_popup({name:'saleOrder', widget: SaleOrderConfirmPopupWidget});

    //Display Sale Order popup.
    //Allows to update shipping address or invoice address.
    //Allows to update the date and note related to sale order.
    var SaleOrderPopup = PopupWidget.extend({
        template: 'SaleOrderPopup',
        show: function(options){
            var self = this;
            this._super(options);
            var order = self.pos.get_order();
            var options = options || {};
            this.sale_order_button = options.sale_order_button ||
            self.pos.gui.screen_instances.products.action_buttons.EditQuotationButton || false
            self.payment_obj = options.payment_obj || false;
            if (self.payment_obj){
                window.document.body.removeEventListener('keypress',self.payment_obj.keyboard_handler);
                window.document.body.removeEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
            }
            if (order.get_client()){
                //Fetch the contacts related to customer selected for the sale order.
                new Model('res.partner').call('search_read', [[['parent_id', '=', order.get_client().id]]], {}, {'async': false})
                .then(function(contacts){
                    self.contacts = contacts;
                });
            }
            self.renderElement();
            //By default set the sale order date, shipping contact and invoice contact.
            if(order.get_edit_quotation()){
                if(order.get_sale_order_date()){
                    var date_order = moment(order.get_sale_order_date(), 'YYYY-MM-DD');
                    $('#orderdate-datepicker').val(date_order.format('YYYY-MM-DD'));
                }
                var shipping_contact = _.find(self.contacts, function(o){
                    return o.id == order.get_shipping_address();
                })
                $('.shipping_contact_selection').val(shipping_contact ? shipping_contact.id : 0);
                var invoice_contact = _.find(self.contacts, function(o){
                    return o.id == order.get_invoice_address();
                })
                $('.invoicing_contact_selection').val(invoice_contact ? invoice_contact.id : 0);
            }
        },

        //Validate Name: check if name exist.
        validate_name: function($contact){
            var name = $contact.find('.client_name');
            if(!name.val()){
                $(name).attr('style', 'border: thin solid red !important');
                return false;
            }
            return true;
        },
        //Used to process order for sale order updation.
        process_order: function(order){
            var self = this;
            if(self.payment_obj){
                order.set_paying_sale_order(true);
                window.document.body.addEventListener('keypress',self.payment_obj.keyboard_handler);
                window.document.body.addEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
            }
            self.gui.close_popup();
            self.pos.create_sale_order();
        },
        //Prepare values for contact creation.
        prepare_vals: function($contact, order, options){
            var self = this;
            var res = {
                'name': $contact.find('.client_name').val(),
                'email': $contact.find('.client_email').val(),
                'city': $contact.find('.client_city').val(),
                'zip': $contact.find('.client_zip').val(),
                'mobile': $contact.find('.client_mobile').val(),
                'phone': $contact.find('.client_phone').val(),
                'parent_id': order.get_client().id,
                'state_id':  false,
                'country_id':  false,
                'type': '',
            }
            return _.extend(res, options);
        },
        //Used to set/create the shipping/invoice address and calls the create sales order to update the sale order.
        click_confirm: function(){
            var self = this;
            var order = self.pos.get_order();

            if($('.sale_order_note').val()){
                order.set_sale_note($.trim($('.sale_order_note').val()));
            }
            order.set_sale_order_date($('#orderdate-datepicker').val() || false);

            var create_shipping_contact = false;
            var create_invoice_contact = false;

            var $is_ship_diff_address = $('.ship_diff_address').prop('checked')
            var $invoice_diff_address = $('.invoice_diff_address').prop('checked')

            var $ship_contact = $('.ship_create_contact')
            var $invoice_contact = $('.invoice_create_contact')

            var selected_shipping_contact = $('.shipping_contact_selection option:selected').val();
            var selected_invoice_contact = $('.invoicing_contact_selection option:selected').val();

            if(selected_shipping_contact > 0 && !$is_ship_diff_address){
                order.set_shipping_address(selected_shipping_contact);
            }

            if(selected_invoice_contact > 0 && !$invoice_diff_address){
                order.set_invoice_address(selected_invoice_contact);
            }

            //Do not allow to process sale order if name is blank in case of
            //shipping address or invoice address is different.
            if($is_ship_diff_address){
                if(!self.validate_name($ship_contact)){
                    return false;
                }
                create_shipping_contact = true;
            }

            if($invoice_diff_address){
                if(!self.validate_name($invoice_contact)){
                    return false;
                }
                create_invoice_contact = true;
            }

            if(!create_shipping_contact && !create_invoice_contact){
                self.process_order(order);
            }else{
                if(create_shipping_contact){
                    var shipping_options = {
                            'state_id':  self.shipping_state || false,
                            'country_id':  self.shipping_country || false,
                            'type': 'delivery',
                    }
                    var ship_contact_vals = self.prepare_vals($ship_contact, order, shipping_options)
                }
                if(create_invoice_contact){
                    var invoice_options = {
                            'state_id':  self.invoice_state || false,
                            'country_id':  self.invoice_country || false,
                            'type': 'invoice',
                    }
                    var invoice_contact_vals = self.prepare_vals($invoice_contact, order, invoice_options)
                }

                //Prepare a dictionary to be sent to server for shipping/invoice contact creation.
                var res_dict = {
                    'create_shipping_contact' : create_shipping_contact,
                    'create_invoice_contact' : create_invoice_contact,
                    'ship_contact_vals' : ship_contact_vals,
                    'invoice_contact_vals' : invoice_contact_vals,
                }
                //Create a shipping contact or invoice contact.
                //Returns the shipping or invoice contact id and set it on order.
                new Model('res.partner').call('create_contact_from_ui',[res_dict]).then(function(result){
                    if(result.ship_contact_id){
                        order.set_shipping_address(result.ship_contact_id);
                    }
                    if(result.invoice_contact_id){
                        order.set_invoice_address(result.invoice_contact_id);
                    }
                    self.process_order(order);
                },function(err,event){
                    event.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (err.data) {
                        var except = err.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Error: Could not Save Changes'),
                        'body': error_body,
                    });
                    $('#btn_so').show();
                });
            }
        },
        //Close the sale order popup.
        click_cancel: function(){
            var self = this;
            if(self.payment_obj){
                window.document.body.addEventListener('keypress',self.payment_obj.keyboard_handler);
                window.document.body.addEventListener('keydown',self.payment_obj.keyboard_keydown_handler);
                $('#btn_so').show();
            }
            this.gui.close_popup();
        },
        renderElement: function(){
            var self = this;
            this._super();

            //initialize a date picker.
            var $date_picker = $('#orderdate-datepicker');
            $date_picker.datepicker({
                dateFormat:'yy-mm-dd',
                setDate: 0,
                minDate: 0,
                closeText: 'Clear',
                showButtonPanel: true,
            }).focus(function(){
                var thisCalendar = $(this);
                $('.ui-datepicker-close').click(function() {
                    thisCalendar.val('');
                });
            });
            $.datepicker._gotoToday = function(id) {
                var target = $(id);
                var inst = this._getInst(target[0]);

                var date = new Date();
                this._setDate(inst,date);
                this._hideDatepicker();
            }
            $date_picker.datepicker("setDate", new Date());

            //Toggle tabs visibility.
            $(".tabs-menu a").click(function(event) {
                event.preventDefault();
                $(this).parent().addClass("current");
                $(this).parent().siblings().removeClass("current");
                var tab = $(this).attr("href");
                $(".tab-content").not(tab).css("display", "none");
                $(tab).fadeIn();
            });

            //Toggle form of invoice address creation.
            $('.invoice_diff_address').click(function(){
                if($(this).prop('checked')){
                    $('.invoicing_contact_selection').attr({'disabled': 'disabled'}).addClass('disabled');
                    $('div.invoice_create_contact').show();
                } else {
                    $('.invoicing_contact_selection').removeAttr('disabled').removeClass('disabled');
                    $('div.invoice_create_contact').hide();
                }
            });

            //Toggle form of invoice address creation.
            $('.ship_diff_address').click(function(){
                if($(this).prop('checked')){
                    $('.shipping_contact_selection').attr({'disabled': 'disabled'}).addClass('disabled');
                    $('div.ship_create_contact').show();
                } else {
                    $('.shipping_contact_selection').removeAttr('disabled').removeClass('disabled');
                    $('div.ship_create_contact').hide();
                }
            });

            //Initialize autocomplete for state and country selection.
            $('.ship_create_contact').find('.client_state').autocomplete({
                source: self.pos.states || false,
                select: function (event, ui) {
                    self.shipping_state = ui.item.id;
                    return ui.item.value
                }
            });
            $('.ship_create_contact').find('.client_country').autocomplete({
                source: self.pos.countries || false,
                select: function (event, ui) {
                    self.shipping_country = ui.item.id;
                    return ui.item.value
                }
            });
            $('.invoice_create_contact').find('.client_state').autocomplete({
                source: self.pos.states || false,
                select: function (event, ui) {
                    self.invoice_state = ui.item.id;
                    return ui.item.value
                }
            });
            $('.invoice_create_contact').find('.client_country').autocomplete({
                source: self.pos.countries || false,
                select: function (event, ui) {
                    self.invoice_country = ui.item.id;
                    return ui.item.value
                }
            });
        },
    });
    gui.define_popup({name:'sale_order_popup', widget: SaleOrderPopup});

    //Reject Reason Popup
    var RejectSoPopup = PopupWidget.extend({
        template: 'RejectSoPopup',
        show: function(options){
            var self = this;
            this._super(options);
            var options = options || {};
            this.order = options.order || false
            this.sale_order_screen = options.sale_order_screen || false
            self.renderElement();
        },
        //Validates that reject reason is specified or not.
        //If reject reason is specified calls the set_cancel_order method to reject the sale order with reason.
        click_confirm: function(){
            var self = this;
            //Display Warning when reason is blank.
            var reject_reason = this.$('.sale_order_reject_note').val() || '';
            if(!reject_reason){
                alert(_t("Please enter Reason."))
                return;
            }
            if(self.order && reject_reason){
                var vals;
                //Set current sale order in cancelled state.
                new Model('sale.order').get_func('set_cancel_order')(vals = {
                    'order_id': self.order.id,
                    'reject_reason': reject_reason,
                    'pos_config_id': self.pos.config.id,
                }).then(function(data) {
                    if(data && data.error){
                        self.gui.show_popup('error', {
                            'title': _t('Warning'),
                            'body': data.error,
                        });
                        return;
                    }
                    if(data){
                        self.order.state = data;
                        self.sale_order_screen.reloading_orders()
                        var accept = document.querySelector('#order_accept[data-id="' + self.order.id + '"]');
                        var reject = document.querySelector('#order_reject[data-id="' + self.order.id + '"]');
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
                        'title': _t('Warning: Could Reject Order.'),
                        'body': error_body,
                    });
                });
            }
            self.gui.close_popup();
        },
        //Close the reject reason popup.
        click_cancel: function(){
            var self = this;
            this.gui.close_popup();
        },
        renderElement: function(){
            var self = this;
            this._super();
        },
    });
    gui.define_popup({name:'reject_so_popup', widget: RejectSoPopup});
});