from odoo import models, fields, api
from odoo.exceptions import UserError

class Property(models.Model):
    _name = 'real_estate.property'        #how it is stored in db (no . in db , it turns it to _ )
    _description = 'Real Estate Property'  #for what appears in technical Menu for ex. (it is human readable)

    name = fields.Char(string='Property Name', required=True, index=True)
    image_1920 = fields.Image(string='Property Photo', max_width=1920, max_height=1920)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True) 
    deposit = fields.Float(string='Deposit Amount')      
    bedrooms = fields.Integer(string='Bedrooms')
    available = fields.Boolean(string='Available', default=True ,default=lambda self:self.env.user, index=True)    
    agent_id = fields.Many2one('res.users', string='Sales Person')
    property_type = fields.Selection([
        ('apartment', 'Apartment'),      #1st is what appears in db, 2nd is how it would appear to users
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)
    lease_ids = fields.One2many(
        'real_estate.lease','property_id',
        string='Leases',
        # required=True,
        # ondelete='cascade',  # If property deleted, delete lease too
        # index=True
    )
    maintenance_ids = fields.One2many(
        'maintenance.request','property_id',
        string='Maintenance',
        # required=True,
        # ondelete='cascade',  # If property deleted, delete lease too
        # index=True
    )
    payment_ids = fields.One2many('lease.payment', 'property_id', string='Payments')

    # tenant_ids = fields.One2many(
    #         'real_estate.tenant','property_id',
    #         string='Tenants',
    #         # required=True,
    #         # ondelete='cascade',  # If property deleted, delete lease too
    #         # index=True
    #     )
    
    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})
    
    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})

    def update_description(self):
        """You can write Description here"""
        for record in self:
            record.write({'description': "update ur Description here"})

    def increase_deposit(self):
            """Add Deposit 1000"""
            for record in self:
                record.write({'deposit': record.deposit + 1000})

    def add_bedroom(self):
                """Add 1 bedrooom"""
                for record in self:
                    record.write({'bedrooms': record.bedrooms + 1})

    def make_property_as_villa(self):
            """change to villa"""
            for record in self:
                if record.available:
                    record.write({'property_type':"villa"})

    def get_agent_name(self):
        """Agent Name here"""
        for record in self:
            record.write({'description': record.agent_id.name})
            #record.agent_id.name =====> pk, agent_id=fk
            #we tried login also instead of name

    #if not available , can not edit bedrooms
        # def write(self, vals):        
        #     if vals.get('available') == True and 'bedrooms' in vals:
        #         #raise UserError("You can not Edit Bedrooms for Non Available Property ")  
        #         pass
        #     else:
        #         raise UserError("You can not Edit Bedrooms for non Available Property ")
        #     return super(Property, self).write(vals)

    # def write(self, vals):
    #     if 'bedrooms' in vals:
    #         for record in self:
    #             if not record.available:
    #                 raise UserError("You cannot edit the number of bedrooms when the property is not available!")
    #     return super().write(vals)

#for the smart button action_open_lease
    def action_open_lease(self):
        self.ensure_one()
        return {
            'name': 'Leases',
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.lease', 
            'domain': [('property_id', '=', self.id)], 
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_open_maintenance(self):
            self.ensure_one()
            return {
                'name': 'Maintenance',
                'type': 'ir.actions.act_window',
                'res_model': 'maintenance.request', 
                'domain': [('property_id', '=', self.id)], 
                'view_mode': 'list,form',
                'target': 'current',
            }

    def action_print_property_summary(self):
        """Print Property Summary Report"""
        self.ensure_one()
        return self.env.ref('real_estate.action_report_property_summary').report_action(self)

    def action_export_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/real_estate/property/excel_export/{self.id}',
            'target': 'self',
        }



