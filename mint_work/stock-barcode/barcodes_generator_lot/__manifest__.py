# -*- coding: utf-8 -*-

{
    "name": "Generate Barcodes for Stock Production Lots",
    "version": "10.0.1.0.0",
    "category": "Tools",
    'author': "Bista Solutions",
    'website': "http://www.bistasolutions.com",
    "license": "AGPL-3",
    "depends": [
        "barcodes_generator_abstract",
        "stock",
    ],
    "data": [
        "views/stock_production_lot.xml",
    ],
    "demo": [
        "demo/ir_sequence.xml",
        "demo/barcode_rule.xml",
        "demo/stock_production_lot.xml",
        "demo/function.xml",
    ],
}
