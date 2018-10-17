# -*- coding: utf-8 -*-

from datetime import datetime
from odoo  import api, fields, models, _
                    
class ticket_deadline(models.Model):
    _name= "ticket.deadline"
    
    name = fields.Char( 
        string    = "Name",
        size      = 10,
        required  = True,
        translate = True 
    )

    value_day = fields.Integer( 
        string    = "Days",
        translate = True
    )

    value_hours = fields.Integer(
        string    = "Hours",
        translate = True
    )

