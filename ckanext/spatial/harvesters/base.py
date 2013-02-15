import re
import cgitb
import warnings
import urllib2
import sys
import logging
from string import Template
from urlparse import urlparse
from datetime import datetime
import uuid
import hashlib
import dateutil
import mimetypes


from pylons import config
from owslib import wms
import requests
from lxml import etree

from ckan import model
from ckan.lib.helpers import json
from ckan import logic
from ckan.logic import get_action, ValidationError
from ckan.lib.navl.validators import not_empty

from ckanext.harvest.harvesters.base import HarvesterBase
from ckanext.harvest.model import HarvestObject

from ckanext.spatial.validation import Validators, all_validators
from ckanext.spatial.model import ISODocument

log = logging.getLogger(__name__)

DEFAULT_VALIDATOR_PROFILES = ['iso19139']


def text_traceback():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = 'the original traceback:'.join(
            cgitb.text(sys.exc_info()).split('the original traceback:')[1:]
        ).strip()
    return res


def get_extra(harvest_object, key):
    for extra in harvest_object.extras:
        if extra.key == key:
            return extra.value
    return None

def guess_standard(content):
    lowered = content.lower()
    if '</gmd:MD_Metadata>'.lower() in lowered:
        return 'iso'
    if '</gmi:MI_Metadata>'.lower() in lowered:
        return 'iso'
    if '</metadata>'.lower() in lowered:
        return 'fgdc'
    return 'unknown'


