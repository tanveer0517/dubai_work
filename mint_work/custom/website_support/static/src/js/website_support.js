odoo.define('website_support.website_support', function (require) {
'use strict';
$(document).ready(function () {
    var ajax = require('web.ajax')
    $("#stage_change").change(function(){
        var con_id = $("#stage_change").val();
        var url = "/support/help?stage=" + con_id
        window.location=url;
        });
    });
});