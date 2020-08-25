import logging
import hashlib
import os
from sqlalchemy.orm import aliased

from ckan import model

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

from ckanext.spatial.harvesters.base import SpatialHarvester, guess_standard

log = logging.getLogger(__name__)


class FileSystemHarvester(SpatialHarvester, SingletonPlugin):
    '''
    A Harvester for local filesystem directory containing spatial metadata documents.
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'filesystem',
            'title': 'Spatial metadata on Local Filesystem',
            'description': 'A local filesystem directory containing a list of spatial metadata documents'
            }

    def get_original_url(self, harvest_object_id):
        url = model.Session.query(HOExtra.value).\
                                    filter(HOExtra.key=='lfs_filename').\
                                    filter(HOExtra.harvest_object_id==harvest_object_id).\
                                    first()

        return url[0] if url else None

    def gather_stage(self, harvest_job, collection_package_id=None):
        log = logging.getLogger(__name__ + '.LFS.gather')
        log.debug('LFSHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job
        self._set_source_config(harvest_job.source.config)

        # URL is the source directory
        source_dir = harvest_job.source.url

        # Get all files in the source directory
        files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir,f))]
        url_to_modified_harvest = {file:os.path.getmtime(os.path.join(source_dir, file)) for file in files}  # mapping of url to last_modified in harvest

        #  Get current harvest object out of db
        url_to_modified_db = {} # mapping of url to last_modified in db
        url_to_ids = {} # mapping of url to guid in db

        HOExtraAlias1 = aliased(HOExtra)
        HOExtraAlias2 = aliased(HOExtra)
        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id, HOExtraAlias1.value, HOExtraAlias2.value).\
                                    join(HOExtraAlias1, HarvestObject.extras).\
                                    join(HOExtraAlias2, HarvestObject.extras).\
                                    filter(HOExtraAlias1.key == 'lfs_modified_date').\
                                    filter(HOExtraAlias2.key == 'lfs_filename').\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id)

        for guid, package_id, modified_date, url in query:
            url_to_modified_db[url] = modified_date
            url_to_ids[url] = (guid, package_id)

        ######  Compare source and db ######
        harvest_locations = set(url_to_modified_harvest.keys())
        old_locations = set(url_to_modified_db.keys())

        new = harvest_locations - old_locations
        delete = old_locations - harvest_locations
        possible_changes = old_locations & harvest_locations
        change = []

        log.debug('LFSHarvester gather: found all:{all} old:{old} check:{check}'.format(
            all=len(files),
            old=len(delete),
            check=len(possible_changes)
        ))

        for item in possible_changes:
            if (not url_to_modified_harvest[item]
                    or not url_to_modified_db[item]  # if there is no date assume change
                    or url_to_modified_harvest[item] > url_to_modified_db[item]):
                change.append(item)

        def create_extras(path, filename, date, status):
            extras = [HOExtra(key='lfs_modified_date', value=date),
                      HOExtra(key='lfs_filepath', value=path),
                      HOExtra(key='lfs_filename', value=filename),
                      HOExtra(key='status', value=status)]
            if collection_package_id:
                extras.append(
                    HOExtra(key='collection_package_id',
                            value=collection_package_id)
                )
            return extras

        ids = []
        for location in new:
            guid=hashlib.md5(location.encode('utf8','ignore')).hexdigest()
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras(source_dir, location,
                                                     url_to_modified_harvest[location],
                                                     'new'),
                                guid=guid
                               )
            obj.save()
            ids.append(obj.id)

        for location in change:
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras(source_dir, location,
                                                     url_to_modified_harvest[location],
                                                     'change'),
                                guid=url_to_ids[location][0],
                                package_id=url_to_ids[location][1],
                               )
            obj.save()
            ids.append(obj.id)

        for location in delete:
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras('', '', '', 'delete'),
                                guid=url_to_ids[location][0],
                                package_id=url_to_ids[location][1],
                               )
            model.Session.query(HarvestObject).\
                  filter_by(guid=url_to_ids[location][0]).\
                  update({'current': False}, False)

            obj.save()
            ids.append(obj.id)

        if len(ids) > 0:
            log.debug('{0} objects sent to the next stage: {1} new, {2} change, {3} delete'.format(
                len(ids), len(new), len(change), len(delete)))
            return ids
        else:
            self._save_gather_error('No records to change',
                                     harvest_job)
            return []

    def fetch_stage(self, harvest_object):

        # Check harvest object status
        status = self._get_object_extra(harvest_object,'status')

        if status == 'delete':
            # No need to fetch anything, just pass to the import stage
            return True

        # We need to fetch the remote document

        # Get location
        filename = self._get_object_extra(harvest_object, 'lfs_filename')
        filepath = self._get_object_extra(harvest_object, 'lfs_filepath')
        if not filename or not filepath:
            self._save_object_error(
                    'No filename or path defined for object {0}'.format(harvest_object.id),
                    harvest_object)
            return False

        fullpath = os.path.join(filepath, filename)

        # Get contents
        try:
            with open(fullpath) as reader:
                content = reader.read()
        except Exception as e:
            msg = 'FSHarvester: Could not read file {0}: {1}'.format(fullpath, e)
            self._save_object_error(msg, harvest_object)
            return False

        # Check if it is an ISO document
        document_format = guess_standard(content)
        if document_format == 'iso':
            harvest_object.content = content
            harvest_object.save()
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

        return True
