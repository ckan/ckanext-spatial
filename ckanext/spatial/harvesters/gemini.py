'''
Different harvesters for spatial metadata

These are designed for harvesting GEMINI2 for the UK Location Programme
but can be easily adapted for other INSPIRE/ISO19139 XML metadata
    - GeminiCswHarvester - CSW servers
    - GeminiDocHarvester - An individual GEMINI resource
    - GeminiWafHarvester - An index page with links to GEMINI resources

'''
import os
from urlparse import urlparse
from datetime import datetime
from numbers import Number
import uuid
import logging
import difflib
import re

from lxml import etree
from sqlalchemy.sql import update, bindparam

from ckan import model
from ckan.model import Session, Package
from ckan.lib.munge import munge_title_to_name
from ckan.plugins.core import SingletonPlugin, implements
from ckan.lib.helpers import json

from ckan import logic
from ckan.logic import get_action, ValidationError
from ckan.lib.navl.validators import not_empty

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject, HarvestObjectExtra

from ckanext.spatial.model import GeminiDocument
from ckanext.spatial.lib.csw_client import CswService

from ckanext.spatial.harvesters.base import SpatialHarvester, text_traceback


log = logging.getLogger(__name__)

# When developing, it might be helpful to 'export DEBUG=1' to reraise the
# exceptions, rather them being caught.
debug_exception_mode = bool(os.getenv('DEBUG'))


