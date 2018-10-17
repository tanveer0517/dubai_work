odoo.define('saas_plan_subscription', function (require) {
"use strict";
    var website = require('website.website');
    var ajax = require('web.ajax');
    var session = require('web.session');
    var Model = require('web.Model');
    function findTotal(new_price){
        var arr = document.getElementsByName('plan_price');
        var numofu  = document.getElementsByName('num_of_user_1');
        var sub_total = document.getElementsByName('sub_total');
        var interval = document.getElementById("interval").value;
        var tot=0.0;
        var final_total=0.0;
        var product_qty = 0;
        var interval_units = document.getElementById("interval_units");
        var selected_interval = interval_units.options[interval_units.selectedIndex].value;
        if (selected_interval == 'monthly'){
            product_qty = 1;
        }
        if (selected_interval == 'yearly'){
            product_qty = 12;
        }
        for(var i=0;i<numofu.length;i++){
            tot = parseFloat(arr[i].value) * parseFloat(numofu[i].value) *
            parseInt(product_qty) * parseInt(interval);
            sub_total[i].value = tot;
            final_total += tot;
        }
        document.getElementById("final_total").value = final_total ;
     }

    function total_pricelist(){
        var model = new Model('product.pricelist');

        var numofu  = document.getElementsByName('num_of_user_1');
        var sub_total = document.getElementsByName('sub_total');
        var interval = document.getElementById("interval").value;
        var products = document.getElementsByName('product_id');

        var interval_units = document.getElementById("interval_units");
        var selected_interval = interval_units.options[interval_units
        .selectedIndex].dataset.pl_id
        var tot=0;
        var final_total=0;
        var new_price = []

        var i=0;
        for(i;i<products.length;i++){
               model.call('price_get', [parseInt(selected_interval),
               parseInt
               (products[i]
               .dataset.product_id)
               ,parseInt(numofu[i].value),'None']).then(function (price) {
                var products = document.getElementsByName('product_id');
                new_price.push(price[selected_interval]);
                set_price(new_price);
                });
        }
    }

    function set_price(new_price){
        var price_arr = document.getElementsByName('plan_price');
        for(var i=0;i<new_price.length;i++){
            price_arr[i].value = new_price[i];
        }
        findTotal(new_price);
    }


    function set_date(){
        var arr = document.getElementsByName('next_invoice_date');
        var interval_units = document.getElementById("interval_units");
        var selected_interval = interval_units.options[interval_units.selectedIndex].value;
        var interval = document.getElementById("interval").value;
        var CurrentDate = new Date();
        var int_unit = 0;
        if (selected_interval == 'monthly'){
            int_unit = 1;
            CurrentDate.setMonth(CurrentDate.getMonth() + parseInt(interval));
        }
        if (selected_interval == 'yearly'){
            int_unit = 12;
            CurrentDate.setFullYear(CurrentDate.getFullYear()+ parseInt
                (interval));
        }

        for(var i=0;i<arr.length;i++){
            arr[i].value = CurrentDate.toISOString().slice(0,10);
        }

    }

    $("#saas_plan_select").change(function(ev){
    });

    $(".n_user").change(function(ev){
         findTotal();
    });

    $("#interval").change(function(ev){
        set_date();
        findTotal();
    });

    $("#interval_units").change(function(ev){
        total_pricelist();
        set_date();
    });

    $(".confirm_order").click(function(ev){
        var contract_dic = {}
        var values_units = [];
        $("input[name='num_of_user_1']").each(function() {
          values_units.push($(this).val());
        });
        var uid = document.getElementById('user_id').value;
        var interval_units = document.getElementById("interval_units");
        var selected_interval = interval_units.options[interval_units.selectedIndex].text;
        var interval = document.getElementById("interval").value;
        var start_date = document.getElementById("start_date").value;
        var next_invoice_date = document.getElementById("next_invoice_date").value;
        var products = document.getElementsByName('product_id');
        var $data = $("#product_id");
        var $price = document.getElementsByName('plan_price');
        var $numofu = document.getElementsByName('num_of_user_1');
        var pricelist_id = interval_units.options[interval_units
        .selectedIndex].dataset.pl_id
        var line_list = []
        for(var i=0;i<products.length;i++){
            var line_dic = {}
            line_dic['product_id'] = parseInt(products[i].dataset.product_id);
            line_dic['name'] = products[i].value;
            line_dic['quantity'] = parseInt(values_units[i]);
            line_dic['price_unit'] = parseInt($price[i].dataset.price);
            line_list.push(line_dic);

        }
        selected_interval
        contract_dic = {
            'pricelist_id': pricelist_id,
            'partner_id' : uid,
            'recurring_invoices': 'True',
            'recurring_interval': parseInt(interval),
            'recurring_rule_type': selected_interval,
            'date_start': start_date,
            'recurring_invoice_line_ids':line_list,
            'recurring_next_date': next_invoice_date
        }
        ajax.jsonRpc("/confirm_order", 'call', contract_dic);
        window.location.href = '/redirect_confirm';
    });
});
