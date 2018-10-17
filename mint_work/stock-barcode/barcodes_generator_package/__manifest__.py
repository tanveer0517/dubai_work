# -*- coding: utf-8 -*-

{
    "name": "Generate Barcodes for Packaging",
    "summary": "Generate Barcodes for Product Packaging",
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
        "views/product_packaging.xml",
    ],
    "demo": [
        "demo/ir_sequence.xml",
        "demo/barcode_rule.xml",
        "demo/product_packaging.xml",
        "demo/function.xml",
    ],
}
