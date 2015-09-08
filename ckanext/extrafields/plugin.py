import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.model as model
import ckan.lib.mailer as mailer

from ckan.plugins import IGroupController
#DEFAULT_DOMAIN_CATEGORY_NAME = 'domain'

get_action = logic.get_action
            
def getGrouplist(self,value):
    print value
    return

    context = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }                                                       
    data_dict = { 'sort': 'name' }               
    grouplist = logic.get_action('group_list')(context, data_dict)
    #{'image_upload': u'', 'title': u'Facetslist', 'description': u'', 'name': u'facetslist', 'image_url': u'', 'users': [{'capacity': 'admin', 'name': u'admin'}], 'save': u'', 'type': 'group', 'clear_upload': u''}

    
    for grouplistitem in grouplist:
        complexdata = { 'id': grouplistitem }
        grouplistDetails = logic.get_action('group_show')(context, complexdata)
        groupCreaated = { 'name' : 'timepass_dm', 'title' : 'timepass_dm', 'users': [{ 'capacity': 'admin', 'name' : 'admin' }], 'type': 'group' }
        group_created = logic.get_action('group_create')(context, groupCreaated)
        print group_created
        return 

class ExtrafieldsPlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):
    
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
	
    
    def before_view(self, pkg_dict):
        return pkg_dict

    def create_package_schema(self):
        schema = super(ExtrafieldsPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
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
                'domain' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),getGrouplist(self, value)]
                })
        schema.update({
                'key_entities' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'phase' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
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
