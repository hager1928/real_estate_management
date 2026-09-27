from odoo import models, fields, api
from datetime import timedelta
class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Property Maintenance Request'
    #_inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(default='New',copy=False)
    lease_id = fields.Many2one('real_estate.lease')
    tenant_id = fields.Many2one(related='lease_id.tenant_id', store=True)
    property_id = fields.Many2one(related='lease_id.property_id', store=True)

    issue_type = fields.Selection([
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('air_condition', 'Air Condition'),
        ('appliance', 'Appliance'),
        ('other', 'Other')
    ], required=True)
    description = fields.Text(required=True, tracking=True)
    urgency = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], default='medium', required=True)
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    scheduled_date = fields.Date()
    completion_date = fields.Date()
    actual_cost = fields.Float()
    preferred_date = fields.Date()
    tenant_phone = fields.Char()
    state=fields.Selection([
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled'),
    ], default='submitted', required=True)

# if emergency ,schedule date is tomorrow
    def _cron_auto_scheduled_date(self):
        """Scheduled action - if emergency ,schedule date tomorrow """
        today = fields.Date.today()
        urgency = self.search([
            ('urgency', '=', 'emergency'),
        ])
        if not urgency.scheduled_date:
            urgency.write({'scheduled_date': today+timedelta(days=1)})

#email for assigned to , when prefered date is tomrrow
    def email_template_maintenance_upcoming(self):
            template_xml_id = 'real_estate.email_template_maintenance_upcoming'
            if not template_xml_id:
                return
                
            template = self.env.ref(template_xml_id, raise_if_not_found=False)
            if not template:
                return
    
            for record in self:
                if not record.assigned_to:
                    record.message_post(body="Could not send reminder: No assigned user.")
                    continue
                template.send_mail(record.id, force_send=True)

    def _cron_auto_next_maintenance_reminder_date(self):
                """Scheduled action - if next maintenance date tommorrow , send email reminder """
                today = fields.Date.today()
                reminder = self.search([
                     ('scheduled_date', '=', today + timedelta(days=1)),
                 ])
                for remind in reminder:
                    remind.email_template_maintenance_upcoming()