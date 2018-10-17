odoo.define('saas_client_portal_access.UserMenu', function (require) {
"use strict";

var framework = require('web.framework');
var Model = require('web.Model');
var session = require('web.session');
var framework = require('web.framework');
var UserMenu = require('web.UserMenu');
var ajax = require('web.ajax');
    UserMenu.include({
       on_menu_empower_account: function() {
            this.trigger_up('clear_uncommitted_changes', {
                callback: function() {
                    ajax.jsonRpc('/login_parameter', 'call', {}).then
                    (function (data) {
                        window.open(data['portal_url']);
                    }).fail(function () {
                        alert("Please contact systerm administrator");
                    });
                },
            });
       }
    });
})



