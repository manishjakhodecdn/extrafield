import urllib2
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
import sys


from ckan.plugins import IGroupController
#DEFAULT_DOMAIN_CATEGORY_NAME = 'domain'
get_action = logic.get_action
NotFound = logic.NotFound
clean_dict = logic.clean_dict
tuplize_dict = logic.tuplize_dict
parse_params = logic.parse_params
ds_groups = []
set_flag = True

def check_group_availability(valueItem,sufix):
    context2 = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    valueItem = valueItem.replace(' ', '-')
    valueItem = valueItem.lower()
    complexdata = { 'id': valueItem+sufix }
    if sufix == '-dm':
        groupshow  = logic.get_action('group_show')(context2, complexdata)
    elif sufix == '-ph': 
        groupshow  = logic.get_action('organization_show')(context2, complexdata)
        
    return groupshow

def manage_vocab(key, data, errors, context):
    # check vocab available
    # if not then create
    # return vocab id
    print "manage vocab start"
    vocab_context = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True }
    vocab_list = []
    value = data.get(key)
   
    if value != '' and value is not None: 
        array = value.split(',')
        for tag_name in array:     
            try:
                # get vocab details
                vocab_list = logic.get_action('vocabulary_list')(vocab_context)
                vocab_list = vocab_list[0]
                
            except Exception, e:
                # create Vocab
                domaindata = {'name': 'gsk_vocab'}
                vocab_list = logic.get_action('vocabulary_create')(vocab_context, domaindata)
       
            # check tag already exist in vocab list
            tag_name = tag_name.replace(' ', '-')
            tag_name = tag_name.lower()
            tagDict1 = {'vocabulary_id':vocab_list['id'], 'query': tag_name }
            taginfo_upper = logic.get_action('tag_search')(vocab_context, tagDict1)
            
            if taginfo_upper['count'] == 0: 
                print "create tag"
                tagdata = {'name': tag_name, 'vocabulary_id': vocab_list['id'] } #, 'vocabulary_id': vocab_list['id']
                tagdata_str = logic.get_action('tag_create')(vocab_context, tagdata)
    return 

def create_missing_group(valueItem ,sufix): 
    context1 = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    _name = valueItem.replace(' ', '-')
    _name = _name.lower()
    
    if sufix == '-dm':             
        groupCreaated = { 'name' :  _name+sufix , 'title' : valueItem, 'users': [{ 'capacity': 'admin', 'name' : 'admin' }], 'type': 'group', 'extras':[{ 'key' : 'gsk_type', 'value' :sufix }] }
        group_created_string = logic.get_action('group_create')(context1, groupCreaated)

    elif sufix == '-ph':
        groupCreaated1 = { 'name' : _name+sufix , 'title' : valueItem, 'users': [{ 'capacity': 'admin', 'name' : 'admin' }], 'type': 'organization', 'extras':[{ 'key' : 'gsk_type', 'value' :sufix }] }
        group_created_string = logic.get_action('organization_create')(context1, groupCreaated1)
        
    return group_created_string

def _check_tags(key, data, errors, context):
    
    unflattened = unflatten(data)
    option = {'domain':'-dm', 'phase':'-ph'}
    keyvalue = key[0]
    pkg_name = unflattened.get('name')
    value = data.get(key)
    if value != '' and value is not None: 
        array = value.split(',')
        for valueItem in array:     
            complexdata = { 'id': valueItem }
            try:        
                groupshow = check_group_availability(valueItem, option[keyvalue])
            except NotFound:
                # If group is not exist then create
                getSting = create_missing_group(valueItem, option[keyvalue])
            
            _name = valueItem.replace(' ', '-')
            _name = _name.lower()
    
            if option[keyvalue] == '-dm':
                ds_groups.append({ 'name' : _name+option[keyvalue] })

    global set_flag
    set_flag = True
 
def create_association_group(pkg_dict):
    global set_flag 
    global ds_groups

    phase_value = pkg_dict['phase']
    if phase_value != '' and phase_value is not None:
        phase_value = pkg_dict['phase']+'-ph'
        phase_value = phase_value.replace(' ', '-')
        phase_value = phase_value.lower()
    
    context_pkg = {'model': model, 'session': model.Session, 'ignore_auth': True, 'allow_partial_update' : True }
    packageUpdate  =  { 'id' : pkg_dict['id'], 'author' : 'gsk' , 'groups' : ds_groups, 'owner_org': phase_value }
    packageUpdate_str = logic.get_action('package_update')(context_pkg, packageUpdate)
    
    ds_groups = []
    return


def update_association_group(pkg_dict):
    global set_flag 
    global ds_groups
    
    #lets get package information first
    context_pkg = { 'model': model, 'session': model.Session, 'ignore_auth': True, 'allow_partial_update' : True }
    pkg_Data = { 'id' : pkg_dict['id']}
    pkg_Info = logic.get_action('package_show')(context_pkg, pkg_Data)
   
    if set_flag is not False:
        set_flag = False
        phase_value = ''
        try:
            pkg_Info['phase']
        except Exception, e:
            pass
        else:
            phase_value = pkg_Info['phase']
            if phase_value != '' and phase_value is not None:
                phase_value = pkg_Info['phase']+'-ph'
                phase_value = phase_value.replace(' ', '-')
                phase_value = phase_value.lower()
            
        if phase_value == '':
            phase_value = 'gsk'

        packageUpdate  =  { 'id' : pkg_dict['id'], 'author' : 'gsk' , 'groups' : ds_groups , 'owner_org': phase_value  }
        packageUpdate_str = logic.get_action('package_update')(context_pkg, packageUpdate)
        ds_groups = []
    
    return

def gettag_list():
    context_tags = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    try:
        # get vocab details
        vocab_list = logic.get_action('vocabulary_list')(context_tags)
        vocab_list = vocab_list[0]
        
        tagDict = { 'vocabulary_id' : vocab_list['id'] }
        gettag_list = logic.get_action('tag_list')(context_tags, tagDict)
        gettag_list = {'result':gettag_list}
        return gettag_list
    except Exception, e:
        return None
      
def manage_rating(pkg_dict):
     context_rating = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
     package_ref = pkg_dict['id']
     package = model.Package.get(package_ref)
     ret_dict = {'rating_average': package.get_average_rating(),
                'rating_count': len(package.ratings)}
     return ret_dict
     
def create_rating(pkg_dict, data):
    context_rating = {'model': model,
                   'session': model.Session,
                   'ignore_auth': True
                }
    rateDict = { 'package' : pkg_dict['id'], 'rating':data  }
    rate_res = logic.get_action('rating_create')(context_rating, rateDict)
    return rate_res

class ExtrafieldsPlugin(plugins.SingletonPlugin,toolkit.DefaultDatasetForm):
    
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IDomainObjectModification, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    
    def before_view(self, pkg_dict):
        #Just to test the method
        set_flag = True       
        return pkg_dict


    def after_create(self, context, pkg_dict):
        create_association_group(pkg_dict)
        return

    def get_helpers(self):
        # Tag listing 
        return {'manage_rating' : manage_rating, 'create_rating' : create_rating}


    def after_update(self, context, pkg_dict):
        update_association_group(pkg_dict)
        return 
   
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
                'frontend_app' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'), manage_vocab]
                })
        schema.update({
                'business_owner' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras')]
                })
        schema.update({
                'domain' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),_check_tags,manage_vocab]
                })
        schema.update({
                'key_entities' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),manage_vocab]
                })
        schema.update({
                'phase' : [ toolkit.get_validator('ignore_missing'), toolkit.get_converter('convert_to_extras'),_check_tags,manage_vocab]
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

    
               
              
                                
