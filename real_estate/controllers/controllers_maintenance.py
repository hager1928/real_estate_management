from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal

class RealEstatePortal(CustomerPortal): #inherit odoo's CustomerPortal controller so you can safely hook into the standard portal framework without rewriting user session handling or security login checks.

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()

        maintenances = request.env['maintenance.request'].sudo().search([
            ('assigned_to', '=', request.env.user.id)
        ])
        values.update({
            'maintenances': maintenances,
        })

        return values


    @http.route(['/my/maintenances', '/my/maintenances/page/<int:page>'], type='http', auth='user', website=True)
    # When the user visits /my/maintenances, execute this Python function.
    def portal_my_maintenances(self, page=1, **kw):
        values = self._prepare_portal_layout_values()

        return request.render('real_estate.portal_my_maintenances', values)
