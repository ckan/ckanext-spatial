import os
import re
from logging import getLogger

from pylons import config
from pylons.i18n import _

import ckan.plugins.toolkit as toolkit
from ckan.lib.search import SearchError, PackageSearchQuery
from ckan.lib.helpers import json

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes
from ckan.plugins import IConfigurable, IConfigurer
from ckan.plugins import ITemplateHelpers
from ckan.plugins import IPackageController

from ckan.logic import ValidationError

from ckanext.spatial.lib import save_package_extent, validate_bbox, bbox_query, bbox_query_ordered
from ckanext.spatial.model.package_extent import setup as setup_model

log = getLogger(__name__)


def package_error_summary(error_dict):
    ''' Do some i18n stuff on the error_dict keys '''

    def prettify(field_name):
        field_name = re.sub('(?<!\w)[Uu]rl(?!\w)', 'URL',
                            field_name.replace('_', ' ').capitalize())
        return _(field_name.replace('_', ' '))

    summary = {}
    for key, error in error_dict.iteritems():
        if key == 'resources':
            summary[_('Resources')] = _('Package resource(s) invalid')
        elif key == 'extras':
            summary[_('Extras')] = _('Missing Value')
        elif key == 'extras_validation':
            summary[_('Extras')] = error[0]
        else:
            summary[_(prettify(key))] = error[0]
    return summary


