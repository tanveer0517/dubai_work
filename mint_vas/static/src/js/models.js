odoo.define('mint_vas.models', function(require) {
    "use strict";

    var vas_model = require('point_of_sale.models');
    vas_model.load_fields("res.partner", "card_number");
    vas_model.load_fields("res.partner", "reference_pnr");
    vas_model.load_fields("res.partner", "addc_acc_no");
    vas_model.load_fields("pos.order","reference_number");
    vas_model.load_fields("pos.order","transaction_number")
    var screens = require('point_of_sale.screens');
    
    var _super = vas_model.Order;
    vas_model.Order = vas_model.Order.extend({
    export_for_printing: function(){
        var json = _super.prototype.export_for_printing.apply(this,arguments);
            json.reference_number = {
                reference_number: localStorage.getItem('referenceNo'),
            };
            json.transaction_number = {
                transaction_number: localStorage.getItem('receiptNo'),
            };
        return json;
    },
    export_as_JSON: function(){
        var json = _super.prototype.export_as_JSON.apply(this,arguments);
        json.reference_number = localStorage.getItem('referenceNo');
        json.transaction_number = localStorage.getItem('receiptNo');
        console.log('json',json)
        return json;
    },
    });

    screens.ClientListScreenWidget.include({
        save_changes: function() {
            var self = this;
            this._super();
            var order = self.pos.get_order();
            vas_services();
            console.log("Orders:", order);
            setTimeout(function(){

            var pos_session_id = order.pos_session_id;
            var key_unpaid_orders;
            for(var i=0; i< localStorage.length; i++){
               var keyUnpaidOrders = localStorage.key(i);
               if(keyUnpaidOrders.lastIndexOf('unpaid_orders') != -1)
                   key_unpaid_orders = localStorage.key(i); 
            }

            //get the current session order
            var unpaidOrders = JSON.parse(localStorage.getItem(key_unpaid_orders));
            var unpaidOrdersCurSession = new Array();
            $.each(unpaidOrders, function(_index, _order){
                if(_order.data.pos_session_id === pos_session_id){
                    unpaidOrdersCurSession.push(_order);
                }
            });

            //check partner not false
             $.each(unpaidOrdersCurSession, function(_index, _order){
                if(_order.data.partner_id != false){
                   //get recharge amt from customer
                   let rechargeAmt = null;
                   $.each(order.pos.partners, function(_index1, _partner){
                        if( _partner.id === _order.data.partner_id )
                            rechargeAmt = localStorage.getItem('rechargeAmt');
                   });

                   //first set the mode to price
                   $('.numpad > [data-mode="price"]').trigger("click");

                   //set the value
                   if( rechargeAmt != null ){
                        let ramt = rechargeAmt.toString().split('');
                        $.each(ramt, function(_index1, _ch){
                            $(".product-screen .numpad > .number-char:contains("+ _ch +")").trigger("click");
                        });
                        localStorage.setItem('rechargeAmt', null);
                   }
                   
                }
            });

            }, 1000);
            
             

        }
    });
    
});

function vas_services(){
    odoo.define('mint_vas.get_plan', function (require) {
    "use strict";
    var Model = require('web.Model');
    var key_unpaid_orders, pos_session_id_key;
    for(var i=0; i< localStorage.length; i++){
        var keyUnpaidOrders = localStorage.key(i);
        if(keyUnpaidOrders.lastIndexOf('unpaid_orders') != -1)
            key_unpaid_orders = localStorage.key(i); 
        if(keyUnpaidOrders.lastIndexOf('pos_session_id') != -1 )
            pos_session_id_key = localStorage.key(i);
    }
    //get the current session order
    var unpaidOrders = JSON.parse(localStorage.getItem(key_unpaid_orders));
    var unpaidOrdersCurSession = new Array();
    $.each(unpaidOrders, function(_index, _order){
        if(_order.data.pos_session_id === parseInt(localStorage.getItem(pos_session_id_key))){
            unpaidOrdersCurSession.push(_order);
            console.log(unpaidOrdersCurSession);
        }
    });

    $.each(unpaidOrdersCurSession, function(_index, _order){
        $.each(_order.data.lines, function(_ii, _ll){
            new Model("pos.order").call("get_product_name",[_ll[2].product_id]).then(function(result){
                console.log(result);//show result in console
                if(result == 'ADDC'){
                    fnCallAddcTopupInfo(_order.data.partner_id,_ll[2].price_unit);
                }
                else if(result == 'Du Voucher'){
                    
                }
                else if(result == 'Du TopUp'){
                    fnCallDuTopupInfo(_order.data.partner_id,_ll[2].price_unit);
                }
                else if(result == 'Etisalat TopUp'){
                    fnCallEtisalatTopupInfo(_order.data.partner_id,_ll[2].price_unit);
                }
                else if(result == 'Etislat Voucher'){
                    
                }
                else if(result == 'Fly Dubai'){
                    fnCallFlyDubaiInfo(_order.data.partner_id,_ll[2].price_unit);  
                }
                else if(result == 'Salik'){

                }
            });
        });
    });    

});
        
}

function fnCallDuTopupInfo(_partnerId,_amount){
let partnerId = _partnerId;
let amount = _amount;
odoo.define('mint_vas.get_plan', function (require) {
    "use strict";
    var Model = require('web.Model');
    new Model("pos.order").call("get_du_topup",[[partnerId,amount]]).then(function(result){
        console.log(result);
        localStorage.setItem("receiptNo",result.receipt_num);
        localStorage.setItem("referenceNo",result.reference_num);
    });
});
}   

function fnCallEtisalatTopupInfo(_partnerId,_amount){
let partnerId = _partnerId;
let amount = _amount;
odoo.define('mint_vas.get_plan', function (require) {
    "use strict";
    var Model = require('web.Model');
    new Model("pos.order").call("get_etisalat_topup",[[partnerId,amount]]).then(function(result){
        console.log(result);
        localStorage.setItem("receiptNo",result.receipt_num);
        localStorage.setItem("referenceNo",result.reference_num);
    });
});
}

function fnCallFlyDubaiInfo(_partnerId,_amount){
let partnerId = _partnerId;
let amount = _amount;
odoo.define('mint_vas.get_plan', function (require) {
    "use strict";
    var Model = require('web.Model');
    new Model("pos.order").call("get_fly_dubai",[[partnerId,amount]]).then(function(result){
        console.log(result);
        localStorage.setItem("receiptNo",result.receipt_num);
        localStorage.setItem("referenceNo",result.reference_num);
    });
});
}

function fnCallAddcTopupInfo(_partnerId,_amount){
let partnerId = _partnerId;
let amount = _amount;
odoo.define('mint_vas.get_plan', function (require) {
    "use strict";
    var Model = require('web.Model');
    new Model("pos.order").call("get_addc_topup",[[partnerId,amount]]).then(function(result){
        console.log(result);
        localStorage.setItem("receiptNo",result.receipt_num);
        localStorage.setItem("referenceNo",result.reference_num);
    });
});
}