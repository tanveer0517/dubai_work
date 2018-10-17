odoo.define('mint_helpdesk_extends.messageext', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var website_mail_thread = require('website_mail.thread');

    website_mail_thread.WebsiteMailThread.include({
        init: function(parent) {
            this._super(parent);
            this.events = _.extend(this.events || {}, {
                "change #attachment": "on_file_read",
            })
        },
        on_file_read: function(e){
            var self = this;
            if(e.currentTarget){
                var input = $(e.currentTarget)
                var file = input.prop('files')[0]
                var reader = new FileReader();
                var attachments = self.$('.o_website_chatter_form').find('#attachments')
                var attachment_name = self.$('.o_website_chatter_form').find('#attachment_name')
                reader.addEventListener("load", function () {
                    attachments.val(reader.result)
                    attachment_name.val(file.name)
                }, false);
                if (file) {
                    reader.readAsDataURL(file);
                }
            }
        },


    });

});
