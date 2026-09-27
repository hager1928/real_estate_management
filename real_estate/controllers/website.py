from odoo import http
from odoo.http import request


class RealEstateWebsite(http.Controller):

    # 1. Public Property Listing Page
    @http.route(
        ['/properties', '/properties/page/<int:page>'],
        type='http',
        auth='public',
        website=True,
    )
    def properties_list(self, **kw):
        domain = [('available', '=', True)]

        prop_type = kw.get('type')
        valid_types = {'apartment', 'house', 'villa', 'commercial'}
        if prop_type not in valid_types:
            prop_type = None
        if prop_type:
            domain.append(('property_type', '=', prop_type))

        search_query = (kw.get('q') or '').strip()
        if search_query:
            domain += ['|', ('name', 'ilike', search_query), ('description', 'ilike', search_query)]

        properties = request.env['real_estate.property'].sudo().search(
            domain,
            order='create_date desc, id desc',
        )

        values = {
            'properties': properties,
            'selected_type': prop_type,
            'search_query': search_query,
        }
        return request.render('real_estate.property_list_template', values)

    # 2. Public Property Detail Page
    @http.route(
        '/properties/<model("real_estate.property"):property_id>',
        type='http',
        auth='public',
        website=True,
    )
    def property_detail(self, property_id, **kw):
        return request.render(
            'real_estate.property_detail_template',
            {
                'property': property_id,
            },
        )

    # 3. Tenant Portal Dashboard
    @http.route('/my/leases', type='http', auth='user', website=True)
    def my_leases(self, **kw):
        user = request.env.user
        tenant = (
            request.env['real_estate.tenant']
            .sudo()
            .search([('user_id', '=', user.id)], limit=1)
        )

        leases = (
            request.env['real_estate.lease']
            .sudo()
            .search([('tenant_id', '=', tenant.id)])
            if tenant
            else request.env['real_estate.lease']
        )
        maintenance_requests = (
            request.env['maintenance.request']
            .sudo()
            .search([('tenant_id', '=', tenant.id)])
            if tenant
            else request.env['maintenance.request']
        )

        return request.render(
            'real_estate.tenant_portal_template',
            {
                'tenant': tenant,
                'leases': leases,
                'maintenance_requests': maintenance_requests,
            },
        )