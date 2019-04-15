import re
import urllib
import urlparse
from string import Template
import uuid
import hashlib
import dateutil
import mimetypes
import logging

from pylons import config

from ckan import plugins as p
from ckan import model
from ckan import logic
from ckan.lib.helpers import json
from ckan.lib.navl.validators import not_empty
from ckan.lib.search.index import PackageSearchIndex
from ckanext.harvest.harvesters.base import munge_tag

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

from ckanext.spatial.lib.csw_client import CswService
from ckanext.spatial.harvesters.base import SpatialHarvester, text_traceback

from ckanext.spatial.model import FGDCDocument
from ckanext.spatial.interfaces import ISpatialHarvester


def guess_resource_format(url, use_mimetypes=True):
    '''
    Given a URL try to guess the best format to assign to the resource

    The function looks for common patterns in popular geospatial services and
    file extensions, so it may not be 100% accurate. It just looks at the
    provided URL, it does not attempt to perform any remote check.

    if 'use_mimetypes' is True (default value), the mimetypes module will be
    used if no match was found before.

    Returns None if no format could be guessed.

    '''
    url = url.lower().strip()

    resource_types = {
        # OGC
        'wms': ('service=wms', 'geoserver/wms', 'mapserver/wmsserver', 'com.esri.wms.Esrimap', 'service/wms'),
        'wfs': ('service=wfs', 'geoserver/wfs', 'mapserver/wfsserver', 'com.esri.wfs.Esrimap'),
        'wcs': ('service=wcs', 'geoserver/wcs', 'imageserver/wcsserver', 'mapserver/wcsserver'),
        'sos': ('service=sos',),
        'csw': ('service=csw',),
        # ESRI
        'kml': ('mapserver/generatekml',),
        'arcims': ('com.esri.esrimap.esrimap',),
        'arcgis_rest': ('arcgis/rest/services',),
    }

    for resource_type, parts in resource_types.iteritems():
        if any(part in url for part in parts):
            return resource_type

    file_types = {
        'kml' : ('kml',),
        'kmz': ('kmz',),
        'gml': ('gml',),
    }

    for file_type, extensions in file_types.iteritems():
        if any(url.endswith(extension) for extension in extensions):
            return file_type

    resource_format, encoding = mimetypes.guess_type(url)
    if resource_format:
        return resource_format

    return None


