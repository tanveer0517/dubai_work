odoo.define('mint_pos_receipt.pos_receipt_2_lang', function(require) {
    "use strict";
    var core = require('web.core');
    var pos_screen = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
    var _t = core._t;
    var Session = require('web.session');
    var models = require('point_of_sale.models');
    var Backbone = window.Backbone;

    // Load Street2 field from partner
    models.load_fields("res.partner", ['street2']);
    // Load Product with multi lang
    models.load_models([{
        model: 'product.product',
        fields: ['display_name'],
        order: ['sequence', 'default_code', 'name'],
        domain: [
            ['sale_ok', '=', true],
            ['available_in_pos', '=', true]
        ],
        context: function(self) {
            var load_lang = self.config.first_lang == Session.user_context.lang ? self.config.second_lang : self.config.first_lang
            self.config.other_lang = load_lang;
            return load_lang && {
                pricelist: self.pricelist.id,
                display_default_code: false,
                lang: load_lang
            } || {};
        },
        loaded: function(self, products) {
            self.lang_products = products;
        },
    }], {
        'after': 'account.fiscal.position.tax'
    });

    //Inherited receipt screen to add changes related to multi receipt.
    pos_screen.ReceiptScreenWidget.include({
        //Used to translate the product name.
        translate_product_lang: function(order_line) {
            var self = this;
            var find_product = _.find(self.pos.lang_products, function(product) {
                return product.id === order_line.product.id;
            });
            if (find_product) {
                order_line.product.lang_display_name = find_product.display_name;
            }
            return order_line;
        },
        //Override print xml in order to add company address.
        print_xml: function() {
        	var self = this;
        	var company_address = '';
            _.each(self.pos.partners, function(partner){
                if (partner.id == self.pos.company.id){
                    if(partner.street){
                        company_address += partner.street + " "
                    }
                    if(partner.street2){
                        company_address += partner.street2 + " "
                    }
                    if(partner.city){
                        company_address += partner.city + " "
                    }
                    if(partner.state_id){
                        company_address += partner.state_id[1] + " "
                    }
                    if(partner.country_id){
                        company_address += partner.country_id[1] + " "
                    }
                }
            })
            var env = {
                widget:  this,
                pos: this.pos,
                order: this.pos.get_order(),
                receipt: this.pos.get_order().export_for_printing(),
                paymentlines: this.pos.get_order().get_paymentlines(),
                company_address: company_address,
            };
            var receipt = QWeb.render('XmlReceipt',env);

            this.pos.proxy.print_receipt(receipt);
            this.pos.get_order()._printed = true;
        },
        //helper method to render receipt based on configuration.
        render_receipt: function() {
            var self = this;
            var order = this.pos.get_order();
            var order_lines = order.get_orderlines();
            var company_address = '';
            _.each(self.pos.partners, function(partner){
                if (partner.id == self.pos.company.id){
                    if(partner.street){
                        company_address += partner.street + " "
                    }
                    if(partner.street2){
                        company_address += partner.street2 + " "
                    }
                    if(partner.city){
                        company_address += partner.city + " "
                    }
                    if(partner.state_id){
                        company_address += partner.state_id[1] + " "
                    }
                    if(partner.country_id){
                        company_address += partner.country_id[1] + " "
                    }
                }
            })
            // Translate in arabic
            ajax.jsonRpc('/web/webclient/translations', 'call', {
                'mods': Session.module_list,
                'lang': self.pos.config.other_lang,
                'context': _.extend({
                    'get_source': self.pos.config.other_lang == 'en_US' ? true : false
                }, Session.user_context),
            })
            .then(function(trans) {
                self.trans_change = trans;
            }).then(function() {
                var template = 'PosTicket';
                var all_templates = QWeb.templates;
                var keys = _.keys(all_templates);
                for (var i = 0; i < order_lines.length; i++) {
                    self.translate_product_lang(order_lines[i]);
                };

                if (self.pos.config.allow_multi_lang_receipt && self.pos.config.print_wise == 'section_wise') {
                    var first_lang = QWeb.render('PosTicket', {
                        widget: self,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order_lines,
                        paymentlines: order.get_paymentlines(),
                        report_option: 'section_wise',
                        company_address: company_address,
                    });
                    var current_trans = _t.database;
                    _t.database.set_bundle(self.trans_change);
                    // Translation Function
                    function translate_node(node) {
                        if (node.nodeType === 3) { // TEXT_NODE
                            if (node.nodeValue.match(/\S/)) {
                                var space = node.nodeValue.match(/^([\s]*)([\s\S]*?)([\s]*)$/);
                                node = document.createTextNode('' + space[1] + $.trim(_t(space[2])) + space[3]);
                            }
                        } else if (node.nodeType === 1 && node.hasChildNodes()) { // ELEMENT_NODE
                            _.each(node.childNodes, translate_node);
                        }
                    }
                    translate_node(all_templates[template]);
                    QWeb.templates['PosArabic'] = $(all_templates[template])[0];
                    var second_lang = QWeb.render('PosArabic', {
                        widget: self,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order.get_orderlines(),
                        paymentlines: order.get_paymentlines(),
                        lang_display_name: true,
                        report_option: 'section_wise'
                    });
                    _t.database = current_trans;
                    if (self.pos.config.first_lang == self.pos.config.other_lang) {
                        var receipt_html = second_lang + "<br/>" + first_lang;
                    } else {
                        var receipt_html = first_lang + "<br/>" + second_lang;
                    }
                    self.$('.pos-receipt-container').html(receipt_html);
                } else if (self.pos.config.allow_multi_lang_receipt && self.pos.config.print_wise == 'line_wise') {
                    var first_lang = QWeb.render('PosTicket', {
                        widget: self,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order_lines,
                        paymentlines: order.get_paymentlines(),
                        report_option: 'line_wise',
                        company_address: company_address,
                    });
                    self.$('.pos-receipt-container').html(first_lang);
                } else {
                    var ticket = QWeb.render('PosTicket', {
                        widget: self,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order_lines,
                        paymentlines: order.get_paymentlines(),
                        report_option: 'none',
                        company_address: company_address,
                    });
                    self.$('.pos-receipt-container').html(ticket);
                }

            }).promise();
        },
    });

});
