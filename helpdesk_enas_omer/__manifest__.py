# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Helpdesk',
    'version' : '0.1', 
    'description' : """
==================================

Main Features
-------------
*  allows a customer to
submit and review their ticket status in a clear and concise manner. 

""",
    'depends': [
        'base','mail',
    ],
    'data': [
        'security/help_desk_sec.xml',
        'security/ir.model.access.csv',
        'data/cron.xml',  
        'data/sequence.xml',
        'views/teams.xml',
        'views/ticket.xml',
        'views/tag.xml',
        'reports/tickets_per_team.xml',
        'reports/tickets_per_team_wizard.xml',
        'reports/tickets_per_team_report_excel.xml', 

    ],


    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
