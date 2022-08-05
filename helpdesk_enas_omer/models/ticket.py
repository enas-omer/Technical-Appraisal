# -*- coding: utf-8 -*-

from odoo import fields, models ,api , _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class Ticket(models.Model):
    _name = 'hd.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "ticket_id"

    @api.model
    def _get_default_tag_ids(self):
        tag_ids = self.env['hd.tag'].search([])
        return tag_ids.ids

    ticket_id = fields.Char('Ticket ID', required=True, index=True, default='New', readonly=True, copy=False)
    team = fields.Many2one('hd.team', string='Team' ,required=True)
    name = fields.Char('Name', required=True)
    time_submitted = fields.Datetime(string="Time Submitted" ,readonly=True , copy=False)
    description = fields.Char('Description', required=True)
    assigned_to = fields.Many2one('res.users', string="Assigned to")
    priority = fields.Selection([('0', 'Very Low'),('1', 'Low'), ('2', 'Medium'), ('3', 'High')], string='Priority')
    customer_id = fields.Many2one('res.partner', string="Customer" ,required=True)
    customer_name = fields.Char('Customer Name', related='customer_id.name')
    customer_email = fields.Char('Customer Email', related='customer_id.email')
    customer_phone = fields.Char('Customer Phone', related='customer_id.phone')
    tag_ids = fields.Many2many('hd.tag' ,default=_get_default_tag_ids ,readonly=True)
    hosting_type = fields.Selection([('On-Premise', 'On-premise'), ('cloud', 'Cloud')], string='Hosting Type',required=True)
    server_url = fields.Char('Server URL')
    resolution_time = fields.Integer(string="Resolution Time", compute='_compute_resolution_time' , readonly=False , copy=False)
    solved_time = fields.Datetime(string="Solved Time" , copy=False)
    acvtivity_id = fields.Many2one('mail.activity', string="Activity")

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
        ('cancelled', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='new',
        track_visibility='onchange', copy=False)
    
    @api.model
    def create(self, vals):
        team = vals['team']

        seq = self.env['ir.sequence'].next_by_code('hd.ticket.seq') or '/'
        team = self.env['hd.team'].search([('id', '=', team)])
        vals['ticket_id'] = team.name + '/' + seq

        return super(Ticket, self).create(vals)      

    def action_run(self):
        self.state = 'in_progress'
        self.time_submitted = fields.Datetime.now()  

    def action_cancel(self):
        self.state = 'cancelled'
   
    def action_done(self):
        self.state = 'solved'   
        self.solved_time = fields.Datetime.now()

    def _compute_resolution_time(self):
        for rec in self:
            rec.resolution_time = ""
            if rec.solved_time:
                rec.resolution_time = (rec.solved_time.date() - rec.create_date.date()).days
    
    def unlink(self):
        running_ticket = self.env['hd.ticket'].search(['|',('state', '=', 'in_progress'),('state', '=', 'solved'), ('id', '=', self.id)])
        if len(running_ticket) > 0:
            raise UserError(_("Sorry, %s  ticket can not be deleted") % self.state)
    
    def send_notification_tickets_exceeds_time(self):
        tickets = self.env['hd.ticket'].search([])
        for rec in tickets:
            rec.acvtivity_id.unlink()
            
            if rec.resolution_time > rec.team.max_resolution_time:
                group_helpdesk_team_leader = rec.env.ref('helpdesk_enas_omer.group_helpdesk_team_leader').id
                rec.env.cr.execute(
                    '''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (
                        group_helpdesk_team_leader))

                # schedule activity for user(s) to approve
                for fm in list(filter(lambda x: (
                        rec.env['res.users'].sudo().search([('id', 'in', x)])),
                                      rec.env.cr.fetchall())):
                    vals = {
                        'activity_type_id': rec.env['mail.activity.type'].sudo().search(
                            [('name', 'like', u'To Do')],
                            limit=1).id,
                        'res_id': rec.id,
                        'res_model_id': rec.env['ir.model'].sudo().search(
                            [('model', '=', 'hd.ticket')], limit=1).id,
                        'user_id': fm[0] or 1,
                        'summary': u'Notification Tickets Exceeds Time',
                    }
                    # add lines
                    acvtivity_id = rec.env['mail.activity'].sudo().create(vals)

        return True