import re
import urllib
import urlparse

import logging

from ckan import model
from ckan.lib.helpers import json

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

from ckanext.spatial.lib.csw_client import CswService
from ckanext.spatial.harvesters.base import SpatialHarvester, text_traceback


class CSWHarvester(SpatialHarvester, SingletonPlugin):
    '''
    A Harvester for CSW servers
    '''
    implements(IHarvester)

    csw = None

    def info(self):
        return {
            'name': 'csw',
            'title': 'CSW Server',
            'description': 'A server that implements OGC\'s Catalog Service for the Web (CSW) standard'
            }

    def get_original_url(self, harvest_object_id):
        obj = model.Session.query(HarvestObject).\
                                    filter(HarvestObject.id == harvest_object_id).\
                                    first()

        parts = urlparse.urlparse(obj.source.url)

        params = {
            'SERVICE': 'CSW',
            'VERSION': '2.0.2',
            'REQUEST': 'GetRecordById',
            'OUTPUTSCHEMA': 'http://www.isotc211.org/2005/gmd',
            'OUTPUTFORMAT': 'application/xml',
            'ID': obj.guid
        }

        url = urlparse.urlunparse((
            parts.scheme,
            parts.netloc,
            parts.path,
            None,
            urllib.urlencode(params),
            None
        ))

        return url

    def output_schema(self):
        return 'gmd'

    def validate_config(self, source_config):
        source_config = super(CSWHarvester, self).validate_config(source_config)
        if not source_config:
            return source_config

        try:
            source_config_obj = json.loads(source_config)

            require_keywords = source_config_obj.get('require_keywords', None)
            if require_keywords is not None:
                if not isinstance(require_keywords, list):
                    raise ValueError('require_keywords must be a list')
                for keyword in require_keywords:
                    if not isinstance(keyword, basestring):
                        raise ValueError('require_keyword values must be strings')

            require_in_abstract = source_config_obj.get('require_in_abstract', None)
            if require_in_abstract is not None:
                if not isinstance(require_in_abstract, basestring):
                    raise ValueError('require_in_abstract must be string')

            identifier_schema = source_config_obj.get('identifier_schema', None)
            if identifier_schema is not None:
                if not isinstance(identifier_schema, basestring):
                    raise ValueError('identifier_schema must be string')

            esn = source_config_obj.get('esn', None)
            if esn is not None:
                if not isinstance(esn, basestring):
                    raise ValueError('esn must be string')

        except ValueError, e:
            raise e

        return source_config

    def gather_stage(self, harvest_job):
        log = logging.getLogger(__name__ + '.CSW.gather')
        log.debug('CswHarvester gather_stage for job: %r', harvest_job)
        # Get source URL
        url = harvest_job.source.url

        self._set_source_config(harvest_job.source.config)

        try:
            self._setup_csw_client(url)
        except Exception, e:
            self._save_gather_error('Error contacting the CSW server: %s' % e, harvest_job)
            return None

        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id). \
            filter(HarvestObject.harvest_source_id == harvest_job.source.id).\
            filter(HarvestObject.current == True) # noqa

        guid_to_package_id = {}

        for guid, package_id in query:
            guid_to_package_id[guid] = package_id

        guids_in_db = set(guid_to_package_id.keys())

        # extract cql filter if any
        cql = self.source_config.get('cql')

        log.debug('Starting gathering for %s' % url)
        guids_in_harvest = set()

        identifier_schema = self.source_config.get('identifier_schema', self.output_schema())

        try:
            for identifier in self.csw.getidentifiers(page=10, outputschema=identifier_schema, cql=cql):
                try:
                    log.info('Got identifier %s from the CSW', identifier)
                    if identifier is None:
                        log.error('CSW returned identifier %r, skipping...' % identifier)
                        continue

                    guids_in_harvest.add(identifier)
                except Exception, e:
                    self._save_gather_error('Error for the identifier %s [%r]' % (identifier, e), harvest_job)
                    continue

        except Exception, e:
            log.error('Exception: %s' % text_traceback())
            self._save_gather_error('Error gathering the identifiers from the CSW server [%s]' % str(e), harvest_job)
            return None

        new = guids_in_harvest - guids_in_db
        delete = guids_in_db - guids_in_harvest
        change = guids_in_db & guids_in_harvest

        ids = []
        for guid in new:
            obj = HarvestObject(guid=guid, job=harvest_job,
                                extras=[HOExtra(key='status', value='new')])
            obj.save()
            ids.append(obj.id)
        for guid in change:
            obj = HarvestObject(guid=guid, job=harvest_job,
                                package_id=guid_to_package_id[guid],
                                extras=[HOExtra(key='status', value='change')])
            obj.save()
            ids.append(obj.id)
        for guid in delete:
            obj = HarvestObject(guid=guid, job=harvest_job,
                                package_id=guid_to_package_id[guid],
                                extras=[HOExtra(key='status', value='delete')])
            model.Session.query(HarvestObject).\
                filter_by(guid=guid).\
                update({'current': False}, False)
            obj.save()
            ids.append(obj.id)

        if len(ids) == 0:
            self._save_gather_error('No records received from the CSW server', harvest_job)
            return None

        return ids

    def _get_extra(self, harvest_object, key):
        for extra in harvest_object.extras:
            if extra.key == key:
                return extra
        return None

    def fetch_stage(self, harvest_object):

        # Check harvest object status
        status = self._get_object_extra(harvest_object, 'status')

        if status == 'delete':
            # No need to fetch anything, just pass to the import stage
            return True

        log = logging.getLogger(__name__ + '.CSW.fetch')
        log.debug('CswHarvester fetch_stage for object: %s', harvest_object.id)

        url = harvest_object.source.url
        try:
            self._setup_csw_client(url)
        except Exception, e:
            self._save_object_error('Error contacting the CSW server: %s' % e,
                                    harvest_object)
            return False

        identifier = harvest_object.guid
        esn = self.source_config.get('esn', 'full')
        try:
            record = self.csw.getrecordbyid([identifier], outputschema=self.output_schema(), esn=esn)
        except Exception, e:
            self._save_object_error('Error getting the CSW record with GUID %s' % identifier, harvest_object)
            return False

        if record is None:
            self._save_object_error('Empty record for GUID %s' % identifier,
                                    harvest_object)
            return False

        source_config = json.loads(harvest_object.source.config) if harvest_object.source.config else {}
        require_keywords = source_config.get('require_keywords', None)
        if require_keywords:
            record_keywords = set()
            for keyword_container in record.get('identification', {}).get('keywords', []):
                keywords = keyword_container.get('keywords', None)
                if keywords and isinstance(keywords, list):
                    record_keywords.update(keywords)

            if not set(require_keywords).issubset(record_keywords):
                status_extra = self._get_extra(harvest_object, 'status')
                if status_extra is None:
                    self._save_object_error('No status set for object with GUID %s' % identifier,
                                            harvest_object)
                    return False
                status_extra.value = 'delete'
                status_extra.save()

                # Should not be processed further
                return 'unchanged'
            else:
                log.info("Found tagged record with guid %s" % identifier)

        require_in_abstract = source_config.get('require_in_abstract', None)
        if require_in_abstract:
            if not record.get('identification', {}).get('abstract', '') or\
                    require_in_abstract not in record.get('identification', {}).get('abstract', ""):
                status_extra = self._get_extra(harvest_object, 'status')
                if status_extra is None:
                    self._save_object_error('No status set for object with GUID %s' % identifier,
                                            harvest_object)
                    return False
                status_extra.value = 'delete'
                status_extra.save()

                # Should not be processed further
                return 'unchanged'
            else:
                log.info("Found tagged record with guid %s" % identifier)

        try:
            # Save the fetch contents in the HarvestObject
            # Contents come from csw_client already declared and encoded as utf-8
            # Remove original XML declaration
            content = re.sub('<\?xml(.*)\?>', '', record['xml'])

            harvest_object.content = content.strip()
            harvest_object.save()
        except Exception, e:
            self._save_object_error('Error saving the harvest object for GUID %s [%r]' %
                                    (identifier, e), harvest_object)
            return False

        log.debug('XML content saved (len %s)', len(record['xml']))
        return True

    def _setup_csw_client(self, url):
        self.csw = CswService(url)
