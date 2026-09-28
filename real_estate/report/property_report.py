# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta

class PropertyReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_property_summary'
    _description = 'Property Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override to add custom data to report context
        """
        properties = self.env['real_estate.property'].browse(docids)
        
        # Calculate occupancy rate
        total_properties = len(properties)
        occupied = len(properties.filtered(lambda p: not p.available))
        occupancy_rate = (occupied / total_properties) if total_properties > 0 else 0
        
        # Get maintenance costs for last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        maintenance_costs = {}
        
        for prop in properties:
            costs = self.env['maintenance.request'].search([
                ('property_id', '=', prop.id),
                ('completion_date', '>=', six_months_ago)
            ])
            maintenance_costs[prop.id] = sum(costs.mapped('actual_cost'))
        
        # return {
        #     'doc_ids': docids,
        #     'doc_model': 'real_estate.property',
        #     'docs': properties,
        #     'occupancy_rate': occupancy_rate,
        #     'maintenance_costs': maintenance_costs,
        #     'report_date': datetime.now(),
        # }

    
        # Get total payment amounts
        six_months_ago = datetime.now() - timedelta(days=180)
        total_payment = {}
                
        for prop in properties:
            payments = self.env['lease.payment'].search([
                ('property_id', '=', prop.id),
                ('state', 'in', ['paid', 'reconciled']),
            ])
            total_payment[prop.id] = sum(payments.mapped('amount'))
                            
        return {
                    'doc_ids': docids,
                    'doc_model': 'real_estate.property',
                    'docs': properties,
                    'occupancy_rate': occupancy_rate,
                    'occupied_properties': occupied,
                    'total_payment': total_payment,
                    'report_date': datetime.now(),
                }
        