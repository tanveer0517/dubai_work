function fnCusDisplay(){
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

    let product_ids = new Array();
    $.each(unpaidOrdersCurSession, function(_index, _order){
        $.each(_order.data.lines, function(_ii, _ll){
            product_ids.push( _ll[2].product_id );
            new Model("pos.order").call("get_product_name",[_ll[2].product_id]).then(function(result){
                console.log(result);//show result in console
                if(result == 'International TopUp'){
                    fnCallOperatorInfo($('.client-phone').text());
                }
            });
        });
    });    

});

}
// function fnCusDisplay(){
//     fnCallOperatorInfo($('.client-phone').val());    
// }
// function fnCusEdit(){
//     fnCallOperatorInfo($('[name="phone"]').val());    
// }
function fnCusEdit(){
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
                if(result == 'International TopUp'){
                    fnCallOperatorInfo($('[name="phone"]').val());
                }
            });
        });
    });    

});
        
}

function fnCallOperatorInfo(_mobileNo){
let mobileNo = _mobileNo;
let uri = '/vasapi/intl-operator-info/'+mobileNo;   
settings = {  
  "url": uri,
  "method": "GET",
  "headers": {
    "content-type": "text/xml",
    "cache-control": "no-cache"
  }
}
$.ajax(settings).done(function (response) {
    xmlRes = new DOMParser();
    xmlDoc = xmlRes.parseFromString(response, "text/xml");    
    const res = {
        statusCode :  xmlDoc.getElementsByTagName("StatusCode")[0].childNodes[0].nodeValue,
        statusDescription: xmlDoc.getElementsByTagName("StatusDescription")[0].childNodes[0].nodeValue,
        country: xmlDoc.getElementsByTagName("Country")[0].childNodes[0].nodeValue,
        operator: xmlDoc.getElementsByTagName("Operator")[0].childNodes[0].nodeValue,
        destinationCurrency: xmlDoc.getElementsByTagName("DestinationCurrency")[0].childNodes[0].nodeValue,
        productList: xmlDoc.getElementsByTagName("ProductList")[0].childNodes[0].childNodes[0].nodeValue,
        retailPriceList: xmlDoc.getElementsByTagName("RetailPriceList")[0].childNodes[0].childNodes[0].nodeValue,
    }
    $('#mintVasVochers').html('');
    let aedCurries = res.retailPriceList.split(',');
    $.each( res.productList.split(','), function(_index, _val){
        let strHTML = '<div onClick="fnSetAmt(this, '+aedCurries[_index]+')" style="width: 100px; text-align: center; border: 1px solid grey; border-radius: 10px; margin: 2px; display: inline-block;     cursor: pointer; ">';
            strHTML += '<h3>'+ _val +'<sub>'+ res.destinationCurrency +'</sub></h3>';
            strHTML += '<h4><span>'+ aedCurries[_index] +'</span><sub>AED</sub></h4>';
            strHTML += '</div>';
        $('#mintVasVochers').append(strHTML);
    });

});
}

function fnSetAmt(_obj, _amt){
    $(_obj).parent().find('div').css("background-color", "white")
    $(_obj).css("background-color", "#efefef");

    localStorage.setItem('rechargeAmt', _amt);
}