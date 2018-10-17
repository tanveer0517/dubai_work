# -*- encoding: utf-8 -*-
{
    'name': 'Pole Customer Display',
    'version': '1.0',
    'category': 'Hardware Drivers',
    'summary': 'Adds support for Customer Display in the Point of Sale',
    'description': """
Hardware Customer Display
=========================

This module adds support for Customer Display in the Point of Sale.
This module is designed to be installed on the *POSbox* (i.e. the
proxy on which the USB devices are connected) and not on the main
Odoo server. On the main Odoo server, you should install the module
*pos_customer_display*.

The configuration of the hardware is done in the configuration file of
the Odoo server of the POSbox. You should add the following entries in
the configuration file:

* customer_display_device_name (default = /dev/ttyUSB0) and also work with the COM port
* customer_display_device_rate (default = 9600)
* customer_display_device_timeout (default = 2 seconds)

The number of cols of the Customer Display (usually 20) should be
configured on the main Odoo server, in the menu Point of Sale >
Configuration > Point of Sales. The number of rows is supposed to be 2.

It should support most serial and USB-serial LCD displays out-of-the-box
or with inheritance of a few functions.

    """,
    'author': "Bist Solutions Pvt Ltd.",
    'website': 'http://bistasolutions.com',
    'depends': ['hw_proxy'],
    'external_dependencies': {
        'python': ['serial', 'unidecode'],
    },
    'data': [],
}
