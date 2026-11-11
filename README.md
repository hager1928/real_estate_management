# Real Estate Management for Odoo 17

An Odoo add-on for managing rental properties and the day-to-day work around them. It brings property records, tenants, lease agreements, rent payments, and maintenance requests into one application, with website pages for public listings and tenant self-service.

## Features

- **Property management:** Store property details, photos, type, monthly rent, deposit, bedroom count, availability, and assigned agent.
- **Tenant records:** Keep tenant contact details, connect tenants to CRM leads, and optionally link a tenant to an Odoo user for portal access.
- **Lease tracking:** Create leases with start and end dates, rent, deposit, status, and related maintenance and payment history. Lease references are generated from an Odoo sequence.
- **Rent payments:** Track due dates, amounts, payment dates, methods, and payment status. Payments are linked to their lease, tenant, and property.
- **Maintenance requests:** Record issue type, urgency, description, scheduling, assignment, completion date, and actual cost.
- **Website and portal:** List available properties publicly, provide property detail pages, and show signed-in tenants their leases and maintenance requests.
- **Reports and exports:** Print property and lease summaries, generate rent roll and maintenance reports, and export property details to an Excel workbook.
- **CRM integration:** Link tenants to CRM leads and accept CRM lead submissions through an API route.
- **Access groups:** Includes groups and record rules for agents, property managers, tenants, lease users and managers, and maintenance users and managers.

## Requirements

- Odoo **17.0**
- Odoo standard modules: `base`, `crm`, `website`, `portal`, and `mail`
- Python package `xlsxwriter` for the property Excel export

## Installation

1. Place the `real_estate` directory in an Odoo add-ons path (or add its parent directory to `addons_path`).
2. Restart the Odoo server and update the Apps list.
3. Install **real_estate** from the Apps menu, or update it from the command line:

   ```bash
   ./odoo-bin -d <database_name> -i real_estate --addons-path=<addons_paths>
   ```

   Replace the placeholders with your database name and configured add-on paths. Odoo must be run from its source directory or through your normal Odoo service configuration.

4. Assign the appropriate Real Estate groups to users. System administrators are configured to inherit the manager groups defined by this add-on.

The optional demo records are loaded when the database is initialized with demo data enabled.

## How to use

After installation, open **Real Estate** in the Odoo backend. Its menus provide access to:

| Area | Purpose |
| --- | --- |
| Properties | Maintain listings, availability, pricing, and property details. |
| Tenants | Maintain tenant contacts and CRM lead links. |
| Leases | Manage lease dates, status, rent, and related records. |
| Maintenance Request | Log and track work reported for a leased property. |
| Payment | Record rent payments and their status. |
| Reporting | Open the rent roll and maintenance report wizards. |

The public website lists available properties at `/properties`. Signed-in tenant portal users can view their lease and maintenance information at `/my/leases`; a tenant record must be linked to the user's Odoo account.

## Data model

| Model | Description |
| --- | --- |
| `real_estate.property` | Property listing and availability. |
| `real_estate.tenant` | Tenant contact and portal linkage. |
| `real_estate.lease` | Agreement connecting a tenant and a property. |
| `lease.payment` | Payment entries connected to a lease. |
| `maintenance.request` | Maintenance work connected to a lease. |

## API routes

The add-on defines routes for creating property, tenant, CRM, and lease records, updating tenant/property records, and listing leases by date range. The implementation is in `real_estate/controllers/api.py`.

> **Deployment note:** Review and secure the API routes before exposing them to the internet. Some routes use public or unauthenticated access, accept writes with elevated permissions, or contain a token directly in source code. Configure authentication, authorization, input validation, and secrets management for your deployment; do not use the source token as a production credential.

## Repository layout

```text
real_estate/
├── controllers/   # Website, portal, API, and Excel export routes
├── demo/          # Optional demo records
├── models/        # Property, tenant, lease, payment, and maintenance models
├── report/        # Property and lease PDF reports
├── security/      # Access control lists, groups, and record rules
├── views/         # Backend views, menus, and website templates
└── wizard/        # Tenant, lease, maintenance, and report wizards
```

## Known implementation notes

- The add-on manifest currently contains placeholder publisher metadata and a generic description; update these before publishing a packaged release.
- Currency display and Excel formatting are currently hard-coded in parts of the interface/export. Adapt them for the currencies and localization used by your database.
- Verify access groups and API permissions against your organization's policy before production use.
