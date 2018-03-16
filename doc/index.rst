================================
Sync Database with LDAP
================================

Configuration
-------------

Before you use this module you must configure the Odoo LDAP Settings:

- Go to Settings --> General Settings --> Enable LDAP Authentication --> LDAP Server.
- Create or Edit the LDAP Server Settings.
- Tested with LDAP Filter = "(mail=%s)", Sequence = 10, Create User Enabled.

In "List" menu create the LDAP mappings to the Odoo models, or import the these mappings and modify them to suit your needs:

.. code-block:: text

 "id","attribute","create_uid/id","create_date","foreign_key_type","foreign_key_field","foreign_key_of","is_unique_identifier","write_uid/id","write_date","ldap_attribute","model"
 "__export__.hr_ldap_sync_model_mapping_1","name","base.user_root","2017-12-14 12:10:27","","","","False","base.user_root","2017-12-15 11:38:19","name","res.users"
 "__export__.hr_ldap_sync_model_mapping_2","login","base.user_root","2017-12-15 11:38:26","","","","True","base.user_root","2017-12-15 16:18:41","mail","res.users"
 "__export__.hr_ldap_sync_model_mapping_4","name","base.user_root","2017-12-15 17:09:11","","","","True","base.user_root","2017-12-15 17:09:11","name","res.company"
 "__export__.hr_ldap_sync_model_mapping_6","company_ids","base.user_root","2017-12-22 14:41:48","Many2*","name","res.company","False","base.user_root","2017-12-22 15:05:11","company","res.users"
 "__export__.hr_ldap_sync_model_mapping_7","company_id","base.user_root","2017-12-22 15:05:14","One2*","name","res.company","False","base.user_root","2017-12-22 15:05:18","company","res.users"
 "__export__.hr_ldap_sync_model_mapping_8","name","base.user_root","2017-12-22 15:33:47","","","","False","base.user_root","2017-12-22 15:33:47","name","hr.employee"
 "__export__.hr_ldap_sync_model_mapping_9","identification_id","base.user_root","2017-12-22 15:34:57","","","","True","base.user_root","2017-12-22 15:34:57","mail","hr.employee"
 "__export__.hr_ldap_sync_model_mapping_10","user_id","base.user_root","2017-12-22 15:37:04","One2*","login","res.users","False","base.user_root","2017-12-22 15:41:16","mail","hr.employee"
 "__export__.hr_ldap_sync_model_mapping_11","address_id","base.user_root","2017-12-22 15:55:47","One2*","name","res.partner","False","base.user_root","2017-12-22 15:55:47","company","hr.employee"
 "__export__.hr_ldap_sync_model_mapping_12","image","base.user_root","2017-12-22 16:04:42","","","","False","base.user_root","2017-12-22 16:04:42","thumbnailPhoto","hr.employee"

Usage
-----

You should follow these guidelines:

- First use the "Sync" option to synchronize the mappings with the LDAP. (delete is commented, uncoment if needed)
- Then Update the Foreign Keys for Company, Jobs and Departments by choosing the "Update_FK Company". (if applicable on your mappings)
- Update the Users Foreign Keys by choosing the "Update_FK Users". (if applicable on your mappings)
- Update the Foreign Keys for the remaining mappings with the "Update_FK" option.

Sometimes the foreign keys will fail due to missing dependencies. Restart the server and try again to refresh the database.

Updating Foreign Keys takes quite some time, if no messages are appearing on logs then execution is running normally.