class GeminiHarvester(SpatialHarvester):
    '''Base class for spatial harvesting GEMINI2 documents for the UK Location
    Programme. May be easily adaptable for other INSPIRE and spatial projects.

    All three harvesters share the same import stage
    '''


    def import_stage(self, harvest_object):
        log = logging.getLogger(__name__ + '.import')
        log.debug('Import stage for harvest object: %r', harvest_object)

        if not harvest_object:
            log.error('No harvest object received')
            return False

        self._set_source_config(harvest_object.source.config)

        # Save a reference
        self.obj = harvest_object

        if harvest_object.content is None:
            self._save_object_error('Empty content for object %s' % harvest_object.id,harvest_object,'Import')
            return False
        try:
            return self.import_gemini_object(harvest_object)
        except Exception, e:
            log.error('Exception during import: %s' % text_traceback())
            if not str(e).strip():
                self._save_object_error('Error importing Gemini document.', harvest_object, 'Import')
            else:
                self._save_object_error('Error importing Gemini document: %s' % str(e), harvest_object, 'Import')

            if debug_exception_mode:
                raise

    def import_gemini_object(self, harvest_object):
        '''Imports the Gemini metadata into CKAN.

        The harvest_source_reference is an ID that the harvest_source uses
        for the metadata document. It is the same ID the Coupled Resources
        use to link dataset and service records.

        Some errors raise Exceptions.
        '''
        gemini_string = harvest_object.content
        log = logging.getLogger(__name__ + '.import')
        xml = etree.fromstring(gemini_string)
        valid, profile, errors = self._get_validator().is_valid(xml)
        if not valid:
            out = errors[0][0] + ':\n' + '\n'.join(e[0] for e in errors[1:])
            log.error('Errors found for object with GUID %s:' % self.obj.guid)
            self._save_object_error(out,self.obj,'Import')

        if datetime.today() > datetime(2019, 12, 1) and hasattr(self, '_validator'):
            if any(schema in ['gemini2', 'gemini2-1.3'] for schema in self._validator.profiles):
                self._save_object_error('gemini2/gemini2-1.3 will be deprecated, please use gemin2-3', self.obj, 'Validation')

        unicode_gemini_string = etree.tostring(xml, encoding=unicode, pretty_print=True)

        # may raise Exception for errors
        package_dict = self.write_package_from_gemini_string(unicode_gemini_string, harvest_object)

        if package_dict:
            return True
        else:
            return 'unchanged'

    def write_package_from_gemini_string(self, content, harvest_object):
        '''Create or update a Package based on some content that has
        come from a URL.

        Returns the package_dict of the result.
        If there is an error, it returns None or raises Exception.
        '''
        log = logging.getLogger(__name__ + '.import')
        package = None
        gemini_document = GeminiDocument(content)
        gemini_values = gemini_document.read_values()
        gemini_guid = gemini_values['guid']

        # Save the metadata reference date in the Harvest Object
        try:
            metadata_modified_date = datetime.strptime(gemini_values['metadata-date'],'%Y-%m-%d')
        except ValueError:
            try:
                metadata_modified_date = datetime.strptime(gemini_values['metadata-date'],'%Y-%m-%dT%H:%M:%S')
            except:
                raise Exception('Could not extract reference date for GUID %s (%s)' \
                        % (gemini_guid,gemini_values['metadata-date']))

        self.obj.metadata_modified_date = metadata_modified_date
        self.obj.save()

        last_harvested_object = Session.query(HarvestObject) \
                            .filter(HarvestObject.guid==gemini_guid) \
                            .filter(HarvestObject.current==True) \
                            .all()

        if len(last_harvested_object) == 1:
            last_harvested_object = last_harvested_object[0]
        elif len(last_harvested_object) > 1:
                raise Exception('Application Error: more than one current record for GUID %s' % gemini_guid)

        if last_harvested_object and last_harvested_object.harvest_source_id == harvest_object.harvest_source_id:
            def get_harvest_object_url(harvest_object_id):
                return Session.query(HarvestObjectExtra.value) \
                    .filter(HarvestObjectExtra.harvest_object_id==harvest_object_id) \
                    .filter(HarvestObjectExtra.key=='url') \
                    .scalar()

            existing_source_url = get_harvest_object_url(last_harvested_object.id)
            new_source_url = get_harvest_object_url(harvest_object.id)

            if existing_source_url and existing_source_url != new_source_url:
                if last_harvested_object.package.state == u'deleted':
                    last_harvested_object.current = False
                    last_harvested_object.save()

                    last_harvested_object = None
                else:
                    raise Exception('Harvest object %s%s has a GUID %s already in use by %s%s in harvest source %s' %
                        (
                            harvest_object.id,
                            ' (%s)' % new_source_url,
                            gemini_guid,
                            last_harvested_object.id,
                            ' (%s)' % existing_source_url,
                            harvest_object.harvest_source_id
                        )
                    )

        reactivate_package = False
        if last_harvested_object:
            # We've previously harvested this (i.e. it's an update)

            self.force_import = self.force_import or getattr(harvest_object, 'force_import', False)

            # Use metadata modified date instead of content to determine if the package
            # needs to be updated
            if last_harvested_object.metadata_modified_date is None \
                or last_harvested_object.metadata_modified_date < self.obj.metadata_modified_date \
                or self.force_import \
                or (last_harvested_object.metadata_modified_date == self.obj.metadata_modified_date and
                    (last_harvested_object.content != self.obj.content or last_harvested_object.source.active is False)):

                if self.force_import:
                    log.info('Import forced for object %s with GUID %s' % (self.obj.id,gemini_guid))
                else:
                    log.info('Package for object with GUID %s needs to be created or updated' % gemini_guid)

                package = last_harvested_object.package

                # If the package has a deleted state, we will only update it and reactivate it if the
                # new document has a more recent modified date
                if package.state == u'deleted':
                    if last_harvested_object.metadata_modified_date < self.obj.metadata_modified_date:
                        log.info('Package for object with GUID %s will be re-activated' % gemini_guid)
                        reactivate_package = True
                    else:
                         log.info('Remote record with GUID %s is not more recent than a deleted package, skipping... ' % gemini_guid)
                         return None

            else:
                # The content hasn't changed, no need to update the package
                log.info('Document with GUID %s unchanged, skipping...' % (gemini_guid))
                return None
        else:
            log.info('No package with GEMINI guid %s found, let\'s create one' % gemini_guid)

        extras = {
            'UKLP': 'True',
            'harvest_object_id': self.obj.id
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
            extras[name] = gemini_values[name]

        if len(gemini_values.get('progress', [])):
            extras['progress'] = gemini_values['progress'][0]
        else:
            extras['progress'] = ''

        extras['resource-type'] = gemini_values['resource-type'][0]

        # Use-constraints can contain values which are:
        #  * free text
        #  * licence URL
        # Store all values in extra['licence'] and if there is a
        # URL in there, store that in extra['licence-url']
        extras['licence'] = gemini_values.get('use-constraints', '')
        if len(extras['licence']):
            licence_url_extracted = self._extract_first_licence_url(extras['licence'])
            if licence_url_extracted:
                extras['licence_url'] = licence_url_extracted

        extras['access_constraints'] = gemini_values.get('limitations-on-public-access','')
        if gemini_values.has_key('temporal-extent-begin'):
            #gemini_values['temporal-extent-begin'].sort()
            extras['temporal_coverage-from'] = gemini_values['temporal-extent-begin']
        if gemini_values.has_key('temporal-extent-end'):
            #gemini_values['temporal-extent-end'].sort()
            extras['temporal_coverage-to'] = gemini_values['temporal-extent-end']

        # Save responsible organization roles
        provider, responsible_parties = self._process_responsible_organisation(
            gemini_values['responsible-organisation'])
        extras['provider'] = provider
        extras['responsible-party'] = '; '.join(responsible_parties)

        if len(gemini_values['bbox']) >0:
            extras['bbox-east-long'] = gemini_values['bbox'][0]['east']
            extras['bbox-north-lat'] = gemini_values['bbox'][0]['north']
            extras['bbox-south-lat'] = gemini_values['bbox'][0]['south']
            extras['bbox-west-long'] = gemini_values['bbox'][0]['west']

            # Construct a GeoJSON extent so ckanext-spatial can register the extent geometry
            extent_string = self.extent_template.substitute(
                    xmin = extras['bbox-east-long'],
                    ymin = extras['bbox-south-lat'],
                    xmax = extras['bbox-west-long'],
                    ymax = extras['bbox-north-lat']
                    )

            extras['spatial'] = extent_string.strip()

        tags = []
        for tag in gemini_values['tags']:
            tag = tag[:50] if len(tag) > 50 else tag
            tags.append({'name':tag})

        package_dict = {
            'title': gemini_values['title'],
            'notes': gemini_values['abstract'],
            'tags': tags,
            'resources':[]
        }

        # We need to get the owner organization (if any) from the harvest
        # source dataset
        source_dataset = Package.get(harvest_object.source.id)
        if source_dataset.owner_org:
            package_dict['owner_org'] = source_dataset.owner_org

        if self.obj.source.publisher_id:
            package_dict['groups'] = [{'id':self.obj.source.publisher_id}]


        if reactivate_package:
            package_dict['state'] = u'active'

        if package is None or package.title != gemini_values['title']:
            name = self.gen_new_name(gemini_values['title'])
            if not name:
                name = self.gen_new_name(str(gemini_guid))
            if not name:
                raise Exception('Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
            package_dict['name'] = name
        else:
            package_dict['name'] = package.name

        resource_locators = gemini_values.get('resource-locator', [])

        if len(resource_locators):
            for resource_locator in resource_locators:
                url = resource_locator.get('url','')
                if url:
                    resource_format = ''
                    resource = {}
                    if extras['resource-type'] == 'service':
                        # Check if the service is a view service
                        if self._is_wms(url, harvest_object=harvest_object):
                            resource['verified'] = True
                            resource['verified_date'] = datetime.now().isoformat()
                            resource_format = 'WMS'
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
        for key,value in extras.iteritems():
            if isinstance(value,(basestring,Number)):
                extras_as_dict.append({'key':key,'value':value})
            else:
                extras_as_dict.append({'key':key,'value':json.dumps(value)})

        package_dict['extras'] = extras_as_dict

        if package == None:
            # Create new package from data.
            package = self._create_package_from_data(package_dict)
            log.info('Created new package ID %s with GEMINI guid %s', package['id'], gemini_guid)
        else:
            package = self._create_package_from_data(package_dict, package = package)
            log.info('Updated existing package ID %s with existing GEMINI guid %s', package['id'], gemini_guid)

        # Flag the other objects of this source as not current anymore
        from ckanext.harvest.model import harvest_object_table
        u = update(harvest_object_table) \
                .where(harvest_object_table.c.package_id==bindparam('b_package_id')) \
                .values(current=False)
        Session.execute(u, params={'b_package_id':package['id']})
        Session.commit()

        # Refresh current object from session, otherwise the
        # import paster command fails
        Session.remove()
        Session.add(self.obj)
        Session.refresh(self.obj)

        # Set reference to package in the HarvestObject and flag it as
        # the current one
        if not self.obj.package_id:
            self.obj.package_id = package['id']

        self.obj.current = True
        self.obj.save()

        return package

    @classmethod
    def _process_responsible_organisation(cls, responsible_organisations):
        '''Given the list of responsible_organisations and their roles,
        (extracted from the GeminiDocument) determines who the provider is
        and the list of all responsible organisations and their roles.

        :param responsible_organisations: list of dicts, each with keys
                      includeing 'organisation-name' and 'role'
        :returns: tuple of: 'provider' (string, may be empty) and
                  'responsible-parties' (list of strings)
        '''
        parties = {}
        owners = []
        publishers = []
        for responsible_party in responsible_organisations:
            if responsible_party['role'] == 'owner':
                owners.append(responsible_party['organisation-name'])
            elif responsible_party['role'] == 'publisher':
                publishers.append(responsible_party['organisation-name'])

            if responsible_party['organisation-name'] in parties:
                if not responsible_party['role'] in parties[responsible_party['organisation-name']]:
                    parties[responsible_party['organisation-name']].append(responsible_party['role'])
            else:
                parties[responsible_party['organisation-name']] = [responsible_party['role']]

        responsible_parties = []
        for party_name in parties:
            responsible_parties.append('%s (%s)' % (party_name, ', '.join(parties[party_name])))

        # Save provider in a separate extra:
        # first organization to have a role of 'owner', and if there is none, first one with
        # a role of 'publisher'
        if len(owners):
            provider = owners[0]
        elif len(publishers):
            provider = publishers[0]
        else:
            provider = u''

        return provider, responsible_parties

    def gen_new_name(self, title):
        name = munge_title_to_name(title).replace('_', '-')
        while '--' in name:
            name = name.replace('--', '-')
        like_q = "{}%".format(name)

        pkg_query = Session.query(
            Package
        ).filter(
            Package.name.ilike(like_q)
        ).order_by(
            Package.metadata_created.desc()
        ).first()

        if pkg_query:
            match = re.match(r"\D+(\d+)$", pkg_query.name)
            counter = int(match.group(1)) if match else 0

            while True:
                counter = counter + 1
                new_name = name + str(counter)

                have_name = Session.query(
                    Package
                ).filter(
                    Package.name.ilike(new_name)
                ).first()

                if not have_name:
                    return new_name

        return name

    @classmethod
    def _extract_first_licence_url(self, licences):
        '''Given a list of pieces of licence info, hunt for the first one
        which looks like a URL and return it. Otherwise returns None.'''
        for licence in licences:
            o = urlparse(licence)
            if o.scheme and o.netloc:
                return licence
        return None

    def _create_package_from_data(self, package_dict, package = None):
        '''
        {'name': 'council-owned-litter-bins',
         'notes': 'Location of Council owned litter bins within Borough.',
         'resources': [{'description': 'Resource locator',
                        'format': 'Unverified',
                        'url': 'http://www.barrowbc.gov.uk'}],
         'tags': [{'name':'Utility and governmental services'}],
         'title': 'Council Owned Litter Bins',
         'extras': [{'key':'INSPIRE','value':'True'},
                    {'key':'bbox-east-long','value': '-3.12442'},
                    {'key':'bbox-north-lat','value': '54.218407'},
                    {'key':'bbox-south-lat','value': '54.039634'},
                    {'key':'bbox-west-long','value': '-3.32485'},
                    # etc.
                    ]
        }
        '''

        if not package:
            package_schema = logic.schema.default_create_package_schema()
        else:
            package_schema = logic.schema.default_update_package_schema()

        # The default package schema does not like Upper case tags
        tag_schema = logic.schema.default_tags_schema()
        tag_schema['name'] = [not_empty,unicode]
        package_schema['tags'] = tag_schema

        context = {'model':model,
                   'session':Session,
                   'user': self._get_user_name(),
                   'schema':package_schema,
                   'extras_as_string':True,
                   'api_version': '2'}
        if not package:
            # We need to explicitly provide a package ID, otherwise ckanext-spatial
            # won't be be able to link the extent to the package.
            package_dict['id'] = unicode(uuid.uuid4())
            package_schema['id'] = [unicode]

            action_function = get_action('package_create')
        else:
            action_function = get_action('package_update')
            package_dict['id'] = package.id

        try:
            package_dict = action_function(context, package_dict)
        except ValidationError,e:
            raise Exception('Validation Error: %s' % str(e.error_summary))
            if debug_exception_mode:
                raise

        return package_dict

    def get_gemini_string_and_guid(self,content,url=None):
        '''From a string buffer containing Gemini XML, return the tree
        under gmd:MD_Metadata and the GUID for it.

        If it cannot parse the XML it will raise lxml.etree.XMLSyntaxError.
        If it cannot find the GUID element, then gemini_guid will be ''.

        :param content: string containing Gemini XML
        :param url: string giving info about the location of the XML to be
                    used only in validation errors
        :returns: (gemini_string, gemini_guid)
        '''
        xml = etree.fromstring(content)

        # The validator and GeminiDocument don\'t like the container
        metadata_tag = '{http://www.isotc211.org/2005/gmd}MD_Metadata'
        if xml.tag == metadata_tag:
            gemini_xml = xml
        else:
            gemini_xml = xml.find(metadata_tag)

        if gemini_xml is None:
            self._save_gather_error('Content is not a valid Gemini document without the gmd:MD_Metadata element', self.harvest_job)

        gemini_string = etree.tostring(gemini_xml)
        gemini_document = GeminiDocument(gemini_string)
        try:
            gemini_guid = gemini_document.read_value('guid')
        except KeyError:
            gemini_guid = None

        return gemini_string, gemini_guid

class GeminiCswHarvester(GeminiHarvester, SingletonPlugin):
    '''
    A Harvester for CSW servers
    '''
    implements(IHarvester)

    csw=None

    def info(self):
        return {
            'name': 'gemini-csw',
            'title': 'CSW Server',
            'description': 'A server that implements OGC\'s Catalog Service for the Web (CSW) standard'
            }

    def gather_stage(self, harvest_job):
        log = logging.getLogger(__name__ + '.CSW.gather')
        log.debug('GeminiCswHarvester gather_stage for job: %r', harvest_job)
        # Get source URL
        url = harvest_job.source.url

        try:
            self._setup_csw_client(url)
        except Exception, e:
            self._save_gather_error('Error contacting the CSW server: %s' % e, harvest_job)
            return None


        log.debug('Starting gathering for %s' % url)
        used_identifiers = []
        ids = []
        try:
            for identifier in self.csw.getidentifiers(page=10):
                try:
                    log.info('Got identifier %s from the CSW', identifier)
                    if identifier in used_identifiers:
                        log.error('CSW identifier %r already used, skipping...' % identifier)
                        continue
                    if identifier is None:
                        log.error('CSW returned identifier %r, skipping...' % identifier)
                        ## log an error here? happens with the dutch data
                        continue

                    # Create a new HarvestObject for this identifier
                    obj = HarvestObject(guid=identifier, job=harvest_job)
                    obj.save()

                    ids.append(obj.id)
                    used_identifiers.append(identifier)
                except Exception, e:
                    self._save_gather_error('Error for the identifier %s [%r]' % (identifier,e), harvest_job)
                    continue

        except Exception, e:
            log.error('Exception: %s' % text_traceback())
            self._save_gather_error('Error gathering the identifiers from the CSW server [%s]' % str(e), harvest_job)
            return None

        if len(ids) == 0:
            self._save_gather_error('No records received from the CSW server', harvest_job)
            return None

        return ids

    def fetch_stage(self,harvest_object):
        log = logging.getLogger(__name__ + '.CSW.fetch')
        log.debug('GeminiCswHarvester fetch_stage for object: %r', harvest_object)

        url = harvest_object.source.url
        try:
            self._setup_csw_client(url)
        except Exception, e:
            self._save_object_error('Error contacting the CSW server: %s' % e,
                                    harvest_object)
            return False

        identifier = harvest_object.guid
        try:
            record = self.csw.getrecordbyid([identifier])
        except Exception, e:
            self._save_object_error('Error getting the CSW record with GUID %s' % identifier, harvest_object)
            return False

        if record is None:
            self._save_object_error('Empty record for GUID %s' % identifier,
                                    harvest_object)
            return False

        try:
            # Contents come from csw_client already declared and encoded as utf-8
            # Remove original XML declaration
            # (copied from csw.py:179

            content = re.sub('<\?xml(.*)\?>', '', record['xml'])

            harvest_object.content = content.strip()
            harvest_object.save()
        except Exception,e:
            self._save_object_error('Error saving the harvest object for GUID %s [%r]' % \
                                    (identifier, e), harvest_object)
            return False

        log.debug('XML content saved (len %s)', len(record['xml']))
        return True

    def _setup_csw_client(self, url):
        self.csw = CswService(url)


class GeminiDocHarvester(GeminiHarvester, SingletonPlugin):
    '''
    A Harvester for individual GEMINI documents
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'gemini-single',
            'title': 'Single GEMINI 2 document',
            'description': 'A single GEMINI 2.1 document'
            }

    def gather_stage(self,harvest_job):
        log = logging.getLogger(__name__ + '.individual.gather')
        log.debug('GeminiDocHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job

        # Get source URL
        url = harvest_job.source.url

        # Get contents
        try:
            content = self._get_content_as_unicode(url)
        except Exception,e:
            self._save_gather_error('Unable to get content for URL: %s: %r' % \
                                        (url, e),harvest_job)
            return None
        try:
            # We need to extract the guid to pass it to the next stage
            gemini_string, gemini_guid = self.get_gemini_string_and_guid(content,url)

            if gemini_guid:
                # Create a new HarvestObject for this identifier
                # Generally the content will be set in the fetch stage, but as we alredy
                # have it, we might as well save a request
                obj = HarvestObject(guid=gemini_guid,
                                    job=harvest_job,
                                    content=gemini_string,
                                    extras=[HarvestObjectExtra(key='url', value=url)])
                obj.save()

                log.info('Got GUID %s' % gemini_guid)
                return [obj.id]
            else:
                self._save_gather_error('Could not get the GUID for source %s' % url, harvest_job)
                return None
        except Exception, e:
            self._save_gather_error('Error parsing the document. Is this a valid Gemini document?: %s [%r]'% (url,e),harvest_job)
            if debug_exception_mode:
                raise
            return None


    def fetch_stage(self,harvest_object):
        # The fetching was already done in the previous stage
        return True


class GeminiWafHarvester(GeminiHarvester, SingletonPlugin):
    '''
    A Harvester from a WAF server containing GEMINI documents.
    e.g. Apache serving a directory of GEMINI files.
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'gemini-waf',
            'title': 'Web Accessible Folder (WAF) - GEMINI',
            'description': 'A Web Accessible Folder (WAF) displaying a list of GEMINI 2.1 documents'
            }

    def gather_stage(self,harvest_job):
        log = logging.getLogger(__name__ + '.WAF.gather')
        log.debug('GeminiWafHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job

        # Get source URL
        url = harvest_job.source.url

        # Get contents
        try:
            content = self._get_content_as_unicode(url)
        except Exception,e:
            self._save_gather_error('Unable to get content for URL: %s: %r' % \
                                        (url, e),harvest_job)
            return None
        ids = []
        try:
            for url in self._extract_urls(content, url):
                try:
                    content = self._get_content_as_unicode(url)
                except Exception, e:
                    msg = 'Couldn\'t harvest WAF link: %s: %s' % (url, e)
                    self._save_gather_error(msg,harvest_job)
                    continue
                else:
                    # We need to extract the guid to pass it to the next stage
                    try:
                        gemini_string, gemini_guid = self.get_gemini_string_and_guid(content,url)
                        if gemini_guid:
                            log.debug('Got GUID %s' % gemini_guid)
                            # Create a new HarvestObject for this identifier
                            # Generally the content will be set in the fetch stage, but as we alredy
                            # have it, we might as well save a request
                            obj = HarvestObject(guid=gemini_guid,
                                                job=harvest_job,
                                                content=gemini_string,
                                                extras=[HarvestObjectExtra(key='url', value=url)])
                            obj.save()

                            ids.append(obj.id)


                    except Exception,e:
                        msg = 'Could not get GUID for source %s: %r' % (url,e)
                        self._save_gather_error(msg,harvest_job)
                        continue
        except Exception, e:
            msg = 'Error extracting URLs from %s' % url
            self._save_gather_error(msg,harvest_job)
            return None

        if len(ids) > 0:
            return ids
        else:
            self._save_gather_error('Couldn\'t find any links to metadata files',
                                     harvest_job)
            return None

    def fetch_stage(self,harvest_object):
        # The fetching was already done in the previous stage
        return True


    def _extract_urls(self, content, base_url):
        '''
        Get the URLs out of a WAF index page
        '''
        try:
            parser = etree.HTMLParser()
            tree = etree.fromstring(content, parser=parser)
        except Exception, inst:
            msg = 'Couldn\'t parse content into a tree: %s: %s' \
                  % (inst, content)
            raise Exception(msg)
        urls = []
        for url in tree.xpath('//a/@href'):
            url = url.strip()
            if not url:
                continue
            if '?' in url:
                self.log_error('Ignoring link in WAF because it has "?": {}', url)
                continue
            if '/' in url:
                self.log_error('Ignoring link in WAF because it has "/": {}', url)
                continue
            if '#' in url:
                self.log_error('Ignoring link in WAF because it has "#": {}', url)
                continue
            if 'mailto:' in url:
                self.log_error('Ignoring link in WAF because it has "mailto": {}', url)
                continue
            if 'tel:' in url:
                self.log_error('Ignoring link in WAF because it has "tel": {}', url)
                continue
            log.debug('WAF contains file: %s', url)
            urls.append(url)
        base_url = base_url.rstrip('/').split('/')
        if 'index' in base_url[-1]:
            base_url.pop()
        base_url = '/'.join(base_url)
        base_url += '/'
        log.debug('WAF base URL: %s', base_url)
        return [base_url + i for i in urls]

    def log_error(self, msg, url):
        msg = msg.format(url)
        log.debug(msg)

        # potential GEMINI doc which may have invalid characters 
        # as part of the URL should be reported back to users to fix
        if url.endswith('.xml'):
            self._save_gather_error(msg, self.harvest_job)
