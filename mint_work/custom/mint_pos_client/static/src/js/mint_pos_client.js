odoo.define('mint_pos_client', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var Model = require('web.DataModel');
    var core = require('web.core');
    var _t = core._t;

    screens.ClientListScreenWidget.include({

        show: function(){
            this._super()

            var self = this;
            this.$('.searchbox').css('width', 'auto')

            this.$('.clientsearchbox .clientsearch-clear').click(function(){
                self.perform_search_client(false);
            });

            var client_search_timeout = null;

            this.$('.clientsearchbox input').on('keypress',function(event){
                if(event.which === 13){
                    clearTimeout(client_search_timeout);

                    var searchbox = this;

                    client_search_timeout = setTimeout(function(){
                        self.perform_search_client(searchbox.value);
                    },70);
                }
                
            });
        },
        perform_search_client: function(qry){
            var self = this;
            var query = qry ? qry : self.$('.clientsearchbox input')[0].value;
            if(query){
                new Model('res.partner').call('fetch_client',[query]).then(function(partner_id){
                    if(partner_id){
                        self.saved_client_details(partner_id);
                        self.$('.clientsearchbox input')[0].value = '';
                        self.$('.clientsearchbox input').focus();
                        var partner = self.pos.db.get_partner_by_id(partner_id);
                        if(partner){
                            self.display_client_details('show',partner);
                        }
                    }else{
                        self.gui.show_popup('error',{
                            'title': _t('Warning'),
                            'body': _t('No Matching Record Found. Please create Customer !'),
                        });
                    }
                    
                },function(err,event){
                    event.preventDefault();
                    var error_body = _t('Your Internet connection is probably down.');
                    if (err.data) {
                        var except = err.data;
                        error_body = except.arguments && except.arguments[0] || except.message || error_body;
                    }
                    self.gui.show_popup('error',{
                        'title': _t('Error: Could Fetch Customer'),
                        'body': error_body,
                    });
                });
            }else{
                self.gui.show_popup('error',{
                    'title': _t('Warning: Empty Fetch Customer !'),
                    'body': _t('Please add customer detail like email/phone/ref in  order to fetch the customer.'),
                });
            }
        },

        //Override this method to make phone and email field required in pos.
        save_client_details: function(partner) {
            var self = this;
            
            var fields = {};
            this.$('.client-details-contents .detail').each(function(idx,el){
                fields[el.name] = el.value || false;
            });

            if (!fields.name) {
                this.gui.show_popup('error',_t('A Customer Name Is Required'));
                return;
            }

            if (!fields.email) {
                this.gui.show_popup('error',_t('A Customer Email Is Required'));
                return;
            }

            if (!fields.phone) {
                this.gui.show_popup('error',_t('A Customer Phone Is Required'));
                return;
            }

            if (this.uploaded_picture) {
                fields.image = this.uploaded_picture;
            }

            fields.id           = partner.id || false;
            fields.country_id   = fields.country_id || false;

            new Model('res.partner').call('create_from_ui',[fields]).then(function(partner_id){
                self.saved_client_details(partner_id);
            },function(err,event){
                event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (err.data) {
                    var except = err.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                if (error_body == _t("Customer already exist!")){
                    error_body += _t(" Please fetch customer.")
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
            });
        },
    });

});
