# import odoo
# from odoo.addons.hw_drivers import http


# from odoo import http, fields
# from odoo.http import request
# import json
# from functools import wraps

# class RealEstateAPI(http.Controller):    
#     @http.route('/api/tenants/<int:tenant_id>', type='http', auth='public', methods=['POST'], csrf=False)
#     def update_tenant(self, tenant_id):
#         tenant_obj = request.env['real_estate.tenant'].sudo().browse(tenant_id)
#         # print(tenant_obj.name)
#         if not tenant_obj.exists():
#             return request.make_json_response(
#                 {'status': 'error', 
#                  'message': 'Tenant not found'}, 
#                  status=404
#                  )
        
#         params = request.httprequest.get_json(silent=True)

#         tenant_obj.write(params)
#         return request.make_json_response({'status': 'success', 
#                                            'tenant_id': tenant_obj.id}
#                                            )
