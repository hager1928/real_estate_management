from odoo import models, fields,api
from odoo.exceptions import UserError
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=0) 

    def get_lead_name(self):
        """Lead Name here"""
        for record in self:
            record.write({'description': record.name})

    def write(self, vals):        
        # if 'active' in vals and vals['active'] == True:
        # print("name:", vals.get('name'))
        # vals['description'] = vals.get('name')
        if vals.get('expected_revenue') > 5000:
            vals['description'] = f"Expected Revenue: {vals['expected_revenue']}"
        else:
            raise UserError("Expected Revenue must be greater than 5000")
        # vals['description'] = self.name
        return super(CrmLead, self).write(vals)

# loop crm , property_type exist? ===>, create new tenant At 1 am
    @api.model
    def _cron_auto_create_tenant(self):
        """Scheduled action - cron_auto_create_tenant"""
        leads= self.search([('property_type','!=',False)])
        for lead in leads:
           self.env['real_estate.tenant'].create({
                'name':lead.name,
                'property_type':lead.property_type,
                'lead_id':lead.id
           })