# -*- coding: utf-8 -*-

import io
import base64
import xlsxwriter

from odoo import models, fields


class MaintenanceWizard(models.TransientModel):
    _name = 'maintenance.wizard'
    _description = 'Maintenance Report Wizard'

    # WIZARD FIELDS

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True
    )

    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], string='Issue Type')

    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], string='Urgency')

    excel_file = fields.Binary(
        string='Excel File',
        readonly=True
    )

    excel_filename = fields.Char(
        string='Filename',
        readonly=True
    )

    # GENERATE REPORT

    def action_generate_report(self):

        self.ensure_one()

        # 1. BUILD SEARCH DOMAIN


        domain = [
            ('property_id', '=', self.property_id.id),
            ('state', '=', 'submitted'),
        ]

        # If user selected an issue type
        if self.issue_type:
            domain.append(('issue_type', '=', self.issue_type))

        # If user selected urgency
        if self.urgency:
            domain.append(('urgency', '=', self.urgency))

        # 2. GET MAINTENANCE REQUESTS

        maintenance_requests = self.env['maintenance.request'].search(domain)

        # 3. CALCULATE TOTALS

        issue_totals = {
            'plumbing': 0.0,
            'air_condition': 0.0,
            'electrical': 0.0,
            'appliance': 0.0,
            'other': 0.0,
        }

        for request in maintenance_requests:

            issue_type = request.issue_type

            if issue_type in issue_totals:
                issue_totals[issue_type] += (
                    request.actual_cost or 0.0
                )

        # Total maintenance cost
        total_maintenance_cost = sum(
            issue_totals.values()
        )

        # 4. CREATE EXCEL FILE

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(
            output,
            {'in_memory': True}
        )

        worksheet = workbook.add_worksheet(
            'Maintenance Report'
        )

        # 5. COLORS / FORMATS

        purple = '#5B2C83'

        # Light purple
        light_purple = '#EADCF8'

        # White
        white = '#FFFFFF'

        # Gray
        gray = '#F2F2F2'

        # Green
        green = '#E2F0D9'

        # -----------------------------------------------------
        # TITLE FORMAT
        # -----------------------------------------------------

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': white,
            'bg_color': purple,
            'align': 'left',
            'valign': 'vcenter',
        })

        # SECTION FORMAT

        section_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': white,
            'bg_color': purple,
            'align': 'left',
            'valign': 'vcenter',
        })

        # FILTER HEADER

        filter_header_format = workbook.add_format({
            'bold': True,
            'bg_color': gray,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })

        # FILTER VALUE

        filter_value_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })
        # TABLE HEADER

        table_header_format = workbook.add_format({
            'bold': True,
            'bg_color': light_purple,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter',
        })

        # NORMAL DATA

        data_format = workbook.add_format({
            'border': 1,
        })

        # CURRENCY

        currency_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'align': 'right',
        })

        # TOTAL FORMAT
    
        total_label_format = workbook.add_format({
            'bold': True,
            'font_color': white,
            'bg_color': purple,
            'border': 1,
        })

        total_value_format = workbook.add_format({
            'bold': True,
            'font_color': white,
            'bg_color': purple,
            'border': 1,
            'num_format': '#,##0.00',
            'align': 'right',
        })

        # 6. COLUMN WIDTHS

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 5)
        worksheet.set_column('E:E', 20)

        # 7. TITLE

        row = 0

        worksheet.merge_range(
            row,
            0,
            row,
            4,
            'Maintenance Report',
            title_format
        )

        worksheet.set_row(row, 28)

        row += 1

        # 8. FILTER HEADERS

        worksheet.write(
            row,
            0,
            'property',
            filter_header_format
        )

        worksheet.write(
            row,
            1,
            'issue type',
            filter_header_format
        )

        worksheet.write(
            row,
            2,
            'urgency',
            filter_header_format
        )

        # Leave D and E empty
        worksheet.write(
            row,
            3,
            '',
            filter_header_format
        )

        worksheet.write(
            row,
            4,
            '',
            filter_header_format
        )

        row += 1

        # 9. FILTER VALUES

        worksheet.write(
            row,
            0,
            self.property_id.name or '',
            filter_value_format
        )

        # Issue type label
        issue_type_label = 'All'

        if self.issue_type:
            issue_type_label = dict(
                self._fields['issue_type'].selection
            ).get(
                self.issue_type,
                self.issue_type
            )

        worksheet.write(
            row,
            1,
            issue_type_label,
            filter_value_format
        )

        # Urgency label
        urgency_label = 'All'

        if self.urgency:
            urgency_label = dict(
                self._fields['urgency'].selection
            ).get(
                self.urgency,
                self.urgency
            )

        worksheet.write(
            row,
            2,
            urgency_label,
            filter_value_format
        )

        worksheet.write(
            row,
            3,
            '',
            filter_value_format
        )

        worksheet.write(
            row,
            4,
            '',
            filter_value_format
        )

        row += 2

        # 10. SUMMARY TITLE

        worksheet.merge_range(
            row,
            0,
            row,
            4,
            'Summary Statistics',
            section_format
        )

        worksheet.set_row(row, 22)

        row += 1

        # 11. SUMMARY HEADERS

        worksheet.write(
            row,
            0,
            'issue type',
            table_header_format
        )

        worksheet.write(
            row,
            1,
            'total cost',
            table_header_format
        )

        # Merge the remaining cells
        worksheet.merge_range(
            row,
            2,
            row,
            4,
            '',
            table_header_format
        )

        row += 1

        # 12. ISSUE TYPE TOTALS

        issue_types = [
            ('plumbing', 'plumbing'),
            ('air_condition', 'air condition'),
            ('electrical', 'electrical'),
            ('appliance', 'appliance'),
            ('other', 'other'),
        ]

        for issue_key, issue_label in issue_types:

            # If user selected one issue type,
            # only show that issue type.
            if (
                self.issue_type
                and self.issue_type != issue_key
            ):
                continue

            worksheet.write(
                row,
                0,
                issue_label,
                data_format
            )

            worksheet.write(
                row,
                1,
                issue_totals[issue_key],
                currency_format
            )

            worksheet.merge_range(
                row,
                2,
                row,
                4,
                '',
                data_format
            )

            row += 1

        # 13. TOTAL MAINTENANCE COST
    

        worksheet.write(
            row,
            0,
            'total maintenance cost',
            total_label_format
        )

        worksheet.write(
            row,
            1,
            total_maintenance_cost,
            total_value_format
        )

        worksheet.merge_range(
            row,
            2,
            row,
            4,
            '',
            total_label_format
        )

        row += 2

        # 14. OPTIONAL EXTRA SUMMARY

        worksheet.merge_range(
            row,
            0,
            row,
            4,
            'No. of Maintenances ',
            section_format
        )

        row += 1

        # Number of maintenance requests
        worksheet.write(
            row,
            0,
            'number of maintenances',
            filter_header_format
        )

        worksheet.write(
            row,
            1,
            len(maintenance_requests),
            data_format
        )

        worksheet.merge_range(row,2,row,4,'',data_format)
        row += 1

        # 15. CLOSE WORKBOOK

        workbook.close()

        # 16. SAVE FILE TO WIZARD

        output.seek(0)

        self.excel_file = base64.b64encode(
            output.read()
        )

        self.excel_filename = (
            f'Maintenance_Report_'
            f'{self.property_id.name}.xlsx'
        )

        # 17. RETURN WIZARD

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }