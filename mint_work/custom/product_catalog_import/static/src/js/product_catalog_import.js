odoo.define('product_catalog.import', function (require) {
    "use strict";
    var core = require('web.core');
    var QWeb = core.qweb;
    var Model = require('web.DataModel');
    var ListView = require('web.ListView');
    QWeb.add_template("/product_catalog_import/static/src/xml/import_product_view.xml");
    ListView.include({
        render_buttons: function() {
            var result = this._super.apply(this, arguments); // Sets this.$buttons
            var self = this;
            if(!self.no_leaf && self.options.action_buttons !== false && self.model == 'product.catelog' && !this.editable()){
                self.$import_button = $(QWeb.render("ListView.ImportButton", {'widget': self}));
                self.$import_button.click(function(){
                    return new Model('product.catelog').call('import_catalog').done(function(r){
                        self.do_action(r)
                    })
                })
                self.$import_button.appendTo(self.$buttons);
            }
            return result;
        },
    })
});
