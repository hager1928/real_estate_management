from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class RealEstateAgentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'property_count' in counters:
            property_count = request.env['real_estate.property'].search_count([
                ('agent_id', '=', request.env.user.id)
            ])
            values['property_count'] = property_count
        return values

    @http.route(['/my/agent/properties', '/my/agent/properties/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_agent_properties(self, page=1, sortby=None, **kw):
        Property = request.env['real_estate.property']
        
        domain = [('agent_id', '=', request.env.user.id)]
        
        # Count for pager
        property_count = Property.search_count(domain)
        
        # Pager configuration
        pager = portal_pager(
            url="/my/agent/properties",
            total=property_count,
            page=page,
            step=10
        )
        
        properties = Property.search(domain, limit=10, offset=pager['offset'])
        
        values = {
            'user_id': request.env.user,
            'properties': properties,
            'page_name': 'agent_property',
            'pager': pager,
            'default_url': '/my/agent/properties',
        }
        return request.render("real_estate.portal_my_agent_properties", values)