class SpatialMetadata(SingletonPlugin):

    implements(IPackageController, inherit=True)
    implements(IConfigurable, inherit=True)

    def configure(self, config):
        if not config.get('ckan.spatial.testing', False):
            setup_model()

    def create(self, package):
        self.check_spatial_extra(package)

    def edit(self, package):
        self.check_spatial_extra(package)

    def check_spatial_extra(self, package):
        '''
        For a given package, looks at the spatial extent (as given in the
        extra "spatial" in GeoJSON format) and records it in PostGIS.
        '''
        if not package.id:
            log.warning('Couldn\'t store spatial extent because no id was provided for the package')
            return

        # TODO: deleted extra
        for extra in package.extras_list:
            if extra.key == 'spatial':
                if extra.state == 'active':
                    try:
                        log.debug('Received: %r' % extra.value)
                        geometry = json.loads(extra.value)
                    except ValueError as e:
                        error_dict = {'spatial': [u'Error decoding JSON object: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except TypeError as e:
                        error_dict = {'spatial': [u'Error decoding JSON object: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                    try:
                        save_package_extent(package.id, geometry)

                    except ValueError as e:
                        error_dict = {'spatial': [u'Error creating geometry: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except Exception as e:
                        if bool(os.getenv('DEBUG')):
                            raise
                        error_dict = {'spatial': [u'Error: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                elif extra.state == 'deleted':
                    # Delete extent from table
                    save_package_extent(package.id, None)

                break

    def delete(self, package):
        save_package_extent(package.id, None)


class SpatialQuery(SingletonPlugin):

    implements(IRoutes, inherit=True)
    implements(IPackageController, inherit=True)

    def before_map(self, map):

        map.connect('api_spatial_query', '/api/2/search/{register:dataset|package}/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')
        return map

    def before_search(self, search_params):
        if ('extras' in search_params and 'ext_bbox' in search_params['extras'] and
                search_params['extras']['ext_bbox']):

            bbox = validate_bbox(search_params['extras']['ext_bbox'])
            if not bbox:
                raise SearchError('Wrong bounding box provided')

            if search_params['sort'] == 'spatial desc':
                if search_params['q'] or search_params['fq']:
                    raise SearchError('Spatial ranking cannot be mixed with other search parameters')
                    # ...because it is too inefficient to use SOLR to filter
                    # results and return the entire set to this class and
                    # after_search do the sorting and paging.
                extents = bbox_query_ordered(bbox)
                are_no_results = not extents
                search_params['extras']['ext_rows'] = search_params['rows']
                search_params['extras']['ext_start'] = search_params['start']
                # this SOLR query needs to return no actual results since
                # they are in the wrong order anyway. We just need this SOLR
                # query to get the count and facet counts.
                rows = 0
                search_params['sort'] = None  # SOLR should not sort.
                # Store the rankings of the results for this page, so for
                # after_search to construct the correctly sorted results
                rows = search_params['extras']['ext_rows'] = search_params['rows']
                start = search_params['extras']['ext_start'] = search_params['start']
                search_params['extras']['ext_spatial'] = [
                    ((extent.package_id, extent.spatial_ranking)
                        for extent in extents[start:start + rows])]
            else:
                extents = bbox_query(bbox)
                are_no_results = extents.count() == 0

            if are_no_results:
                # We don't need to perform the search
                search_params['abort_search'] = True
            else:
                # We'll perform the existing search but also filtering by the ids
                # of datasets within the bbox
                bbox_query_ids = [extent.package_id for extent in extents]

                q = search_params.get('q', '').strip() or '""'
                new_q = '%s AND ' % q if q else ''
                new_q += '(%s)' % ' OR '.join(['id:%s' % id for id in bbox_query_ids])

                search_params['q'] = new_q

        return search_params

    def after_search(self, search_results, search_params):
        if search_params.get('extras', {}).get('ext_spatial'):
            # Apply the spatial sort
            querier = PackageSearchQuery()
            pkgs = []
            for package_id, spatial_ranking in search_params['extras']['ext_spatial']:
                # get package from SOLR
                pkg = querier.get_index(package_id)['data_dict']
                pkgs.append(json.loads(pkg))
            search_results['results'] = pkgs
        return search_results


class SpatialQueryWidget(SingletonPlugin):
    """
    Requires DatasetExtentMap to be present
    because its update_config needs to be called
    """
    implements(ITemplateHelpers)

    @classmethod
    def spatial_config(cls, data):
        return config.get('ckan.spatial.%s' % data)

    def get_helpers(self):
        return {'spatial_config': self.spatial_config}


class DatasetExtentMap(SingletonPlugin):

    implements(ITemplateHelpers)
    implements(IConfigurer, inherit=True)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))

        our_public_dir = os.path.join(rootdir, 'ckanext', 'spatial',
                'public')
        template_dir = os.path.join(rootdir, 'ckanext', 'spatial',
                'templates')
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])
        config['extra_template_paths'] = ','.join([template_dir,
                config.get('extra_template_paths', '')])

        toolkit.add_resource('public', 'ckanext-spatial')

    @classmethod
    def get_spatial(cls, pkg):
        spatial = pkg.extras.get('spatial', None)
        if spatial:
            return {
                'extent': json.dumps(str(spatial)),
                'title': config.get('ckan.spatial.dataset_extent_map.title', 'Geographic extent')
            }
        return None

    def get_helpers(self):
        return {'get_spatial': self.get_spatial}


class CatalogueServiceWeb(SingletonPlugin):
    implements(IConfigurable)
    implements(IRoutes)

    def configure(self, config):
        config.setdefault("cswservice.title", "Untitled Service - set cswservice.title in config")
        config.setdefault("cswservice.abstract", "Unspecified service description - set cswservice.abstract in config")
        config.setdefault("cswservice.keywords", "")
        config.setdefault("cswservice.keyword_type", "theme")
        config.setdefault("cswservice.provider_name", "Unnamed provider - set cswservice.provider_name in config")
        config.setdefault("cswservice.contact_name", "No contact - set cswservice.contact_name in config")
        config.setdefault("cswservice.contact_position", "")
        config.setdefault("cswservice.contact_voice", "")
        config.setdefault("cswservice.contact_fax", "")
        config.setdefault("cswservice.contact_address", "")
        config.setdefault("cswservice.contact_city", "")
        config.setdefault("cswservice.contact_region", "")
        config.setdefault("cswservice.contact_pcode", "")
        config.setdefault("cswservice.contact_country", "")
        config.setdefault("cswservice.contact_email", "")
        config.setdefault("cswservice.contact_hours", "")
        config.setdefault("cswservice.contact_instructions", "")
        config.setdefault("cswservice.contact_role", "")

        config["cswservice.rndlog_threshold"] = float(config.get("cswservice.rndlog_threshold", "0.01"))

    def before_map(self, route_map):
        c = "ckanext.spatial.controllers.csw:CatalogueServiceWebController"
        route_map.connect("/csw", controller=c, action="dispatch_get",
                          conditions={"method": ["GET"]})
        route_map.connect("/csw", controller=c, action="dispatch_post",
                          conditions={"method": ["POST"]})

        return route_map

    def after_map(self, route_map):
        return route_map


class HarvestMetadataApi(SingletonPlugin):
    '''
    Harvest Metadata API
    (previously called "InspireApi")

    A way for a user to view the harvested metadata XML, either as a raw file or
    styled to view in a web browser.
    '''
    implements(IRoutes)

    def before_map(self, route_map):
        controller = "ckanext.spatial.controllers.api:HarvestMetadataApiController"

        route_map.connect("/api/2/rest/harvestobject/:id/xml", controller=controller,
                          action="display_xml")
        route_map.connect("/api/2/rest/harvestobject/:id/html", controller=controller,
                          action="display_html")

        return route_map

    def after_map(self, route_map):
        return route_map
