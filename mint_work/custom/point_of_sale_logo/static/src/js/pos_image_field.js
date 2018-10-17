odoo.define("point_of_sale_logo.image", function (require) {
    "use strict";
    var PosBaseWidget = require('point_of_sale.chrome');
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var core = require('web.core');

    var QWeb = core.qweb;

    //Load the config logo from the pos config.
    models.load_models([{
        label: 'logo',
        loaded: function(self) {
            if(self.config.image){
                self.config_logo = new Image();
                var  logo_loaded = new $.Deferred();
                self.config_logo.onload = function(){
                    var img = self.config_logo;
                    var ratio = 1;
                    var targetwidth = 300;
                    var maxheight = 150;
                    if( img.width !== targetwidth ){
                        ratio = targetwidth / img.width;
                    }
                    if( img.height * ratio > maxheight ){
                        ratio = maxheight / img.height;
                    }
                    var width  = Math.floor(img.width * ratio);
                    var height = Math.floor(img.height * ratio);
                    var c = document.createElement('canvas');
                        c.width  = width;
                        c.height = height;
                    var ctx = c.getContext('2d');
                        ctx.drawImage(self.config_logo,0,0, width, height);

                    self.config_logo_base64 = c.toDataURL();
                    logo_loaded.resolve();
                };
                self.config_logo.onerror = function(){
                    logo_loaded.reject();
                };
                self.config_logo.crossOrigin = "anonymous";
                self.config_logo.src = window.location.origin + '/web/image?model=pos.config&field=image&id='+self.config.id;

                return logo_loaded;
            }
        },
    }], {
        'after': 'pictures'
    });

  //Load the receipt logo from the pos config.
    models.load_models([{
        label: 'Receipt logo',
        loaded: function(self) {
            if(self.config.enable_receipt_image){
                self.receipt_logo = new Image();
                var logo_loaded = new $.Deferred();
                self.receipt_logo.onload = function(){
                    var img = self.receipt_logo;
                    var ratio = 1;
                    var targetwidth = 300;
                    var maxheight = 150;
                    if( img.width !== targetwidth ){
                        ratio = targetwidth / img.width;
                    }
                    if( img.height * ratio > maxheight ){
                        ratio = maxheight / img.height;
                    }
                    var width  = Math.floor(img.width * ratio);
                    var height = Math.floor(img.height * ratio);
                    var c = document.createElement('canvas');
                        c.width  = width;
                        c.height = height;
                    var ctx = c.getContext('2d');
                        ctx.drawImage(self.receipt_logo,0,0, width, height);

                    self.receipt_logo_base64 = c.toDataURL();
                    logo_loaded.resolve();
                };
                self.receipt_logo.onerror = function(){
                    logo_loaded.reject();
                };
                self.receipt_logo.crossOrigin = "anonymous";
                self.receipt_logo.src = window.location.origin + '/web/image?model=pos.config&field=receipt_image&id='+self.config.id;

                return logo_loaded;
            }
        },
    }], {
        'after': 'pictures'
    });
    var _super_posmodel = models.PosModel;
    models.PosModel = models.PosModel.extend({
        //Initially set config logo and base64 logo to null.
        initialize: function(session, attributes) {
            _super_posmodel.prototype.initialize.call(this, session, attributes);
            var self = this;
            this.config_logo = null;
            this.config_logo_base64 = '';
            this.receipt_logo = null;
            this.receipt_logo_base64 = '';
        },
    });

});