class CSWFGDCHarvester(SpatialHarvester, SingletonPlugin):
    '''
    A Harvester for CSW servers
    '''
    implements(IHarvester)

    csw=None

    def info(self):
        return {
            'name': 'csw_fgdc',
            'title': 'CSW FGDC Server',
            'description': 'A server that implements OGC\'s Catalog Service for the Web (CSW) standard'
            }


    def get_original_url(self, harvest_object_id):
        obj = model.Session.query(HarvestObject).\
                                    filter(HarvestObject.id==harvest_object_id).\
                                    first()

        parts = urlparse.urlparse(obj.source.url)

        params = {
            'SERVICE': 'CSW',
            'VERSION': '2.0.2',
            'REQUEST': 'GetRecordById',
            'OUTPUTSCHEMA': 'http://www.opengis.net/cat/csw/csdgm',
            'OUTPUTFORMAT':'application/xml' ,
            'ELEMENTSETNAME':'full',
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
        return 'fgdc'

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

        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id).\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id)
        guid_to_package_id = {}

        for guid, package_id in query:
            guid_to_package_id[guid] = package_id

        guids_in_db = set(guid_to_package_id.keys())

        # extract cql filter if any
        cql = self.source_config.get('cql')

        log.debug('Starting gathering for %s' % url)
        guids_in_harvest = set()
        try:
            for identifier in self.csw.getidentifiers(page=10, outputschema=self.output_schema(), cql=cql):
                try:
                    log.info('Got identifier %s from the CSW', identifier)
                    if identifier is None:
                        log.error('CSW returned identifier %r, skipping...' % identifier)
                        continue

                    guids_in_harvest.add(identifier)
                except Exception, e:
                    self._save_gather_error('Error for the identifier %s [%r]' % (identifier,e), harvest_job)
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

    def fetch_stage(self,harvest_object):

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
        record = self.csw.getrecordbyid([identifier], outputschema=self.output_schema())

        if record is None:
            self._save_object_error('Empty record for GUID %s' % identifier,
                                    harvest_object)
            return False

        try:
            # Save the fetch contents in the HarvestObject
            # Contents come from csw_client already declared and encoded as utf-8
            # Remove original XML declaration
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

    def import_stage(self, harvest_object):
        context = {
            'model': model,
            'session': model.Session,
            'user': self._get_user_name(),
        }

        log = logging.getLogger(__name__ + '.import')
        log.debug('Import stage for harvest object: %s', harvest_object.id)

        if not harvest_object:
            log.error('No harvest object received')
            return False

        self._set_source_config(harvest_object.source.config)

        if self.force_import:
            status = 'change'
        else:
            status = self._get_object_extra(harvest_object, 'status')

        # Get the last harvested object (if any)
        previous_object = model.Session.query(HarvestObject) \
                          .filter(HarvestObject.guid==harvest_object.guid) \
                          .filter(HarvestObject.current==True) \
                          .first()

        if status == 'delete':
            # Delete package
            context.update({
                'ignore_auth': True,
            })
            p.toolkit.get_action('package_delete')(context, {'id': harvest_object.package_id})
            log.info('Deleted package {0} with guid {1}'.format(harvest_object.package_id, harvest_object.guid))

            return True

        # Parse as FGDC document
        try:
            fgdc_parser = FGDCDocument(harvest_object.content)
            fgdc_values = fgdc_parser.read_values()
        except Exception, e:
            self._save_object_error('Error parsing FGDC document for object {0}: {1}'.format(harvest_object.id, str(e)),
                                    harvest_object, 'Import')
            return False

        # Flag previous object as not current anymore
        if previous_object and not self.force_import:
            previous_object.current = False
            previous_object.add()

        # Update GUID with the one on the document
        fgdc_guid = fgdc_values['guid']
        if fgdc_guid and harvest_object.guid != fgdc_guid:
            # First make sure there already aren't current objects
            # with the same guid
            existing_object = model.Session.query(HarvestObject.id) \
                            .filter(HarvestObject.guid==fgdc_guid) \
                            .filter(HarvestObject.current==True) \
                            .first()
            if existing_object:
                self._save_object_error('Object {0} already has this guid {1}'.format(existing_object.id, fgdc_guid),
                        harvest_object, 'Import')
                return False

            harvest_object.guid = fgdc_guid
            harvest_object.add()

        # Generate GUID if not present (i.e. it's a manual import)
        if not harvest_object.guid:
            m = hashlib.md5()
            m.update(harvest_object.content.encode('utf8', 'ignore'))
            harvest_object.guid = m.hexdigest()
            harvest_object.add()

        # Get document modified date
        try:
            metadata_modified_date = dateutil.parser.parse(fgdc_values['metadata-date'], ignoretz=True)
        except ValueError:
            self._save_object_error('Could not extract reference date for object {0} ({1})'
                        .format(harvest_object.id, fgdc_values['metadata-date']), harvest_object, 'Import')
            return False

        harvest_object.metadata_modified_date = metadata_modified_date
        harvest_object.add()


        # Build the package dict
        package_dict = self.get_package_dict(fgdc_values, harvest_object)
        for harvester in p.PluginImplementations(ISpatialHarvester):
            package_dict = harvester.get_package_dict(context, {
                'package_dict': package_dict,
                'fgdc_values': fgdc_values,
                'xml_tree': fgdc_parser.xml_tree,
                'harvest_object': harvest_object,
            })
        if not package_dict:
            log.error('No package dict returned, aborting import for object {0}'.format(harvest_object.id))
            return False

        # Create / update the package
        context.update({
           'extras_as_string': True,
           'api_version': '2',
           'return_id_only': True})

        if self._site_user and context['user'] == self._site_user['name']:
            context['ignore_auth'] = True


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
                package_id = p.toolkit.get_action('package_create')(context, package_dict)
                log.info('Created new package %s with guid %s', package_id, harvest_object.guid)
            except p.toolkit.ValidationError, e:
                self._save_object_error('Validation Error: %s' % str(e.error_summary), harvest_object, 'Import')
                return False

        elif status == 'change':

            # Check if the modified date is more recent
            if not self.force_import and previous_object and harvest_object.metadata_modified_date <= previous_object.metadata_modified_date:

                # Assign the previous job id to the new object to
                # avoid losing history
                harvest_object.harvest_job_id = previous_object.job.id
                harvest_object.add()

                # Delete the previous object to avoid cluttering the object table
                previous_object.delete()

                # Reindex the corresponding package to update the reference to the
                # harvest object
                if ((config.get('ckanext.spatial.harvest.reindex_unchanged', True) != 'False'
                    or self.source_config.get('reindex_unchanged') != 'False')
                    and harvest_object.package_id):
                    context.update({'validate': False, 'ignore_auth': True})
                    try:
                        package_dict = logic.get_action('package_show')(context,
                            {'id': harvest_object.package_id})
                    except p.toolkit.ObjectNotFound:
                        pass
                    else:
                        for extra in package_dict.get('extras', []):
                            if extra['key'] == 'harvest_object_id':
                                extra['value'] = harvest_object.id
                        if package_dict:
                            package_index = PackageSearchIndex()
                            package_index.index_package(package_dict)

                log.info('Document with GUID %s unchanged, skipping...' % (harvest_object.guid))
            else:
                package_schema = logic.schema.default_update_package_schema()
                package_schema['tags'] = tag_schema
                context['schema'] = package_schema

                package_dict['id'] = harvest_object.package_id
                try:
                    package_id = p.toolkit.get_action('package_update')(context, package_dict)
                    log.info('Updated package %s with guid %s', package_id, harvest_object.guid)
                except p.toolkit.ValidationError, e:
                    self._save_object_error('Validation Error: %s' % str(e.error_summary), harvest_object, 'Import')
                    return False

        model.Session.commit()

        return True


    def get_package_dict(self, fgdc_values, harvest_object):
        '''
        Constructs a package_dict suitable to be passed to package_create or
        package_update. See documentation on
        ckan.logic.action.create.package_create for more details

        Extensions willing to modify the dict should do so implementing the
        ISpatialHarvester interface

            import ckan.plugins as p
            from ckanext.spatial.interfaces import ISpatialHarvester

            class MyHarvester(p.SingletonPlugin):

                p.implements(ISpatialHarvester, inherit=True)

                def get_package_dict(self, context, data_dict):

                    package_dict = data_dict['package_dict']

                    package_dict['extras'].append(
                        {'key': 'my-custom-extra', 'value': 'my-custom-value'}
                    )

                    return package_dict

        If a dict is not returned by this function, the import stage will be cancelled.

        :param fgdc_values: Dictionary with parsed values from the ISO 19139
            XML document
        :type fgdc_values: dict
        :param harvest_object: HarvestObject domain object (with access to
            job and source objects)
        :type harvest_object: HarvestObject

        :returns: A dataset dictionary (package_dict)
        :rtype: dict
        '''

        log = logging.getLogger(__name__ + '.import')

        tags = []

        if 'tags' in fgdc_values:
            do_clean = self.source_config.get('clean_tags')
            tags_val = [munge_tag(tag) if do_clean else tag[:100] for tag in fgdc_values['tags']]
            tags = [{'name': tag} for tag in tags_val]

        # Add default_tags from config
        default_tags = self.source_config.get('default_tags', [])
        if default_tags:
            for tag in default_tags:
                tags.append({'name': tag})

        # Adding default_groups from config
        groups = []
        default_groups = self.source_config.get('default_groups', [])
        if default_groups:
            for group_id in default_groups:
                context = {'model': model, 'user': p.toolkit.c.user}
                try:
                    group = p.toolkit.get_action('group_show')(context, {'id': group_id})
                    groups.append({'id': group['id'], 'name': group['name']})
                except p.toolkit.ObjectNotFound, e:
                    log.error('Default group %s not found, proceeding without.' % group_id)

        package_dict = {
            'title': fgdc_values['title'],
            'notes': fgdc_values['abstract'],
            'tags': tags,
            'resources': [],
            'groups': groups
        }

        # set default values from config
        default_values = self.source_config.get('default_values',[])
        if default_values:
            for default_field in default_values:
                for key in default_field:
                    package_dict[key] = default_field[key]

        # We need to get the owner organization (if any) from the harvest
        # source dataset
        source_dataset = model.Package.get(harvest_object.source.id)
        if source_dataset.owner_org:
            package_dict['owner_org'] = source_dataset.owner_org

        # Package name
        package = harvest_object.package
        if package is None or package.title != fgdc_values['title']:
            name = self._gen_new_name(fgdc_values['title'])
            if not name:
                name = self._gen_new_name(str(fgdc_values['guid']))
            if not name:
                raise Exception('Could not generate a unique name from the title or the GUID. Please choose a more unique title.')
            package_dict['name'] = name
        else:
            package_dict['name'] = package.name

        extras = {
            'guid': harvest_object.guid,
            'spatial_harvester': True,
        }

        # Just add some of the metadata as extras, not the whole lot
        for name in [
            # Essentials
            'guid',
            # Usefuls
            'metadata-date',  # Released
        ]:
            extras[name] = fgdc_values[name]


        # Graphic preview
        browse_graphic = fgdc_values.get('browse-graphic')
        if browse_graphic:
            browse_graphic = browse_graphic[0]
            extras['graphic-preview-file'] = browse_graphic.get('file')
            if browse_graphic.get('description'):
                extras['graphic-preview-description'] = browse_graphic.get('description')
            if browse_graphic.get('type'):
                extras['graphic-preview-type'] = browse_graphic.get('type')


        if len(fgdc_values['bbox']) > 0:
            bbox = fgdc_values['bbox'][0]

            try:
                xmin = float(bbox['west'])
                xmax = float(bbox['east'])
                ymin = float(bbox['south'])
                ymax = float(bbox['north'])
            except ValueError, e:
                self._save_object_error('Error parsing bounding box value: {0}'.format(str(e)),
                                    harvest_object, 'Import')
            else:
                # Construct a GeoJSON extent so ckanext-spatial can register the extent geometry

                # Some publishers define the same two corners for the bbox (ie a point),
                # that causes problems in the search if stored as polygon
                if xmin == xmax or ymin == ymax:
                    extent_string = Template('{"type": "Point", "coordinates": [$x, $y]}').substitute(
                        x=xmin, y=ymin
                    )
                    self._save_object_error('Point extent defined instead of polygon',
                                     harvest_object, 'Import')
                else:
                    extent_string = self.extent_template.substitute(
                        xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax
                    )

                extras['spatial'] = extent_string.strip()
        else:
            log.debug('No spatial extent defined for this object')

        ea_list = fgdc_values.get('entity-and-attribute', [])
        resource_locators = fgdc_values.get('resource-locator', [])

        if len(resource_locators):
            for index, resource_locator in enumerate(resource_locators):
                url = resource_locator.get('url', '').strip()
                if url:
                    res_name = resource_locator.get('format-name', 'Unnamed resource')
                    res_description = resource_locator.get('format-info-content', '')
                    if len(ea_list) > 0 and index < len(ea_list):
                        ea_info = ea_list[index]
                        res_name = ea_info.get('entity-type-label')
                        res_description = ea_info.get('entity-type-definition')

                    resource = {}
                    res_format = guess_resource_format(url)
                    if not res_format:
                        res_format = guess_resource_format(res_name)
                    resource['format'] = res_format

                    resource.update({
                        'url': url,
                        'name': res_name,
                        'description': res_description,
                        'url_type': 'xloader',
                    })
                    package_dict['resources'].append(resource)


        # Add default_extras from config
        default_extras = self.source_config.get('default_extras',{})
        if default_extras:
           override_extras = self.source_config.get('override_extras',False)
           for key,value in default_extras.iteritems():
              log.debug('Processing extra %s', key)
              if not key in extras or override_extras:
                 # Look for replacement strings
                 if isinstance(value,basestring):
                    value = value.format(harvest_source_id=harvest_object.job.source.id,
                             harvest_source_url=harvest_object.job.source.url.strip('/'),
                             harvest_source_title=harvest_object.job.source.title,
                             harvest_job_id=harvest_object.job.id,
                             harvest_object_id=harvest_object.id)
                 extras[key] = value

        extras_as_dict = []
        for key, value in extras.iteritems():
            if isinstance(value, (list, dict)):
                extras_as_dict.append({'key': key, 'value': json.dumps(value)})
            else:
                extras_as_dict.append({'key': key, 'value': value})

        package_dict['extras'] = extras_as_dict

        return package_dict
