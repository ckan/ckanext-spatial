import hashlib
import logging

from ckan import model

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

from ckanext.spatial.harvesters.base import SpatialHarvester,  guess_standard


class DocHarvester(SpatialHarvester, SingletonPlugin):
    '''
    A Harvester for individual spatial metadata documents
    TODO: Move to new logic
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'single-doc',
            'title': 'Single spatial metadata document',
            'description': 'A single spatial metadata document'
            }


    def get_original_url(self, harvest_object_id):
        obj = model.Session.query(HarvestObject).\
                                    filter(HarvestObject.id==harvest_object_id).\
                                    first()
        if not obj:
            return None

        return obj.source.url


    def gather_stage(self,harvest_job):
        log = logging.getLogger(__name__ + '.individual.gather')
        log.debug('DocHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job

        # Get source URL
        url = harvest_job.source.url

        self._set_source_config(harvest_job.source.config)

        # Get contents
        try:
            content = self._get_content_as_unicode(url)
        except Exception,e:
            self._save_gather_error('Unable to get content for URL: %s: %r' % \
                                        (url, e),harvest_job)
            return None

        existing_object = model.Session.query(HarvestObject.guid, HarvestObject.package_id).\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id).\
                                    first()

        def create_extras(url, status):
            return [HOExtra(key='doc_location', value=url),
                    HOExtra(key='status', value=status)]

        if not existing_object:
            guid=hashlib.md5(url.encode('utf8', 'ignore')).hexdigest()
            harvest_object = HarvestObject(job=harvest_job,
                                extras=create_extras(url,
                                                     'new'),
                                guid=guid
                               )
        else:
            harvest_object = HarvestObject(job=harvest_job,
                                extras=create_extras(url,
                                                     'change'),
                                guid=existing_object.guid,
                                package_id=existing_object.package_id
                               )

        harvest_object.add()

        # Check if it is an ISO document
        document_format = guess_standard(content)
        if document_format == 'iso':
            harvest_object.content = content
        else:
            extra = HOExtra(
                    object=harvest_object,
                    key='original_document',
                    value=content)
            extra.save()

            extra = HOExtra(
                    object=harvest_object,
                    key='original_format',
                    value=document_format)
            extra.save()

        harvest_object.save()

        return [harvest_object.id]




    def fetch_stage(self,harvest_object):
        # The fetching was already done in the previous stage
        return True

