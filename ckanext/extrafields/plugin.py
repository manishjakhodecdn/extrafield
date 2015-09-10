import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.model as model
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.lib.navl.dictization_functions import unflatten, Invalid
from ckan.model.domain_object import DomainObjectOperation
import ckan.lib.mailer as mailer
import ckan.lib.helpers as h
import time



from ckan.plugins import IGroupController
#DEFAULT_DOMAIN_CATEGORY_NAME = 'domain'
get_action = logic.get_action
NotFound = logic.NotFound
clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params
ds_groups = []

def check_group_availability(valueItem,sufix):
    context2 = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    complexdata = { 'id': valueItem+sufix }
    groupshow  = logic.get_action('group_show')(context2, complexdata) 
    return groupshow

def create_missing_group(valueItem ,sufix): 
    context1 = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    groupCreaated = { 'name' : valueItem+sufix , 'title' : valueItem, 'users': [{ 'capacity': 'admin', 'name' : 'admin' }], 'type': 'group' }
    group_created_string = logic.get_action('group_create')(context1, groupCreaated)
    return group_created_string 

def _check_tags(key, data, errors, context):

    unflattened = unflatten(data)
    option = {'domain':'-dm', 'phase':'-ph'}
    keyvalue = key[0]
    pkg_name = unflattened.get('name')
    value = data.get(key)
    array = value.split(',')
    for valueItem in array:     
        complexdata = { 'id': valueItem }
        try: 
            groupshow = check_group_availability(valueItem, option[keyvalue])
        except NotFound:
            # If group is not exist then create
            getSting = create_missing_group(valueItem, option[keyvalue])
            
        ds_groups.append({ 'name' : valueItem+option[keyvalue] })
    return
def update_package_group_association(pkg_name, ds_groups):
    context_pkg = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    chk_pckg = { 'id' : pkg_name }
    pkg_avail = logic.get_action('package_show')(context_pkg, chk_pckg)
    context_group1 = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    #schemaUpdateGroup = { 'id' : pkg_avail['name'], 'groups' : ds_groups }
    #getlisting = logic.get_action('package_update')(context_group1, schemaUpdateGroup)
    return  #getlisting


class ExtrafieldsPlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):
    
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    
    
    def before_view(self, pkg_dict):
        return pkg_dict

    def create_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        #update_package_group_association(self.name, ds_groups)
        return schema   

    def _modify_package_schema(self, schema):
        schema.update({
                'system_data': [toolkit.get_validator('ignore_missing'),
                    toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'structured_data' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'data_sources' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'requirement_security' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'system_experts' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'it_system_owner' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'business_owner' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'frontend_app' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'business_owner' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'domain' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),_check_tags]
                })
        schema.update({
                'key_entities' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'phase' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),_check_tags]
                })
        schema.update({
                'chameleon_id' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        # Add our custom_resource_text metadata field to the schema
        schema['resources'].update({
                'oracle_database_sid' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'oracle_server_name' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'oracle_port' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'mysql_hostname' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'mysql_port' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'access_database' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'path_to_shared_area' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'path_url' : [ toolkit.get_validator('ignore_missing') ]
                })
        return schema
    # IConfigurer

    def update_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).update_package_schema()
        #our custom field
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).show_package_schema()
        schema.update({
            'system_data': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'structured_data': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'data_sources': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'requirement_security': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'system_experts': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'it_system_owner': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'business_owner': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'frontend_app': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'domain': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'key_entities': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'phase': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })
        schema.update({
            'chameleon_id': [toolkit.get_converter('convert_from_extras'),
                            toolkit.get_validator('ignore_missing')]
        })

        schema['resources'].update({
                'oracle_database_sid' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'oracle_server_name' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'oracle_port' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'mysql_hostname' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'mysql_port' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'access_database' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'path_to_shared_area' : [ toolkit.get_validator('ignore_missing') ]
                })
        schema['resources'].update({
                'path_url' : [ toolkit.get_validator('ignore_missing') ]
                })
        
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
    
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'extrafields')

    def notify(self, entity, operation=None):
        context4 = {'model': model, 'ignore_auth': True, 'defer_commit': True}
        if isinstance(entity, model.Package):
            if operation == DomainObjectOperation.new:
                update_package_group_association(entity.name,ds_groups)
            elif operation == DomainObjectOperation.changed: 
                update_package_group_association(entity.name,ds_groups)
            else:
                return
                                