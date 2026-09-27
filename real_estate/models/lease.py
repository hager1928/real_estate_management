from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
        
    name = fields.Char(string='Lease Reference', required=True, default='New')
    #name = fields.Char(string='Lease Reference', required=True, readonly=True, default='New')
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',  # If property deleted, delete lease too
        index=True
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True
    )
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)
    user_id = fields.Many2one('res.users', string='User', index=True)
    maintenance_ids = fields.One2many(
            'maintenance.request','lease_id',
            string='Maintenance',
            # required=True,
            # ondelete='cascade',  # If property deleted, delete lease too
            # index=True
        )
    
    duration_months = fields.Integer(string='Duration (Months)', compute='_compute_duration', store=True)
    is_active = fields.Boolean(string='Currently Active', compute='_compute_is_active')
    total_cost = fields.Float(compute='_compute_total_cost', string='Maintenance Total Cost')

    maintenance_plumbing_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Plumbing Actual Costs')
    maintenance_electrical_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Electrical Actual Costs')
    maintenance_air_condition_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Air Condition Actual Costs')
    maintenance_appliance_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Appliance Actual Costs')
    maintenance_other_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Other Actual Costs')

    cash = fields.Float(string='Cash', compute='_compute_total_amount', store=True)
    check = fields.Float(string='Check', compute='_compute_total_amount', store=True)
    bank_transfer = fields.Float(string='Bank Transfer', compute='_compute_total_amount', store=True)
    credit_card = fields.Float(string='Credit Card', compute='_compute_total_amount', store=True)
    other = fields.Float(string='Other', compute='_compute_total_amount', store=True)
    payment_ids = fields.One2many('lease.payment', 'lease_id', string='Payment')
    #(oof to search )field_name_ids = fields.One2many('comodel_name', 'inverse_field_name', string='field_name')
    next_payment_date = fields.Date(string='Last Reminder Sent')
    last_reminder_sent = fields.Date(string='Last Reminder Sent', readonly=True)

    def convert_to_active(self):
            """Convert State To Active """
            if not self.env.user.has_group('real_estate.group_tenant_manager'):               
                raise UserError("You can not Edit , you Need to be a Manager ")
            for record in self:
                record.write({'state': 'active'})
            

    def back_to_draft(self):
                """Convert State To Draft """
                for record in self:
                    record.write({'state': 'draft'})

    def convert_to_risk(self):
                    """Convert State To Risk """
                    for record in self:
                        record.write({'state': 'at_risk'})

    def convert_to_expired(self):
                    """Convert State To Expired """
                    for record in self:
                        record.write({'state': 'expired'})

    def cancelled(self):
                        """Convert State To Cancelled """
                        for record in self:
                            record.write({'state': 'cancelled'})
    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)


    def copy(self, default=None):
            default = dict(default or {})
            # raise UserError("you can not Duplicate Lease ")
            # default['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
            return super().copy(default)

    # def write(self, vals):        
    #     if not self.env.user.has_group('real_estate.group_lease_manager'):               
    #         raise UserError("You can not Edit , you Need to be a Manager ")
    #     return super(Lease, self).write(vals)

    def unlink(self):
            """Override create to generate lease reference"""
            if not self.env.user.has_group('real_estate.group_lease_manager'):               
                raise UserError("You can Not Delete , you Need to be a Manager ")
            return super(Lease, self).unlink()

    def action_open_maintenance(self):
        self.ensure_one()
        return {
            'name': 'Maintenance',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request', 
            'domain': [('lease_id', '=', self.id)], 
            'view_mode': 'list,form',
            'target': 'current',
        }

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        """Calculate lease duration in months"""
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration_months = int(delta.days / 30)
            else:
                record.duration_months = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Set default price when property is selected and validate availability"""
        if self.property_id and not self.property_id.available:
            raise ValidationError("The selected property is not available.")
        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price

    @api.depends('maintenance_ids.actual_cost')
    def _compute_total_cost(self):
        for lease in self:
            # 1
            lease.total_cost = sum(maintenance.actual_cost for maintenance in lease.maintenance_ids)

            # 2
            # lease.total_cost = 0
            # total_cost = 0
            # for maintenance in lease.maintenance_ids:
            #     if maintenance.actual_cost:
            #         total_cost += maintenance.actual_cost
            # lease.total_cost = total_cost   

            # 3
            # lease_maintenance_ids = self.env['maintenance.request'].search([('lease_id', '=', lease.id)])  
            # for maintenance in lease_maintenance_ids:
            #     if maintenance.actual_cost:
            #         lease.total_cost += maintenance.actual_cost


    @api.depends(
        'maintenance_ids.actual_cost',
        'maintenance_ids.issue_type'
    )
    def _compute_maintenance_types_costs(self):
        for lease in self:
            lease.total_cost = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
            )

            lease.maintenance_plumbing_costs = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
                if maintenance.issue_type == 'plumbing'
            )

            lease.maintenance_electrical_costs = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
                if maintenance.issue_type == 'electrical'
            )

            lease.maintenance_air_condition_costs = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
                if maintenance.issue_type == 'air_condition'
            )

            lease.maintenance_appliance_costs = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
                if maintenance.issue_type == 'appliance'
            )

            lease.maintenance_other_costs = sum(
                maintenance.actual_cost
                for maintenance in lease.maintenance_ids
                if maintenance.issue_type == 'other'
            )

    # @api.depends('maintenance_ids.actual_cost', 'maintenance_ids.issue_type')
    # def _compute_maintenance_costs(self):
    #     for record in self:
    #         costs = {
    #             type_name: sum(
    #                 record.maintenance_ids.filtered(
    #                     lambda maintenance: maintenance.issue_type == type_name
    #                 ).mapped('actual_cost')
    #             )
    #             for type_name in ['plumbing', 'electrical', 'air_condition', 'appliance', 'other']
    #         }

    #         record.plumbing_cost = costs['plumbing']
    #         record.electrical_cost = costs['electrical']
    #         record.air_condition_cost = costs['air_condition']
    #         record.appliance_cost = costs['appliance']
    #         record.other_cost = costs['other']

    @api.depends('payment_ids.amount', 'payment_ids.payment_method')
    def _compute_total_amount(self):
        for record in self:
            costs = {
                type_name: sum(
                    record.payment_ids.filtered(
                        lambda lease: lease.payment_method == type_name    #lambda is shortcut for tiny func [def is_cash(lease):return lease.payment_method == 'cash']
                    ).mapped('amount')
                )
                for type_name in ['cash', 'check', 'bank_transfer', 'credit_card', 'other']
            }
    
            record.cash = costs['cash']
            record.check = costs['check']
            record.bank_transfer = costs['bank_transfer']
            record.credit_card = costs['credit_card']
            record.other = costs['other']

    # @api.depends('payments_ids.amount', 'payments_ids.payment_method')
    # def _compute_payment_details(self):
    #     for lease in self:
    #       #(dictionary comprehension)
    #         payments_data = {  
    #             f'{method}_details': sum(lease.payments_ids.filtered(lambda r: r.payment_method == method).mapped('amount'))
    #             for method in ['cash', 'check', 'bank_transfer', 'credit_card', 'other']
    #         }
    #         lease.update(payments_data)

    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})

# === VALIDATION ===
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be after start date")

    # _sql_constraints = [
    #     ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.')
    # ]
#     Task 1 – Lease Deposit Validation
# Add a constraint in(lease py) to ensure that the deposit amount does not exceed the Monthly rent.
#  If the deposit is greater than the amount, display a validation error message.
    @api.constrains('deposit_paid', 'monthly_rent')
    def _check_deposit(self):
            """Ensure Deposit is less than monthly rent"""
            for record in self:
                # if record.deposit_paid and record.monthly_rent:
                    if record.monthly_rent <= record.deposit_paid:
                        raise ValidationError("Deposit can not be greater than Or Equal to Monthly Rent")
    #CHECK SQL constraints
    # _sql_constraints = [
    #         ('check_deposit', 'CHECK(deposit_paid < monthly_rent)', 'Deposit can not be greater than Or Equal to Monthly Rent')
    #     ]

    # How to Remove a SQL Constraint from the Database
    # To completely remove the unique constraint, you need to run a quick SQL command directly against your database using your terminal (psql) or a database tool like pgAdmin or DBeaver.
    # Step 1: Connect to your database
    # psql -d test17 (in cmd)
    # Step 2: Drop the constraint
    # Remember that Odoo automatically prefixes your custom constraint name with the table name (real_estate_tenant_ + email_unique). Run this SQL command:
    # SQL:
    # ALTER TABLE real_estate_tenant DROP CONSTRAINT real_estate_tenant_email_unique;
    # If it succeeds, PostgreSQL will return ALTER TABLE.


    def send_reminder_email(self):
        template_xml_id = 'real_estate.email_template_payment_upcoming'
        if not template_xml_id:
            return
            
        template = self.env.ref(template_xml_id, raise_if_not_found=False)
        if not template:
            return

        for lease in self:
            if not lease.tenant_id.email:
                lease.message_post(body="Could not send reminder: Tenant has no email.")
                continue
            template.send_mail(lease.id, force_send=True)
            lease.last_reminder_sent = fields.Date.today()

#if next payment date tommorrow , send email reminder
    def _cron_auto_next_payment_reminder_date(self):
            """Scheduled action - if next payment date tommorrow , send email reminder """
            today = fields.Date.today()
            reminder = self.search([
                 ('end_date', '=', today + timedelta(days=1)),
             ])
            for remind in reminder:
                remind.send_reminder_email()
