from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name',required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(compute='_compute_notes',string='Notes')
    active = fields.Boolean(string='Active', default=True) 
    lead_id = fields.Many2one('crm.lead' ,string ='CRM Lead' )  #inherit from crm
    age_category = fields.Selection([
            ('a','21 - 40'),
            ('b','41 - 60'),
            ('c','over 60'),
        ], string='Age Category')
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    property_type = fields.Selection([
            ('apartment', 'Apartment'),
            ('house', 'House'),
            ('villa', 'Villa'),
            ('commercial', 'Commercial'),
        ], string='Property Type', required=True) 
    company_type = fields.Selection(string='Company Type',
            selection=[('person', 'Individual'), ('company', 'Company')],default='person', required=True)
    
    def update_notes(self):
        """You can update notes here"""
        for record in self:
            record.write({'notes': record.name})

    def get_lead_website(self):
            """Lead website here"""
            for record in self:
                if record.lead_id.email_from:
                    record.write({'notes': record.lead_id.email_from})
                else:
                    record.write({'notes': record.lead_id.website})
            return None

    
    @api.depends('name')
    def _compute_notes(self):
        for record in self:
             record.notes='Hello %s' %record.name

    # === VALIDATION ===
    @api.constrains('date_of_birth')
    def _check_age(self):
        """Ensure BOD is ok"""
        for record in self:
                if record.date_of_birth >= fields.Date.today():
                    raise ValidationError("Age is not suitable")

#     Task 2 – Tenant Email Uniqueness
# Add an SQL constraint in (tenant py) to ensure that the tenant's email address is unique.
# Prevent creating or updating a tenant with an email address that already exists.

    _sql_constraints = [
        ('email_unique', 'UNIQUE(email)', 'Email must be unique! This email is already registered.')
    ]

    def create_portal_user(self):
        portal_group = self.env.ref('base.group_portal')

        for tenant in self:

            user = self.env['res.users'].create({
                'name': tenant.name,
                'login': tenant.email,
                'groups_id': [(4, portal_group.id)],
            })

            tenant.user_id = user.id

