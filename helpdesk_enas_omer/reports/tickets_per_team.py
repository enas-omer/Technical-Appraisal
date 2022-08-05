import statistics
from statistics import mode, mean

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime

class TicketsPerTeamWizard(models.TransientModel):
    _name = 'tickets.per.team.wizard'

    team = fields.Many2one('hd.team', string='Team' ,required=True) 
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
        ('cancelled', 'Cancelled'),
        ], string='Status')
    
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'team': self.team.id,
                'state': self.state,
            },
        }

        return self.env.ref('helpdesk_enas_omer.tickets_per_team_report').report_action(self, data=data)


class TicketsPerTeamReport(models.AbstractModel):
    _name = 'report.helpdesk_enas_omer.tickets_per_team_template_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        team = data['form']['team']
        state = data['form']['state']

        team_name = self.env['hd.team'].search([('id', '=', team)])

        if state:
            hd_ticket = self.env['hd.ticket'].search([('state', '=', state),('team', '=', team)])
        else:
            hd_ticket = self.env['hd.ticket'].search([('team', '=', team)])
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'team_name':team_name.name,
            'docs': hd_ticket,
        }
