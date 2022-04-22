import logging
import subprocess
import os

from ckan import plugins as p
from ckan.lib.helpers import json
from ckan.plugins.core import SingletonPlugin, implements
from ckanext.harvest.interfaces import IHarvester
from ckanext.spatial.harvesters.waf import WAFHarvester

log = logging.getLogger(__name__)


class WAFHarvesterCIOOS(WAFHarvester, SingletonPlugin):
    '''
    A Harvester for WAF (Web Accessible Folders) containing spatial metadata documents.
    e.g. Apache serving a directory of ISO 19139 files.
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'waf_cioos',
            'title': 'CIOOS Web Accessible Folder (WAF)',
            'description': 'A Web Accessible Folder (WAF) displaying a list of spatial metadata documents that implement the CIOOS metadata profile'
        }

    def from_json(self, val):
        try:
            new_val = json.loads(val)
        except Exception:
            new_val = val
        return new_val

    def get_package_dict(self, iso_values, harvest_object):

        package_dict = super(WAFHarvesterCIOOS, self).get_package_dict(iso_values, harvest_object)

        # Package name
        package = harvest_object.package

        # Handle title as json language dictinary
        iso_title = self.from_json(iso_values['title'])
        iso_title = iso_title.get(p.toolkit.config.get('ckan.locale_default', 'en'), iso_title)

        if package is None or package.title != iso_title:
            name = self._gen_new_name(iso_title)
            if not name:
                name = self._gen_new_name(str(iso_values['guid']))
            if not name:
                raise Exception('Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
            package_dict['name'] = name
        else:
            package_dict['name'] = package.name

        # Handle Scheming, Composit, and Fluent extensions
        loaded_plugins = p.toolkit.config.get("ckan.plugins")
        if 'scheming_datasets' in loaded_plugins:
            composite = 'composite' in loaded_plugins
            fluent = 'fluent' in loaded_plugins

            log.debug('#### Scheming, Composite, or Fluent extensions found, processing dictinary ####')
            schema = p.toolkit.h.scheming_get_dataset_schema('dataset')

            # convert extras key:value list to dictinary
            extras = {x['key']: x['value'] for x in package_dict.get('extras', [])}

            for field in schema['dataset_fields']:
                fn = field['field_name']
                iso = iso_values.get(fn, {})
                # remove empty strings from list
                if isinstance(iso, list):
                    iso = list(filter(len, iso))

                handled_fields = []
                if composite:
                    self.handle_composite_harvest_dictinary(field, iso_values, package_dict, handled_fields)

                if fluent:
                    self.handle_fluent_harvest_dictinary(field, iso_values, package_dict, schema, handled_fields, self.source_config)

                self.handle_scheming_harvest_dictinary(field, iso_values, extras, package_dict, handled_fields)

            extras_as_dict = []
            for key, value in extras.iteritems():
                if package_dict.get(key, ''):
                    log.error('extras %s found in package dict: key:%s value:%s', key, key, value)
                if isinstance(value, (list, dict)):
                    extras_as_dict.append({'key': key, 'value': json.dumps(value)})
                else:
                    extras_as_dict.append({'key': key, 'value': value})

            package_dict['extras'] = extras_as_dict

        # End of processing, return the modified package
        return package_dict

    def transform_to_iso(self, original_document, original_format, harvest_object):

        lowered = original_document.lower()
        if '</mdb:MD_Metadata>'.lower() in lowered:
            log.debug('Found ISO19115-3 format, transforming to ISO19139')

            xsl_filename = os.path.abspath("./ckanext-spatial/ckanext/spatial/transformers/ISO19115-3/toISO19139.xsl")
            process = subprocess.Popen(["saxonb-xslt", "-s:-", xsl_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.stdin.write(original_document.encode('utf-8'))
            newDoc, errors = process.communicate()
            process.stdin.close()
            if errors:
                log.error(errors)
                return None
            return newDoc

        return None

    def handle_fluent_harvest_dictinary(self, field, iso_values, package_dict, schema, handled_fields, harvest_config):
        field_name = field['field_name']
        if field_name in handled_fields:
            return

        field_value = {}

        if not field.get('preset', '').startswith(u'fluent'):
            return

        # set default language, default to english
        default_language = iso_values.get('metadata-language', 'en')
        if not default_language:
            default_language = 'en'

        # handle tag fields
        if field.get('preset', '') == u'fluent_tags':
            tags = iso_values.get('tags', [])
            schema_languages = p.toolkit.h.fluent_form_languages(schema=schema)

            # init language key
            field_value = {l: [] for l in schema_languages}

            # process tags by convert list of language dictinarys into
            # a dictinary of language lists
            for t in tags:
                tobj = self.from_json(t)
                if isinstance(tobj, dict):
                    for key, value in tobj.iteritems():
                        if key in schema_languages:
                            field_value[key].append(value)
                else:
                    field_value[default_language].append(tobj)
            package_dict[field_name] = field_value

            # clean existing tag list in package_dict as it can only contain
            # alphanumeric characters. This only works if clean_tags is false
            # in config
            pkg_dict_tags = package_dict.get('tags', [])
            if pkg_dict_tags and not harvest_config.get('clean_tags'):
                tag_list = []
                for x in pkg_dict_tags:
                    x['name'] = self.from_json(x['name'])

                    if isinstance(x['name'], dict):
                        langValList = list(x['name'].values())
                        for item in langValList:
                            if item not in tag_list:
                                tag_list.append(item)
                    else:
                        if x['name'] not in tag_list:
                            tag_list.append(x['name'])
                package_dict['tags'] = [{'name': t} for t in tag_list]

        else:
            # strip trailing _translated part of field name
            if field_name.endswith(u'_translated'):
                package_fn = field_name[:-11]
            else:
                package_fn = field_name

            package_val = package_dict.get(package_fn, '')
            field_value = self.from_json(package_val)

            if isinstance(field_value, dict):  # assume biligual values already in data
                package_dict[field_name] = field_value
            else:
                # create bilingual dictinary. This will likely fail validation as it does not contain all the languages
                package_dict[field_name] = {}
                package_dict[field_name][default_language] = field_value

        handled_fields.append(field_name)

    def flatten_composite_keys(self, obj, new_obj={}, keys=[]):
        for key, value in obj.iteritems():
            if isinstance(value, dict):
                self.flatten_composite_keys(obj[key], new_obj, keys + [key])
            else:
                new_obj['_'.join(keys + [key])] = value
        return new_obj

    def handle_composite_harvest_dictinary(self, field, iso_values, package_dict, handled_fields):
        field_name = field['field_name']
        if field_name in handled_fields:
            return

        field_value = iso_values.get(field_name, {})
        # add __extras field to package dict as composit expects fields to be located there
        if '__extras' not in package_dict:
            package_dict['__extras'] = {}

        # populate composite fields
        if field_value and field.get('preset', '') == 'composite':
            if isinstance(field_value, list):
                field_value = field_value[0]
            field_value = self.flatten_composite_keys(field_value)
            for key, value in field_value.iteritems():
                newKey = field_name + '|' + key
                package_dict['__extras'][newKey] = value
            handled_fields.append(field_name)
        # populate composite repeating fields
        elif field_value and field.get('preset', '') == 'composite_repeating':
            if isinstance(field_value, dict):
                field_value[0] = field_value
            for idx, subitem in enumerate(field_value):
                # collaps subfields into one key value pair
                subitem = self.flatten_composite_keys(subitem)
                for key, value in subitem.iteritems():
                    newKey = field_name + '|' + str(idx + 1) + '|' + key
                    package_dict['__extras'][newKey] = value
            handled_fields.append(field_name)

    def handle_scheming_harvest_dictinary(self, field, iso_values, extras, package_dict, handled_fields):
        field_name = field['field_name']
        if field_name in handled_fields:
            return
        iso_field_value = iso_values.get(field_name, {})
        extra_field_value = extras.get(field_name, "")

        # move schema fields, in extras, to package dictionary
        if extra_field_value and not package_dict.get(field_name, ''):
            package_dict[field_name] = extra_field_value
            del extras[field_name]
            handled_fields.append(field_name)
        # move schema fields, in iso_values, to package dictionary
        elif iso_field_value and not package_dict.get(field_name, ''):
            # convert list to single value for select fields (not multi-select)
            if field.get('preset', '') == 'select' and isinstance(iso_field_value, list):
                iso_field_value = iso_field_value[0]
            package_dict[field_name] = iso_field_value
            # remove from extras so as not to duplicate fields
            if extras.get(field_name):
                del extras[field_name]
            handled_fields.append(field_name)
