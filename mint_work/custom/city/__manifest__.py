# -*- coding: utf-8 -*-

{
    "name": "City-Helps to keep Homogeneous address data in the Database",
    "version": "10.0.1.0.0",
    'author': "Bista Solutions ",
    'website': 'http://www.bistasolutions.com',
    "category": "Hidden",
    "license": "AGPL-3",
    "summary": "City-Helps to keep Homogeneous address data in the Database",
    "description": """Creates a model for storing cities Zip code, city,
        state and country fields are replaced with a location
        field in partner and partner contact forms.
        This module helps to keep homogeneous address data in the database.""",
    "depends": ['sales_team', 'base'],
    "data": [
        "views/city_view.xml",
        "security/ir.model.access.csv",
        ],
    "installable": True,
    "auto_install": True,
}
