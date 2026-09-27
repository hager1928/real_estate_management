from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class LeasePayment(models.Model):
    _name = 'lease.payment'
    _description = 'Lease Payment'
    _order = 'due_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Inherited mail classes to allow tracking
    
    name = fields.Char(string='Payment Reference', required=True, copy=False, readonly=False, default='New')
    lease_id = fields.Many2one('real_estate.lease', string='Lease', required=True, ondelete='cascade')
    tenant_id = fields.Many2one(related='lease_id.tenant_id', string='Tenant', store=True)
    property_id = fields.Many2one(related='lease_id.property_id', string='Property', store=True)
    
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    amount = fields.Float(string='Amount Due', required=True, tracking=True)
    late_fee = fields.Float(string='Late Fee', tracking=True)
    late_fee_applied = fields.Boolean(string='Late Fee Applied', default=False)
    # total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], string='Payment Method')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled')
    ], default='draft', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        """Override create to generate payment reference"""
        #if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('lease.payment')
        return super(LeasePayment,self).create(vals)


    def _cron_auto_at_risk_payment(self):
            """Scheduled action - Amount is paid if > 0 """
            payment_amount = self.search([
                ('amount', '>', 0),
                ('state' , '!=','paid')
            ])
            payment_amount.write({'state': 'paid'})
    