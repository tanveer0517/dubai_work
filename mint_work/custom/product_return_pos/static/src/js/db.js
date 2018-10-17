odoo.define('product_return_pos.db', function(require) {

    var DB = require('point_of_sale.DB');
    DB.include({
        init: function(options) {
            this._super.apply(this, arguments);
            this.pos_order_sorted = [];
            this.pos_order_by_id = {};
            this.pos_order_search_string = "";
            this.pos_order_write_date = null;
        },
        add_pos_orders: function(orders){
            var updated_count = 0;
            var new_write_date = '';
            var order;
            for(var i = 0, len = orders.length; i < len; i++){
                order = orders[i];

                order.return_status = order.return_status;
                var local_order_date = (this.pos_order_write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                var dist_order_date = (order.write_date || '').replace(/^(\d{4}-\d{2}-\d{2}) ((\d{2}:?){3})$/, '$1T$2Z');
                if (    this.pos_order_write_date &&
                        this.pos_order_by_id[order.id] &&
                        new Date(local_order_date).getTime() + 1000 >=
                        new Date(dist_order_date).getTime() ) {
                    // FIXME: The write_date is stored with milisec precision in the database
                    // but the dates we get back are only precise to the second. This means when
                    // you read orders modified strictly after time X, you get back orders that were
                    // modified X - 1 sec ago. 
                    continue;
                } else if ( new_write_date < order.write_date ) { 
                    new_write_date  = order.write_date;
                }
                if (!this.pos_order_by_id[order.id]) {
                    this.pos_order_sorted.push(order.id);
                }
                this.pos_order_by_id[order.id] = order;

                updated_count += 1;
            }

            this.pos_order_write_date = new_write_date || this.pos_order_write_date;

            if (updated_count) {
                // If there were updates, we need to completely 
                // rebuild the search string and the barcode indexing

                this.pos_order_search_string = "";

                for (var id in this.pos_order_by_id) {
                    order = this.pos_order_by_id[id];
                    this.pos_order_search_string += this._pos_order_search_string(order);
                }
            }
            return updated_count;
        },
        _pos_order_search_string: function(order) {
            var str = order.pos_reference;
            if (order.return_ref) {
                str += '|' + order.return_ref;
            }
            str = '' + order.id + ':' + str.replace(':', '') + '\n';
            return str;
        },
        get_pos_order_write_date: function(){
            return this.pos_order_write_date || "1970-01-01 00:00:00";
        },
        get_pos_order_by_id: function(id){
            return this.pos_order_by_id[id];
        },
        get_pos_order_sorted: function(max_count){
            max_count = max_count ? Math.min(this.pos_order_sorted.length, max_count) : this.pos_order_sorted.length;
            var orders = [];
            for (var i = 0; i < max_count; i++) {
                orders.push(this.pos_order_by_id[this.pos_order_sorted[i]]);
            }
            return _.sortBy(orders, 'id').reverse();
        },
        search_pos_orders: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.pos_order_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_pos_order_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
    });
});