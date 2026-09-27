from odoo import models, fields, api

class TenantWizard(models.TransientModel):
    _name = 'real_estate.tenant.wizard'
    _description = 'Real Estate Tenant Wizard'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    # city = fields.Char(string='City')
    # date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    # date_of_birth = fields.Date(string='Date of Birth')
    # notes = fields.Text(string='Notes')
    # active = fields.Boolean(string='Active', default=True) 
    lead_id = fields.Many2one('crm.lead' ,string ='CRM Lead' )
    # age_category = fields.Selection([
    #         ('a','21 - 40'),
    #         ('b','41 - 60'),
    #         ('c','over 60'),
    #     ], string='Age Category')
    # user_id = fields.Many2one('res.users', string='Related User', index=True)


    def action_submit_request(self):
            """Create Tenant and notify manager"""
            self.ensure_one()
            
            # 1. Create maintenance.request record
            tenant = self.env['real_estate.tenant'].sudo().create({
                'name': self.name,
                'email': self.email,
                'phone': self.phone,
                'mobile': self.mobile,
                'lead_id':self.lead_id.id,
            })
            
            # 2. Send notification to property manager (Agent)
            # if self.property_id.agent_id:
            #     maintenance_request.activity_schedule(
            #         'mail.mail_activity_data_todo',
            #         user_id=self.property_id.agent_id.id,
            #         summary=f"New {self.issue_type.capitalize()} Maintenance Request",
            #         note=f"Urgency: {self.urgency}\nDescription: {self.description}"
            #     )
            
            # 3. Return action to close wizard and show confirmation
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': 'Request Submitted',
            #         'message': 'Your Tenant request has been submitted successfully and the manager has been notified.',
            #         'type': 'success',
            #         'sticky': False,
            #         'next': {'type': 'ir.actions.act_window_close'},
            #     },
            # }
                       # 4. Opening a Created Record
            return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.tenant',
            'res_id': tenant.id,
            'views': [(False, 'form')],
            'target': 'current',
        }
