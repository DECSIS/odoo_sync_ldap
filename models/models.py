# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import logging, sys, base64
import traceback

_logger = logging.getLogger(__name__)

class TransientModelMapping:

    def __init__(self):
        self.attributes = {}
        self.foreign_keys = {}
        self.id_in_odoo = None
        self.model_instance = None

    def __repr__(self):
        return str(self.__dict__)

    def validate(self):
        if not self.id_in_odoo:
            raise ValueError('Model {} dont define an identifier field'.format(self.model_instance))

class EmployeeLDAP(models.Model):
    _inherit = 'hr.employee'

    ldap_id = fields.Char()

class ModelMapping(models.Model):
    _name = "hr_ldap_sync.model_mapping"

    name = fields.Char(compute='_compute_name')
    model = fields.Char(required=True)
    attribute = fields.Char(required=True)
    ldap_attribute = fields.Char(required=True)
    is_unique_identifier = fields.Boolean(string='Is unique identifier?',required=True, default=False)
    foreign_key_of = fields.Char(string='Foreign key of model',required=False)
    foreign_key_field = fields.Char(string='Foreign key field on dst model',required=False)
    foreign_key_type = fields.Selection(string='FK Relation Type',selection=[('One2*','One2*'),('Many2*','Many2*')])


    @api.multi
    def _compute_name(self):
        for record in self:
            record.name = '[{}] ({}->{})'.format(record.model,record.ldap_attribute,record.attribute)

    @api.model
    def sync(self):
        Ldap = self.env['res.company.ldap']

        companies_ldap = {}
        departments_ldap = {}
        user_in_ldap = {}
        job_ldap = {}
        records_in_ldap = {
            'res.users': user_in_ldap,
            'hr.employee': user_in_ldap,
            'res.company': companies_ldap,
            'hr.department': departments_ldap,
            'hr.job': job_ldap,
        }
        for conf in Ldap.get_ldap_dicts():
            _logger.info('Querying ldap {}:{}'.format(conf['ldap_server'],conf.get('ldap_server_port')))
            results = Ldap.query(conf,u"(&(objectCategory=person)(mail=*))")
            for dn,entry in results:
                entry['mail'][0] = (entry['mail'][0]).lower()
                user_in_ldap[tools.ustr(entry['mail'][0])] = entry #toolds.ustr is used because a byte array is fetched from LDAP
                if 'company' in entry:
                    companies_ldap[tools.ustr(entry['company'][0])] = {'company': entry['company']}
                if 'department' in entry:
                    departments_ldap[tools.ustr(entry['department'][0])] = {'department': entry['department']}
                if 'title' in entry:
                    job_ldap[tools.ustr(entry['title'][0])] = {'title': entry['title']}

        _logger.info('{} users found in LDAP servers'.format(len(user_in_ldap)))
        _logger.info('{} companies found in LDAP servers'.format(len(companies_ldap)))
        _logger.info('{} departments found in LDAP servers'.format(len(departments_ldap)))
        _logger.info('{} job found in LDAP servers'.format(len(job_ldap)))


        mapping = self.generate_mapping()

        records_to_update_fk = {}
        # creates
        try:
            for model in mapping:
                model_id_field_in_odoo = mapping[model].id_in_odoo
                model_instance = mapping[model].model_instance
                map_records_odoo = {}
                for model_record in model_instance.search([]):
                    map_records_odoo[model_record[model_id_field_in_odoo]] = model_record
                _logger.info('{} {} found in Odoo'.format(len(map_records_odoo),model))

                records_in_ldap_for_model = records_in_ldap[model]
                records_to_add    = set(records_in_ldap_for_model.keys()) - set(map_records_odoo.keys())
                records_to_update = set(records_in_ldap_for_model.keys()) & set(map_records_odoo.keys())
                # Need to check which records are in update
                records_to_delete = set(map_records_odoo.keys()) - set(records_in_ldap_for_model.keys())

                _logger.info('Found {} new {} to add'.format(len(records_to_add),model))
                records_to_update_fk[model] = []

                for record_id_to_add in records_to_add:
                    record_odoo = self.add_record(records_in_ldap_for_model[record_id_to_add], mapping[model])
                    record_ldap = records_in_ldap_for_model[record_id_to_add]

                    records_to_update_fk[model].append({'odoo': record_odoo, 'ldap': record_ldap})

                for record_id_to_update in records_to_update:
                    record_odoo = map_records_odoo[record_id_to_update]
                    record_ldap = records_in_ldap_for_model[record_id_to_update]

                    self.update_record(record_ldap,record_odoo,mapping[model])
                    records_to_update_fk[model].append({'odoo': record_odoo, 'ldap': record_ldap})
                # for record_id_to_update in records_to_delete:
                    #    map_records_odoo[record_id_to_update].active = False

                _logger.info('###############Sync finished {}!##################'.format(model))
        except:
            _logger.error('Error sync {}!##################'.format(traceback.format_exc()))

        # update FK
        # self.update_fk(records_to_update_fk, mapping)

        _logger.info('###############Sync finished!##################')

    def update_fk(self, records_to_update, mapping):
        try:
            for model in mapping:
                _logger.info('###############Update FK {}!##################'.format(model))
                for new_record in records_to_update[model]:
                    self.apply_fks_to_record(new_record['odoo'], new_record['ldap'], mapping[model])
        except:
            _logger.error('Error sync {}!##################'.format(traceback.format_exc()))

    def update_fk_users(self, records_to_update, mapping):
        try:
            for model in mapping:
                if model == 'res.users':
                    _logger.info('###############Update FK {}!##################'.format(model))
                    for new_record in records_to_update[model]:
                        self.apply_fks_to_record(new_record['odoo'], new_record['ldap'], mapping[model])
        except:
            _logger.error('Error sync {}!##################'.format(traceback.format_exc()))


    def update_fk_company(self, records_to_update, mapping):
        try:
            for model in mapping:
                if model in ['res.company', 'hr.job', 'hr.department']:
                    _logger.info('###############Update FK {}!##################'.format(model))
                    for new_record in records_to_update[model]:
                        self.apply_fks_to_record(new_record['odoo'], new_record['ldap'], mapping[model])
        except:
            _logger.error('Error sync {}!##################'.format(traceback.format_exc()))

    def add_record(self,record_in_ldap,mapping):
        new_record = {}
        for attr_odoo,attr_ldap in mapping.attributes.items():
            if attr_ldap in record_in_ldap:
                if attr_odoo == 'image':
                    try:
                        new_record[attr_odoo] = base64.b64encode(record_in_ldap[attr_ldap][0])
                    except IOError as e:
                        _logger.error(e)
                    except ValueError as ve:
                        _logger.error(ve)
                else:
                    new_record[attr_odoo] = record_in_ldap[attr_ldap][0]

        _logger.info('Adding new {} {}'.format(mapping.model_instance,new_record))
        mapping.model_instance.create(new_record)
        return new_record

    def get_fk(self,fk_model_instance,fk_identifier_field,fk_value_in_ldap):
        result_fk = fk_model_instance.search([(fk_identifier_field,'=',fk_value_in_ldap )])
        if len(result_fk) == 1:
            return result_fk.id
        return None

    def update_manager_permissions(self, manager):
        # Manager Group Search
        manager_group = self.env.ref('job_plans.manager_group')
        # templateManager_group = self.env.ref('job_plans.job_template_manager')

        # if (manager.has_group('job_plans.job_template_manager')):
        #     templateManager_group.write({'users': [(3, manager.id)]})
        #     _logger.info('###############Write Template Manager##################')

        if (not manager.has_group('job_plans.manager_group')):
            manager_group.write({'users': [(4, manager.id)]})
            # _logger.info('###############Write Manager##################')

    def apply_fks_to_record(self,record_to_apply,record_in_ldap,mapping):
        for model_field,(fk_ldap_field,fk_model_instance,fk_identifier_field,foreign_key_type) in mapping.foreign_keys.items():
            if record_in_ldap.get(fk_ldap_field):
                fk_value_in_ldap = tools.ustr(record_in_ldap.get(fk_ldap_field)[0])
                result_fk = self.get_fk(fk_model_instance,fk_identifier_field,fk_value_in_ldap)
                try:
                    if result_fk:
                        # Check if foreign key exists and then that it does not reference itself (infinite recursion)
                        if fk_ldap_field == 'manager' and record_to_apply['id'] == result_fk:
                            if 'name' in record_to_apply[model_field]:
                                _logger.info('###############Tried to reference self {} {} with FK {} ({}={})!##################'.format(mapping.model_instance,record_to_apply.name,fk_model_instance,fk_identifier_field,fk_value_in_ldap))
                            else:
                                _logger.error('###############Tried to reference self {}, failed due to missing dependency {} ({}={})##################'.format(mapping.model_instance, fk_model_instance, fk_identifier_field, fk_value_in_ldap))
                        else:
                            if foreign_key_type == 'One2*':
                                record_to_apply[model_field] = result_fk

                                if fk_ldap_field == 'manager':
                                    manager = record_to_apply['parent_id'].user_id

                                    if manager:
                                        self.update_manager_permissions(manager)
                                    else:
                                        _logger('###############Failed due to no manager##################')

                                # if 'name' in record_to_apply:
                                #     _logger.info('###############Update {} {} inside One2* FK {} ({}={})!##################'.format(mapping.model_instance,record_to_apply.name,fk_model_instance,fk_identifier_field,fk_value_in_ldap))
                            elif foreign_key_type == 'Many2*':
                                record_to_apply[model_field] = [result_fk]

                                if fk_ldap_field == 'manager':
                                    manager = record_to_apply['parent_id'].user_id

                                    if manager:
                                        self.update_manager_permissions(manager)
                                    else:
                                        _logger('###############Failed due to no manager##################')

                                # if 'name' in record_to_apply:
                                #     _logger.info('###############Update {} {} inside FK Many2* {} ({}={})!##################'.format(mapping.model_instance,record_to_apply.name,fk_model_instance,fk_identifier_field,fk_value_in_ldap))
                    else:
                        _logger.warning('Applying FK to {} {}, failed due to missing dependency {} ({}={})'.format(mapping.model_instance,record_to_apply.name,fk_model_instance,fk_identifier_field,fk_value_in_ldap))
                except:
                    _logger.error('Trying to apply FK to {}, failed due to missing dependency {} ({}={})'.format(
                        mapping.model_instance, fk_model_instance, fk_identifier_field,
                        fk_value_in_ldap))

    def update_record(self,record_in_ldap,record_in_odoo,mapping):
        record_identifier = record_in_odoo[mapping.id_in_odoo]
        for attr_odoo,attr_ldap in mapping.attributes.items():
            if attr_ldap in record_in_ldap and tools.ustr(record_in_ldap[attr_ldap][0]) != tools.ustr(record_in_odoo[attr_odoo]):
                if attr_odoo == 'image':
                    image_ldap = tools.ustr(base64.b64encode(record_in_ldap[attr_ldap][0]))
                    image_odoo = tools.ustr(record_in_odoo[attr_odoo] )
                    if image_ldap != image_odoo:
                        _logger.info('Updated {} in {} ({})'.format(attr_odoo, mapping.model_instance,record_identifier))
                        record_in_odoo[attr_odoo] = image_odoo
                else:
                    _logger.info('Updated {} in {} ({}) from {} to {}'.format(attr_odoo, mapping.model_instance,
                                                                              record_identifier,
                                                                              record_in_odoo[attr_odoo],
                                                                              record_in_ldap[attr_ldap][0]))
                    record_in_odoo[attr_odoo] = record_in_ldap[attr_ldap][0]


    def generate_mapping(self):
        mapping = {}
        for record in self.search([]):
            if record.model not in mapping:
                mapping[record.model] = TransientModelMapping()
                mapping[record.model].model_instance = self.env[record.model]
            if record.is_unique_identifier:
                mapping[record.model].id_in_odoo = record.attribute
            if record.foreign_key_of:
                mapping[record.model].foreign_keys[record.attribute] = (record.ldap_attribute,self.env[record.foreign_key_of],record.foreign_key_field,record.foreign_key_type)
            else:
                mapping[record.model].attributes[record.attribute] = record.ldap_attribute
        self.validate_mapping(mapping)
        return mapping

    def validate_mapping(self,mapping):
        for model_name,model_mapping in mapping.items():
            model_mapping.validate()

    @api.model
    def sync_FK(self, option):
        Ldap = self.env['res.company.ldap']

        companies_ldap = {}
        departments_ldap = {}
        user_in_ldap = {}
        job_ldap = {}
        records_in_ldap = {
            'res.users': user_in_ldap,
            'hr.employee': user_in_ldap,
            'res.company': companies_ldap,
            'hr.department': departments_ldap,
            'hr.job': job_ldap,
        }
        for conf in Ldap.get_ldap_dicts():
            _logger.info('Querying ldap {}:{}'.format(conf['ldap_server'], conf.get('ldap_server_port')))
            results = Ldap.query(conf, u"(&(objectCategory=person)(mail=*))")
            for dn, entry in results:
                entry['mail'][0] = (entry['mail'][0]).lower()
                user_in_ldap[tools.ustr(
                    entry['mail'][0])] = entry  # toolds.ustr is used because a byte array is fetched from LDAP
                if 'company' in entry:
                    companies_ldap[tools.ustr(entry['company'][0])] = {'company': entry['company']}
                if 'department' in entry:
                    departments_ldap[tools.ustr(entry['department'][0])] = {'department': entry['department']}
                if 'title' in entry:
                    job_ldap[tools.ustr(entry['title'][0])] = {'title': entry['title']}

        _logger.info('{} users found in LDAP servers'.format(len(user_in_ldap)))
        _logger.info('{} companies found in LDAP servers'.format(len(companies_ldap)))
        _logger.info('{} departments found in LDAP servers'.format(len(departments_ldap)))
        _logger.info('{} job found in LDAP servers'.format(len(job_ldap)))

        mapping = self.generate_mapping()

        records_to_update_fk = {}
        # creates
        try:
            for model in mapping:
                model_id_field_in_odoo = mapping[model].id_in_odoo
                model_instance = mapping[model].model_instance
                map_records_odoo = {}
                for model_record in model_instance.search([]):
                    map_records_odoo[model_record[model_id_field_in_odoo]] = model_record
                _logger.info('{} {} found in Odoo'.format(len(map_records_odoo), model))

                records_in_ldap_for_model = records_in_ldap[model]
                records_to_add = set(records_in_ldap_for_model.keys()) - set(map_records_odoo.keys())
                records_to_update = set(records_in_ldap_for_model.keys()) & set(map_records_odoo.keys())
                # Need to check which records are in update
                records_to_delete = set(map_records_odoo.keys()) - set(records_in_ldap_for_model.keys())

                _logger.info('Found {} new {} to add'.format(len(records_to_add), model))
                records_to_update_fk[model] = []

                for record_id_to_add in records_to_add:
                    record_odoo = self.add_record(records_in_ldap_for_model[record_id_to_add], mapping[model])
                    record_ldap = records_in_ldap_for_model[record_id_to_add]

                    records_to_update_fk[model].append({'odoo': record_odoo, 'ldap': record_ldap})

                for record_id_to_update in records_to_update:
                    record_odoo = map_records_odoo[record_id_to_update]
                    record_ldap = records_in_ldap_for_model[record_id_to_update]

                    self.update_record(record_ldap, record_odoo, mapping[model])
                    records_to_update_fk[model].append({'odoo': record_odoo, 'ldap': record_ldap})
                # for record_id_to_update in records_to_delete:
                #    map_records_odoo[record_id_to_update].active = False

                _logger.info('###############Sync finished {}!##################'.format(model))
        except:
            _logger.error('Error sync {}!##################'.format(traceback.format_exc()))

        # update FK
        if option=='users':
            self.update_fk_users(records_to_update_fk, mapping)
        elif option=='company':
            self.update_fk_company(records_to_update_fk, mapping)
        else:
            self.update_fk(records_to_update_fk, mapping)

        _logger.info('###############Sync finished!##################')
