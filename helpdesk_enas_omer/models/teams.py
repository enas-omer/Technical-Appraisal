# -*- coding: utf-8 -*-

from odoo import fields, models 

class Team(models.Model):
    _name = 'hd.team'

    name = fields.Char('Name', required=True)
    max_resolution_time = fields.Float('Max Resolution Time', required=True)

    