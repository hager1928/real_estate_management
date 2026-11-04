import odoo
from odoo import http, fields
from odoo.http import request
import json
from functools import wraps

def valid_response(data=None, message='Success', status=200):
    return request.make_json_response({
        'status': 'success',
        'message': message,
        'data': data
    }, status=status)


def invalid_response(message='Bad Request', status=400, data=None):
    return request.make_json_response({
        'status': 'error',
        'message': message,
        'data': data
    }, status=status)

TOKEN = 'cacb064fd72c08b445959768'
class RealEstateAPI(http.Controller):
    @http.route('/api/properties/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        #TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs
            print(request.env.user.name)
            if not request.env.user.has_group('real_estate.group_property_manager'):
                return {
                    'status': 'error',
                    'message': 'You do not have permission to create properties'
                }
            # Validate required fields
            if not params.get('name') or not params.get('price'):
                return {
                    'status': 'error',
                    'message': 'Name and price are required'
                }
            
            # Create property
            property_obj = request.env['real_estate.property'].sudo().create({
                'name': params.get('name'),
                'price': params.get('price'),
                'bedrooms': params.get('bedrooms', 0),
                'property_type': params.get('property_type', 'house'),
                'external_id': params.get('external_id'),
            })
            
            return {
                'status': 'success',
                'message': 'Property created successfully',
                'data': {
                    'property_id': property_obj.id,
                    'name': property_obj.name,
                    'external_id': property_obj.external_id
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


    @http.route('/api/tenants/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_tenant(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs
            print(request.env.user.name)
            # if not request.env.user.has_group('real_estate.group_tenant_manager'):
            #     return {
            #         'status': 'error',
            #         'message': 'You do not have permission to create tenants'
            #     }
            # Validate required fields
            # if not params.get('name') or not params.get('email') or not params.get('tenant_api'):
            #     return {
            #         'status': 'error',
            #         'message': 'Name, email, and tenant API are required'
            #     }
            
            # # Create tenant
            # tenant_obj = request.env['real_estate.tenant'].sudo().browse(params.get('tenant_id')) or request.env['real_estate.tenant'].sudo().create({
            #     'name': params.get('name'),
            #     'email': params.get('email'),
            #     'tenant_api': params.get('tenant_api')
            # })
            #update tenant phone number
            tenant_obj = request.env['real_estate.tenant'].sudo().browse(params.get('tenant_id'))# try not exists
            # tenant_obj = request.env['real_estate.tenant'].sudo().search([('id', '=', params.get('tenant_id'))])
            if not tenant_obj.active:
                return {
                        'status': 'failed',
                        'message': 'Tenant not active ',
                    }
            tenant_obj.sudo().write({
                'phone': params.get('phone')
            })

            # return {
            #             'status': 'success',
            #             'message': 'Tenant updated successfully',
            #             'data': {
            #                 'tenant_id': tenant_obj.id,
            #                 'phone': tenant_obj.phone,
            #             }
            #         }
                        
            #return created tenant details
            return {
                'status': 'success',
                'message': 'Tenant created successfully',
                'data': {
                    'tenant_id': tenant_obj.id,
                    'name': tenant_obj.name,
                    'email': tenant_obj.email,
                    'phone': tenant_obj.phone,
                    'tenant_api': tenant_obj.tenant_api
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/crm/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_crm_record(self, **kwargs):
        try:
            params = kwargs
            print(request.env.user.name)
            
            # Validate required fields
            if not params.get('name') or not params.get('email_from') or not params.get('phone') or not params.get('property_type'):
                return {
                    'status': 'error',
                    'message': 'All fields are required'
                }
            
            # Create crm
            crm_obj = request.env['crm.lead'].sudo().create({
                'name': params.get('name'),
                'email_from': params.get('email_from'),
                'phone': params.get('phone'),
                'property_type': params.get('property_type'),
                'expected_revenue': params.get('expected_revenue', 0)
            })
            
            return {
                'status': 'success',
                'message': 'CRM record created successfully',
                'data': {
                    'crm_id': crm_obj.id,
                    'name': crm_obj.name,
                    'email_from': crm_obj.email_from,
                    'phone': crm_obj.phone,
                    'property_type': params.get('property_type'),
                    'expected_revenue': params.get('expected_revenue', 0)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/tenants/<int:tenant_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def update_tenant(self, tenant_id):
        tenant_obj = request.env['real_estate.tenant'].sudo().browse(tenant_id)
        # print(tenant_obj.name)
        if not tenant_obj.exists():
            return request.make_json_response(
                {'status': 'error', 
                 'message': 'Tenant not found'}, 
                 status=404
                 )
        
        params = request.httprequest.get_json(silent=True)

        tenant_obj.write(params)
        return request.make_json_response({'status': 'success', 
                                           'tenant_id': tenant_obj.id}
                                           )

    @http.route('/api/property/<int:property_id>', type='http', auth='public', methods=['POST'], csrf=False)
    def update_property(self, property_id):
        property_obj = request.env['real_estate.property'].sudo().browse(property_id)
        # print(property_obj.name)
        if not property_obj.exists():
            return request.make_json_response(
                {'status': 'error', 
                    'message': 'Property not found'}, 
                    status=404
                    )
        
        params = request.httprequest.get_json(silent=True)

        property_obj.write(params)
        return request.make_json_response({'status': 'success', 
                                            'property_id': property_obj.id}
                                            )

    @http.route('/api/list_leases', type='http', auth='public', methods=['GET'], csrf=False)
    def list_leases(self):
        date_from = request.httprequest.args.get('date_from')
        date_to = request.httprequest.args.get('date_to')
        if not date_from or not date_to:
            return request.make_json_response(
                {'status': 'error', 
                 'message': 'date_from and date_to are required'}, 
                 status=400
            )

        try:
            print('date_from 1:', date_from)
            date_from = fields.Date.to_date(date_from)
            date_to = fields.Date.to_date(date_to)
            print('date_from 2:', date_from)
        
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )

        if date_from > date_to:
            return request.make_response(
                json.dumps({'status': 'error', 
                            'message': 'date_from must be before date_to'}),
                headers={'Content-Type': 'application/json'}
            )

        leases = request.env['real_estate.lease'].sudo().search([
            ('start_date', '<=', date_to),
            ('end_date', '>=', date_from),
        ])
        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': [{
                    'id': lease.id,
                    'name': lease.name,
                    'tenant': lease.tenant_id.name,
                    'property': lease.property_id.name,
                    'start_date': fields.Date.to_string(lease.start_date),
                    'end_date': fields.Date.to_string(lease.end_date),
                    'monthly_rent': lease.monthly_rent,
                    'state': lease.state,
                } for lease in leases],
            }),
            headers={'Content-Type': 'application/json'}
        )

    # @http.route('/api/list_leases', type='http', auth='public', methods=['GET'], csrf=False)
    # def list_leases(self):
    #     date_from = request.httprequest.args.get('date_from')
    #     date_to = request.httprequest.args.get('date_to')
    #     tenant_id = request.httprequest.args.get('tenant_id')
        
    #     if not date_from or not date_to:
    #         return request.make_json_response(
    #             {'status': 'error', 
    #              'message': 'date_from and date_to are required'}, 
    #              status=400
    #         )

    #     try:
    #         date_from = fields.Date.to_date(date_from)
    #         date_to = fields.Date.to_date(date_to)
    #         if tenant_id:
    #             tenant_id = int(tenant_id)
    #     except (ValueError, TypeError) as e:
    #         return request.make_json_response(
    #             {'status': 'error', 'message': f'Invalid parameter value: {str(e)}'},
    #             status=400
    #         )

    #     if date_from > date_to:
    #         return request.make_json_response(
    #             {'status': 'error', 
    #              'message': 'date_from must be before date_to'},
    #             status=400
    #         )

    #     domain = [
    #         ('start_date', '<=', date_to),
    #         ('end_date', '>=', date_from),
    #     ]
    #     if tenant_id:
    #         domain.append(('tenant_id', '=', tenant_id))

    #     leases = request.env['real_estate.lease'].sudo().search(domain)

    #     # Structure response to group/return tenant details with their leases
    #     tenants_data = {}
    #     for lease in leases:
    #         tenant = lease.tenant_id
    #         t_id = tenant.id
    #         if t_id not in tenants_data:
    #             tenants_data[t_id] = {
    #                 'tenant_id': t_id,
    #                 'tenant_name': tenant.name,
    #                 'leases': []
    #             }
            
    #         tenants_data[t_id]['leases'].append({
    #             'id': lease.id,
    #             'name': lease.name,
    #             'property_id': lease.property_id.id,
    #             'property_name': lease.property_id.name,
    #             'start_date': fields.Date.to_string(lease.start_date),
    #             'end_date': fields.Date.to_string(lease.end_date),
    #             'monthly_rent': lease.monthly_rent,
    #             'state': lease.state,
    #         })

    #     return request.make_json_response({
    #         'status': 'success',
    #         'data': list(tenants_data.values()),
    #     })


#tenant leases and its count
    @http.route('/api/tenant_leases', type='http', auth='none', methods=['GET'], csrf=False)
    def list_leases(self):

        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
        tenant_id = request.httprequest.args.get('tenant_id')
        date_from = request.httprequest.args.get('date_from')
        date_to = request.httprequest.args.get('date_to')

        if not tenant_id:
            return request.make_json_response(
                {'status': 'error', 'message': 'tenant_id is required'},
                status=400
            )

        try:
            tenant_id = int(tenant_id)
            date_from_dt = fields.Date.to_date(date_from) if date_from else None
            date_to_dt = fields.Date.to_date(date_to) if date_to else None
        except (ValueError, TypeError) as e:
            return request.make_json_response(
                {'status': 'error', 'message': f'Invalid parameter format: {str(e)}'},
                status=400
            )

        domain = [('tenant_id', '=', tenant_id)]

        if date_from_dt and date_to_dt:
            if date_from_dt > date_to_dt:
                return request.make_json_response(
                    {'status': 'error', 'message': 'date_from must be before or equal to date_to'},
                    status=400
                )
            domain.extend([
                ('start_date', '<=', date_to_dt),
                ('end_date', '>=', date_from_dt),
            ])

        leases = request.env['real_estate.lease'].sudo().search(domain)

        return request.make_json_response({
            'status': 'success',
            'tenant_id': tenant_id,
            'count': len(leases),
            'leases': [{
                'id': lease.id,
                'name': lease.name,
                'property_id': lease.property_id.id,
                'property_name': lease.property_id.name,
                'start_date': fields.Date.to_string(lease.start_date),
                'end_date': fields.Date.to_string(lease.end_date),
                'monthly_rent': lease.monthly_rent,
                'state': lease.state,
            } for lease in leases]
        })

#api to create lease
    @http.route('/api/lease/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_lease(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get('Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs
            #lease
            if not params.get('name') or not params.get('property_id') or not params.get('start_date') or not params.get('end_date'):
                return {
                    'status': 'error',
                    'message': 'Name , property_id, tenant_id, start_date and end_date are required'
                }
            #tenant
            if not params.get('tenant_name') or not params.get('email'):
    
                    return {
                        'status': 'error',
                        'message': 'Either tenant_id , email and tenant_name (to create a new tenant) must be provided'
                    }

            # Create tenant
            tenant_obj = request.env['real_estate.tenant'].sudo().create({
                    'name': params.get('tenant_name'),
                    'email': params.get('email')
                  })
            # Create lease
            lease_obj = request.env['real_estate.lease'].sudo().create({
                'name': params.get('name'),
                'property_id': params.get('property_id'),
                'tenant_id': tenant_obj.id,
                'start_date': params.get('start_date'),
                'end_date': params.get('end_date')
      })
            
            return {
                'status': 'success',
                'message': 'Lease created successfully',
                'data': {
                    'lease_id': lease_obj.id,
                    'name': lease_obj.name,
                    'property_id': lease_obj.property_id.id,
                    'tenant_id':tenant_obj.id,
                    'tenant_name': tenant_obj.name,
                    'tenant_email':tenant_obj.email

                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
#########check with api key instead of token ########
    @http.route(
            '/api/check_api_key',
            type='http',
            auth='none',
            methods=['GET'],
            csrf=False
        )
    def check_api_key(self):

            api_key = request.httprequest.headers.get(
                'Authorization',
                ''
            )

            api_key = api_key.replace('Bearer ', '').strip()

            user_id = request.env['res.users.apikeys']._check_credentials(
                scope='rpc',
                key=api_key
            )

            if not user_id:
                return invalid_response(
                    message='Invalid API Key',
                    status=401
                )

            return valid_response(
                message='Valid API Key',
                data={
                    'user_id': user_id
                }
            )