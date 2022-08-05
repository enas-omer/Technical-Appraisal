# -*- coding: utf-8 -*-
from random import randint
from odoo import fields, models 

class Tag(models.Model):
    _name = 'hd.tag'

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color', default=_default_color)