odoo.define('mint_pos.multi_barcode', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

    models.load_fields("product.product", ['multi_barcode_ids']);

    //Load product.multi.barcode and add product by parent barcode and child barcode.
    models.load_models({
        model: 'product.multi.barcode',
        fields: ['product_id', 'lot_id', 'parent_barcode','child_barcode', 'qty'],
        context: [],
        loaded: function(self, barcodes){
            self.barcode_products = barcodes;
            var product_by_parent_barcode = {};
            var product_by_child_barcode = {};
            for(var i = 0, len = self.barcode_products.length; i < len; i++){
                if(self.barcode_products[i].product_id){
                    if(self.barcode_products[i].parent_barcode){
                        product_by_parent_barcode[self.barcode_products[i].parent_barcode] = self.db.get_product_by_id(self.barcode_products[i].product_id[0]);
                    }
                    if(self.barcode_products[i].child_barcode){
                        product_by_child_barcode[self.barcode_products[i].child_barcode] = self.db.get_product_by_id(self.barcode_products[i].product_id[0]);
                    }
                }
            }
            self.product_by_parent_barcode = product_by_parent_barcode;
            self.product_by_child_barcode = product_by_child_barcode;
        },
    });

    //Overridden scan product to extend scan functionality and all product to be add based on multi barcode.
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        scan_product: function(parsed_code){
            var self = this
            var selectedOrder = this.get_order();
            var product = this.db.get_product_by_barcode(parsed_code.base_code);
            var is_from_base_barcode = false
            var is_from_child_barcode = false
            if(product){
                is_from_base_barcode = true
            }
            if(!is_from_base_barcode){
                if(this.product_by_parent_barcode[parsed_code.base_code]){
                    product = this.product_by_parent_barcode[parsed_code.base_code]
                } else if(this.product_by_child_barcode[parsed_code.base_code]){
                    product = this.product_by_child_barcode[parsed_code.base_code]
                    is_from_child_barcode = true
                }else {
                    product = undefined;
                }
            }
            if(!product){
                return false;
            }
            if(!is_from_base_barcode){
                var qty = 0;
                _.each(self.barcode_products, function(bc) {
                    if(parsed_code.base_code == bc.parent_barcode || parsed_code.base_code == bc.child_barcode){
                        qty = parseInt(bc.qty)
                    }
                });
                if(!is_from_child_barcode){
                    selectedOrder.add_product(product, {quantity:qty});
                }else if(is_from_child_barcode){
                    selectedOrder.add_product(product);
                }
                return true;
            }
            if(parsed_code.type === 'price'){
                selectedOrder.add_product(product, {price:parsed_code.value});
            }else if(parsed_code.type === 'weight'){
                selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false});
            }else if(parsed_code.type === 'discount'){
                selectedOrder.add_product(product, {discount:parsed_code.value, merge:false});
            }else{
                selectedOrder.add_product(product);
            }
            return true;
        },
    });

});
