# -*- coding: utf-8 -*-
###########

from openerp import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO



class TicketsPerTeamReportExcelWizard(models.Model):
    _name = 'tickets.per.team.report.excel.wizard'

    team = fields.Many2one('hd.team', string='Team' ,required=True) 
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
        ('cancelled', 'Cancelled'),
        ], string='Status')

    def print_report(self):
        for report in self:
            file_name = _('Tickets Per Team Report.xlsx') 
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet()
            
            format_black = workbook.add_format({'bold': False, 'align': 'center','font_color': 'black', 'bg_color': 'white', 'border': 1})
            format_black_blod = workbook.add_format({'bold': True, 'align': 'center','font_color': 'black', 'bg_color': 'white', 'border': 1})
            
            format_black.set_text_wrap()
            format_black.set_num_format('#,##0.000')
            col = 0
            row = 0
            # title

            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Ticket ID', format_black_blod)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Name', format_black_blod)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Time Submitted', format_black_blod)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Priority', format_black_blod)
            col += 1
            excel_sheet.set_column(col, col, 25)
            excel_sheet.write(row, col, 'Resolution Time', format_black_blod)
            
            if self.state:
                hd_ticket = self.env['hd.ticket'].search([('state', '=', self.state),('team', '=', self.team.id)])
            else:
                hd_ticket = self.env['hd.ticket'].search([('team', '=', self.team.id)]) 

            
           
            for ticket in hd_ticket: 
                row += 1    
                col = 0
                excel_sheet.write(row, col,ticket.ticket_id, format_black)
                col += 1
               
                excel_sheet.write(row, col, ticket.name, format_black)
                col += 1
                if ticket.time_submitted:
                    excel_sheet.write(row, col, ticket.time_submitted.strftime("%Y-%m-%d, %H:%M"), format_black)
                    col += 1
                else:
                    excel_sheet.write(row, col,"", format_black)
                    col += 1
                if ticket.priority:
                    excel_sheet.write(row, col,dict(ticket._fields['priority']._description_selection(self.env)).get(ticket.priority), format_black)
                    col += 1
                else:
                    excel_sheet.write(row, col,"", format_black)
                    col += 1
                excel_sheet.write(row, col, ticket.resolution_time, format_black)
                col += 1  

        
        workbook.close()

        file_download = base64.b64encode(fp.getvalue())
        wizardmodel = self.env['tickets.per.team.report.excel']
        res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
        
        return {
            'name': 'Files to Download',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tickets.per.team.report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id.id,
        }


class TicketsPerTeamReportExcel(models.TransientModel):
    _name = 'tickets.per.team.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)
