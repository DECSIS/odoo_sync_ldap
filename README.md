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

You must set the priorities for the models and for the foreign keys. If model X
depends on model Y, then model X should have higher priorities. The "model
priorities" use the priority of the first mapping of that model found on the
list.

For Foreign Keys higher priority also means it is executed first. For example
"company_ids" should be assigned before "company_id" to user foreign key, then
"company_ids" must have higher priority than "company_id". This priority is in
relation to the foreign keys in the same model.

## Usage

You should follow these guidelines:

- First use the "Sync" option to synchronize the mappings with the LDAP. (delete is commented, uncoment if needed)
- Use the "Update_FK" option to update the foreign keys. 

Updating Foreign Keys takes quite some time, if no error messages are appearing on
logs then execution is running normally.
