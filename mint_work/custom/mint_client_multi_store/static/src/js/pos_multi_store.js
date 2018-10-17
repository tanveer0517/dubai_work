odoo.define('pos_multi_store.pos_multi_store_product_load', function(require) {
    "use strict";
    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        load_server_data: function() {
            var self = this;
            _.find(self.models, function(model) {
                if (model.model == "product.product") {
                    console.log('12344444444444444fff44445555555555',self)
                    model.domain.push('store_id', '=', self.config.store_id[0])
                    console.log("FFFFFFFFFFFFF",self,model)
                }
            })
            return _super_posmodel.prototype.load_server_data.call(this);;
        },
    });
});