class SpatialHarvester(HarvesterBase):

    _user_name = None

    source_config = {}

    force_import = False

    extent_template = Template('''
    {"type":"Polygon","coordinates":[[[$minx, $miny],[$minx, $maxy], [$maxx, $maxy], [$maxx, $miny], [$minx, $miny]]]}
    ''')

    ## IHarvester

    def validate_config(self, source_config):
        if not source_config:
            return source_config

        try:
            source_config_obj = json.loads(source_config)

            if 'validator_profiles' in source_config_obj:
                if not isinstance(source_config_obj['validator_profiles'],list):
                    raise ValueError('validator_profiles must be a list')

                # Check if all profiles exist
                existing_profiles = [v.name for v in all_validators]
                unknown_profiles = set(source_config_obj['validator_profiles']) - set(existing_profiles)

                if len(unknown_profiles) > 0:
                    raise ValueError('Unknown validation profile(s): %s' % ','.join(unknown_profiles))

        except ValueError,e:
            raise e

        return source_config

    ##

    ## SpatialHarvester

    '''
    These methods can be safely overridden by classes extending
    SpatialHarvester
    '''

    def get_package_dict(self, iso_values, harvest_object):
        '''
        Constructs a package_dict suitable to be passed to package_create or
        package_update. See documentation on
        ckan.logic.action.create.package_create for more details

        Tipically, custom harvesters would only want to add or modify the
        extras, but the whole method can be replaced if necessary. Note that
        if only minor modifications need to be made you can call the parent
        method from your custom harvester and modify the output, eg:

            class MyHarvester(SpatialHarvester):

                def get_package_dict(self, iso_values, harvest_object):

                    package_dict = super(MyHarvester, self).get_package_dict(iso_values, harvest_object)

                    package_dict['extras']['my-custom-extra-1'] = 'value1'
                    package_dict['extras']['my-custom-extra-2'] = 'value2'

                    return package_dict


        :param iso_values: Dictionary with parsed values from the ISO 19139
            XML document
        :type iso_values: dict
        :param harvest_object: HarvestObject domain object (with access to
            job and source objects)
        :type harvest_object: HarvestObject

        :returns: A dataset dictionary (package_dict)
        :rtype: dict
        '''

        tags = []
        for tag in iso_values['tags']:
            tag = tag[:50] if len(tag) > 50 else tag
            tags.append({'name':tag})

        package_dict = {
            'title': iso_values['title'],
            'notes': iso_values['abstract'],
            'tags': tags,
            'resources':[]
        }

        # We need to get the owner organization (if any) from the harvest
        # source dataset
        source_dataset = model.Package.get(harvest_object.source.id)
        if source_dataset.owner_org:
            package_dict['owner_org'] = source_dataset.owner_org

        # Package name
        package = harvest_object.package
        if package is None or package.title != iso_values['title']:
            name = self._gen_new_name(iso_values['title'])
            if not name:
                name = self._gen_new_name(str(iso_values['guid']))
            if not name:
                raise Exception('Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
            package_dict['name'] = name
        else:
            package_dict['name'] = package.name

        extras = {
            'guid': harvest_object.guid,
        }


        # Just add some of the metadata as extras, not the whole lot
        for name in [
            # Essentials
            'spatial-reference-system',
            'guid',
            # Usefuls
            'dataset-reference-date',
            'metadata-language', # Language
            'metadata-date', # Released
            'coupled-resource',
            'contact-email',
            'frequency-of-update',
            'spatial-data-service-type',
        ]:
            extras[name] = iso_values[name]

        extras['resource-type'] = iso_values['resource-type'][0]

        extras['licence'] = iso_values.get('use-constraints', '')

        def _extract_first_license_url(licences):
            for licence in licences:
                o = urlparse(licence)
                if o.scheme and o.netloc:
                    return licence
            return None

        if len(extras['licence']):
            license_url_extracted = _extract_first_license_url(extras['licence'])
            if license_url_extracted:
                extras['licence_url'] = license_url_extracted

        extras['access_constraints'] = iso_values.get('limitations-on-public-access','')
        if iso_values.has_key('temporal-extent-begin'):
            extras['temporal_coverage-from'] = iso_values['temporal-extent-begin']
        if iso_values.has_key('temporal-extent-end'):
            extras['temporal_coverage-to'] = iso_values['temporal-extent-end']

        # Save responsible organization roles
        parties = {}
        owners = []
        publishers = []
        for responsible_party in iso_values['responsible-organisation']:

            if responsible_party['role'] == 'owner':
                owners.append(responsible_party['organisation-name'])
            elif responsible_party['role'] == 'publisher':
                publishers.append(responsible_party['organisation-name'])

            if responsible_party['organisation-name'] in parties:
                if not responsible_party['role'] in parties[responsible_party['organisation-name']]:
                    parties[responsible_party['organisation-name']].append(responsible_party['role'])
            else:
                parties[responsible_party['organisation-name']] = [responsible_party['role']]

        parties_extra = []
        for party_name in parties:
            parties_extra.append('%s (%s)' % (party_name, ', '.join(parties[party_name])))
        extras['responsible-party'] = '; '.join(parties_extra)

        # Save provider in a separate extra:
        # first organization to have a role of 'owner', and if there is none, first one with
        # a role of 'publisher'
        if len(owners):
            extras['provider'] = owners[0]
        elif len(publishers):
            extras['provider'] = publishers[0]
        else:
            extras['provider'] = u''

        if len(iso_values['bbox']) > 0:
            extras['bbox-east-long'] = iso_values['bbox'][0]['east']
            extras['bbox-north-lat'] = iso_values['bbox'][0]['north']
            extras['bbox-south-lat'] = iso_values['bbox'][0]['south']
            extras['bbox-west-long'] = iso_values['bbox'][0]['west']

            # Construct a GeoJSON extent so ckanext-spatial can register the extent geometry
            extent_string = self.extent_template.substitute(
                    minx = extras['bbox-east-long'],
                    miny = extras['bbox-south-lat'],
                    maxx = extras['bbox-west-long'],
                    maxy = extras['bbox-north-lat']
                    )

            extras['spatial'] = extent_string.strip()
        else:
            log.debug('No spatial extent defined for this object')


        resource_locators = iso_values.get('resource-locator', []) +\
                            iso_values.get('resource-locator-identification', [])

        if len(resource_locators):
            for resource_locator in resource_locators:
                url = resource_locator.get('url','')
                if url:
                    resource_format = ''
                    resource = {}
                    if extras['resource-type'] == 'service':
                        # Check if the service is a view service
                        test_url = url.split('?')[0] if '?' in url else url
                        if self._is_wms(test_url):
                            resource['verified'] = True
                            resource['verified_date'] = datetime.now().isoformat()
                            resource_format = 'WMS'
                    if not resource_format:
                        resource_format, encoding = mimetypes.guess_type(url)

                    resource.update(
                        {
                            'url': url,
                            'name': resource_locator.get('name',''),
                            'description': resource_locator.get('description') if resource_locator.get('description') else 'Resource locator',
                            'format': resource_format or None,
                            'resource_locator_protocol': resource_locator.get('protocol',''),
                            'resource_locator_function':resource_locator.get('function','')

                        })
                    package_dict['resources'].append(resource)

            # Guess the best view service to use in WMS preview
            verified_view_resources = [r for r in package_dict['resources'] if 'verified' in r and r['format'] == 'WMS']
            if len(verified_view_resources):
                verified_view_resources[0]['ckan_recommended_wms_preview'] = True
            else:
                view_resources = [r for r in package_dict['resources'] if r['format'] == 'WMS']
                if len(view_resources):
                    view_resources[0]['ckan_recommended_wms_preview'] = True

        extras_as_dict = []
        for key, value in extras.iteritems():
            if isinstance(value, (list, dict)):
                extras_as_dict.append({'key': key, 'value': json.dumps(value)})
            else:
                extras_as_dict.append({'key': key, 'value': value})

        package_dict['extras'] = extras_as_dict

        return package_dict


    def transform_to_iso(self, original_document, original_format, harvest_object):
        '''
        Transforms an XML document to ISO 19139

        This method will be only called from the import stage if the
        harvest_object content is null and original_document and
        original_format harvest object extras exist (eg if an FGDC document
        was harvested).

        In that case, this method should do the necessary to provide an
        ISO 1939 like document, otherwise the import process will stop.


        :param original_document: Original XML document
        :type original_document: string
        :param original_format: Original format (eg 'fgdc')
        :type original_format: string
        :param harvest_object: HarvestObject domain object (with access to
            job and source objects)
        :type harvest_object: HarvestObject

        :returns: An ISO 19139 document or None if the transformation was not
            successful
        :rtype: string

        '''

        return None

    ##


    def _is_wms(self,url):
        try:
            capabilities_url = wms.WMSCapabilitiesReader().capabilities_url(url)
            res = urllib2.urlopen(capabilities_url,None,10)
            xml = res.read()

            s = wms.WebMapService(url,xml=xml)
            return isinstance(s.contents, dict) and s.contents != {}
        except Exception, e:
            log.error('WMS check for %s failed with exception: %s' % (url, str(e)))
        return False


    def _set_source_config(self, config_str):
        if config_str:
            self.source_config = json.loads(config_str)
            log.debug('Using config: %r', self.source_config)


    def _get_validator(self):
        '''
        Returns the validator object using the relevant profiles

        The profiles to be used are assigned in the following order:

        1. 'validator_profiles' property of the harvest source config object
        2. 'ckan.spatial.validator.profiles' configuration option in the ini file
        3. Default value as defined in DEFAULT_VALIDATOR_PROFILES
        '''
        if not hasattr(self, '_validator'):
            if hasattr(self, 'source_config') and self.source_config.get('validator_profiles',None):
                profiles = self.source_config.get('validator_profiles')
            elif config.get('ckan.spatial.validator.profiles', None):
                profiles = [
                    x.strip() for x in
                    config.get('ckan.spatial.validator.profiles').split(',')
                ]
            else:
                profiles = DEFAULT_VALIDATOR_PROFILES
            self._validator = Validators(profiles=profiles)
        return self._validator


    def _get_user_name(self):
        '''
        Returns the name of the user that will perform the harvesting actions
        (deleting, updating and creating datasets)

        By default this will be the internal site admin user. This is the
        recommended setting, but if necessary it can be overridden with the
        `ckanext.spatial.harvest.user_name` config option, eg to support the
        old hardcoded 'harvest' user:

           ckanext.spatial.harvest.user_name = harvest

        '''
        if self._user_name:
            return self._user_name

        config_user_name = config.get('ckanext.spatial.harvest.user_name')
        if config_user_name:
            self._user_name = config_user_name
        else:
            user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
            self._user_name = user['name']

        return self._user_name


    def _get_content(self, url):
        '''
        DEPRECATED: Use _get_content_as_unicode instead
        '''
        url = url.replace(' ','%20')
        http_response = urllib2.urlopen(url)
        return http_response.read()


    def _get_content_as_unicode(self, url):
        '''
        Get remote content as unicode.

        We let requests handle the conversion [1] , which will use the content-type
        header first or chardet if the header is missing (requests uses its own
        embedded chardet version).

        As we will be storing and serving the contents as unicode, we actually
        replace the original XML encoding declaration with an UTF-8 one.


        [1] http://github.com/kennethreitz/requests/blob/63243b1e3b435c7736acf1e51c0f6fa6666d861d/requests/models.py#L811

        '''
        url = url.replace(' ','%20')
        response = requests.get(url, timeout=10)

        content = response.text

        # Remove original XML declaration
        content = re.sub('<\?xml(.*)\?>','',content)

        # Get rid of the BOM and other rubbish at the beginning of the file
        content = re.sub('.*?<', '<', content, 1)
        content = content[content.index('<'):]

        content = u'<?xml version="1.0" encoding="UTF-8"?>\n' + content

        return content

    def _validate_document(self, document_string, harvest_object, validator=None):
        if not validator:
            validator = self._get_validator()

        document_string = re.sub('<\?xml(.*)\?>','',document_string)

        try:
            xml = etree.fromstring(document_string)
        except etree.XMLSyntaxError, e:
            self._save_object_error('Could not parse XML file: {0}'.format(str(e)), harvest_object,'Import')
            return False, None, []


        valid, profile, errors = validator.is_valid(xml)
        if not valid:
            log.error('Validation errors found using profile {0} for object with GUID {1}'.format(profile, harvest_object.guid))
            for error in errors:
                self._save_object_error(error[0], harvest_object,'Validation',line=error[1])

        return valid, profile, errors


    def import_stage(self, harvest_object):

        log = logging.getLogger(__name__ + '.import')
        log.debug('Import stage for harvest object: %s', harvest_object.id)

        if not harvest_object:
            log.error('No harvest object received')
            return False

        self._set_source_config(harvest_object.source.config)

        status = get_extra(harvest_object, 'status')

        # Get the last harvested object (if any)
        previous_object = model.Session.query(HarvestObject) \
                          .filter(HarvestObject.guid==harvest_object.guid) \
                          .filter(HarvestObject.current==True) \
                          .first()

        if status == 'delete':
            # Delete package
            context = {'model':model, 'session': model.Session, 'user': self._get_user_name()}

            get_action('package_delete')(context, {'id': harvest_object.package_id})
            log.info('Deleted package {0} with guid {1}'.format(harvest_object.package_id, harvest_object.guid))

            return True


        # Check if it is a non ISO document
        original_document = get_extra(harvest_object, 'original_document')
        original_format = get_extra(harvest_object, 'original_format')
        if original_document and original_format:
            content = self.transform_to_iso(original_document, original_format, harvest_object)
            if content:
                harvest_object.content = content
            else:
                self._save_object_error('Transformation to ISO failed for object {0}'.format(harvest_object.id), harvest_object, 'Import')
                return False
        else:
            if harvest_object.content is None:
                self._save_object_error('Empty content for object {0}'.format(harvest_object.id), harvest_object, 'Import')
                return False

            # Validate ISO document
            is_valid, profile, errors = self._validate_document(harvest_object.content, harvest_object)
            if not is_valid:
                # TODO: Provide an option to continue anyway
                return False


        # Parse ISO document
        try:
            iso_values = ISODocument(harvest_object.content).read_values()
        except Exception, e:
            self._save_object_error('Error parsing ISO document for object {0}: {1}'.format(harvest_object.id,str(e)),
                                    harvest_object,'Import')
            return False

        # Flag previous object as not current anymore
        if previous_object:
            previous_object.current = False
            previous_object.add()

        # Update GUID with the one on the document
        iso_guid = iso_values['guid']
        if iso_guid and harvest_object.guid != iso_guid:
            # First make sure there already aren't current objects
            # with the same guid
            existing_object = model.Session.query(HarvestObject.id) \
                            .filter(HarvestObject.guid==iso_guid) \
                            .filter(HarvestObject.current==True) \
                            .first()
            if existing_object:
                self._save_object_error('Object {0} already has this guid {1}'.format(existing_object.id, iso_guid),
                                    harvest_object,'Import')
                return False

            harvest_object.guid = iso_guid
            harvest_object.add()

        # Generate GUID if not present (i.e. it's a manual import)
        if not harvest_object.guid:
            m = hashlib.md5()
            m.update(harvest_object.content.encode('utf8',errors='ignore'))
            harvest_object.guid = m.hexdigest()
            harvest_object.add()

        # Get document modified date
        try:
            metadata_modified_date = dateutil.parser.parse(iso_values['metadata-date'])
        except ValueError:
            self._save_object_error('Could not extract reference date for object {0} ({1})'
                        .format(harvest_object.id, iso_values['metadata-date']), harvest_object, 'Import')
            return False

        harvest_object.metadata_modified_date = metadata_modified_date
        harvest_object.add()

        # Build the package dict
        package_dict = self.get_package_dict(iso_values, harvest_object)

        # Create / update the package

        context = {'model':model,
                   'session': model.Session,
                   'user': self._get_user_name(),
                   'extras_as_string':True, # TODO: check if needed
                   'api_version': '2',
                   'return_id_only': True}

        # The default package schema does not like Upper case tags
        tag_schema = logic.schema.default_tags_schema()
        tag_schema['name'] = [not_empty, unicode]

        # Flag this object as the current one
        harvest_object.current = True
        harvest_object.add()

        if status == 'new':
            package_schema = logic.schema.default_create_package_schema()
            package_schema['tags'] = tag_schema
            context['schema'] = package_schema

            # We need to explicitly provide a package ID, otherwise ckanext-spatial
            # won't be be able to link the extent to the package.
            package_dict['id'] = unicode(uuid.uuid4())
            package_schema['id'] = [unicode]

            # Save reference to the package on the object
            harvest_object.package_id = package_dict['id']
            harvest_object.add()
            # Defer constraints and flush so the dataset can be indexed with
            # the harvest object id (on the after_show hook from the harvester
            # plugin)
            model.Session.execute('SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED')
            model.Session.flush()

            try:
                package_id = get_action('package_create')(context, package_dict)
                log.info('Created new package %s with guid %s', package_id, harvest_object.guid)
            except ValidationError,e:
                self._save_object_error('Validation Error: %s' % str(e.error_summary), harvest_object, 'Import')
                return False

        elif status == 'change':

            # Check if the modified date is more recent
            if harvest_object.metadata_modified_date <= previous_object.metadata_modified_date:

                # Assign the previous job id to the new object to
                # avoid losing history
                harvest_object.harvest_job_id = previous_object.job.id
                harvest_object.add()

                # Delete the previous object to avoid cluttering the object table
                previous_object.delete()

                log.info('Document with GUID %s unchanged, skipping...' % (harvest_object.guid))
            else:
                package_schema = logic.schema.default_update_package_schema()
                package_schema['tags'] = tag_schema
                context['schema'] = package_schema

                package_dict['id'] = harvest_object.package_id
                try:
                    package_id = get_action('package_update')(context, package_dict)
                    log.info('Updated package %s with guid %s', package_id, harvest_object.guid)
                except ValidationError,e:
                    self._save_object_error('Validation Error: %s' % str(e.error_summary), harvest_object, 'Import')
                    return False


        model.Session.commit()


        return True
