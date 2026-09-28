# -*- coding: utf-8 -*-
{
    'name': "real_estate",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm', 'website','portal', 'mail'],

    'assets': {
        'web.assets_frontend': [
            'real_estate/static/src/css/property_website.css',
        ],
    },

    # always loaded
    'data': [
        'security/property_security.xml',
        'security/ir.model.access.csv',
        'wizard/tenant.xml',
        'wizard/maintenance.xml',
        'wizard/lease.xml',
        'report/report.xml',
        'report/property_report_template.xml',
        'report/lease_report_template.xml',
        'views/payment_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/mail_template_data.xml',
        'views/res_partner_views.xml',
        'views/portal_templates.xml',
        'views/portal_prop.xml',
        'views/portal_maintainance.xml',
        'views/property_views.xml',
        'views/maintenance_request_views.xml',  
        'views/tenant_views.xml',
        'views/lease_views.xml',
        'views/crm_lead_views.xml',
        'views/ir_sequence_data.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

