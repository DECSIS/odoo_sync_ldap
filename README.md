# Sync LDAP Odoo Module

odoo_sync_ldap aims to sync LDAP information with Odoo.
![Module Overview](hr_ldap_sync/images/hr_ldap_sync.png?raw=true)


## Configuration

Before you use this module you must configure the Odoo LDAP Settings:

- Go to Settings --> General Settings --> Enable LDAP Authentication --> LDAP Server.
- Create or Edit the LDAP Server Settings.
- Tested with LDAP Filter = "(mail=%s)", Sequence = 10, Create User Enabled.

In "List" menu create the LDAP mappings to the Odoo models like so:
![Mapping Example](hr_ldap_sync/images/mapping_example.png?raw=true)

Or import the "hr_ldap_sync.model_mapping.csv" file into Odoo and change it to suit your needs.

## Usage

You should follow these guidelines:

- First use the "Sync" option to synchronize the mappings with the LDAP. (delete part of sync is commented, uncoment if needed)
- Then Update the Foreign Keys for Company, Jobs and Departments by choosing the "Update_FK Company". (if applicable on your mappings)
- Update the Users Foreign Keys by choosing the "Update_FK Users". (if applicable on your mappings)
- Update the Foreign Keys for the remaining mappings with the "Update_FK" option.

Sometimes the foreign keys will fail due to missing dependencies. Restart the server and try again to refresh the database.

Updating Foreign Keys takes quite some time, if no messages are appearing on logs then execution is running normally.
