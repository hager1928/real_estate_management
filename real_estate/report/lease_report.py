# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta

class LeaseReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_lease_summary'
    _description = 'Lease Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data to report context
        """
        leases = self.env['real_estate.lease'].browse(docids)
        maintenances_info = {}
        maintenances_costs = {}
        for lease in leases:
            maintenance_requests = self.env['maintenance.request'].search([
                ('lease_id', '=', lease.id)
            ])
            maintenances_info[lease.id] =maintenance_requests.mapped('name')
            maintenances_costs[lease.id] = sum(maintenance_requests.mapped('actual_cost'))

        return {
            'doc_ids': docids,
            'doc_model': 'real_estate.lease',
            'docs': leases,
            'maintenance_requests': maintenances_info,
            'maintenance_costs': maintenances_costs,
            'report_date': datetime.now(),
        }

        
                                    