import os
import re
from logging import getLogger
from pylons import config
from pylons.i18n import _
from genshi.input import HTML
from genshi.filters import Transformer

import ckan.lib.helpers as h

from ckan.lib.search import SearchError, PackageSearchQuery
from ckan.lib.helpers import json

from ckan import model

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes
from ckan.plugins import IConfigurable, IConfigurer
from ckan.plugins import IGenshiStreamFilter
from ckan.plugins import IPackageController

from ckan.logic import ValidationError

import html

from ckanext.spatial.lib import save_package_extent,validate_bbox, bbox_query, bbox_query_ordered
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
        if not config.get('ckan.spatial.testing',False):
            setup_model()


    def create(self, package):
        self.check_spatial_extra(package)

    def edit(self, package):
        self.check_spatial_extra(package)

    def check_spatial_extra(self,package):
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
                    except ValueError,e:
                        error_dict = {'spatial':[u'Error decoding JSON object: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except TypeError,e:
                        error_dict = {'spatial':[u'Error decoding JSON object: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                    try:
                        save_package_extent(package.id,geometry)

                    except ValueError,e:
                        error_dict = {'spatial':[u'Error creating geometry: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except Exception, e:
                        if bool(os.getenv('DEBUG')):
                            raise
                        error_dict = {'spatial':[u'Error: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                elif extra.state == 'deleted':
                    # Delete extent from table
                    save_package_extent(package.id,None)

                break


    def delete(self, package):
        save_package_extent(package.id,None)

class SpatialQuery(SingletonPlugin):

    implements(IRoutes, inherit=True)
    implements(IPackageController, inherit=True)

    def before_map(self, map):

        map.connect('api_spatial_query', '/api/2/search/{register:dataset|package}/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')
        return map

    def before_search(self,search_params):
        if 'extras' in search_params and 'ext_bbox' in search_params['extras'] \
            and search_params['extras']['ext_bbox']:

            bbox = validate_bbox(search_params['extras']['ext_bbox'])
            if not bbox:
                raise SearchError('Wrong bounding box provided')

            if 'sort' in search_params and search_params['sort'] == 'spatial desc':
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
                search_params['sort'] = None # SOLR should not sort.
                # Store the rankings of the results for this page, so for
                # after_search to construct the correctly sorted results
                rows = search_params['extras']['ext_rows'] = search_params['rows']
                start = search_params['extras']['ext_start'] = search_params['start']
                search_params['extras']['ext_spatial'] = [
                    (extent.package_id, extent.spatial_ranking) \
                    for extent in extents[start:start+rows]]
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

                q = search_params.get('q','').strip() or '""'
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

    implements(IGenshiStreamFilter)

    def filter(self, stream):
        from pylons import request, tmpl_context as c
        routes = request.environ.get('pylons.routes_dict')
        if routes.get('controller') == 'package' and \
            routes.get('action') == 'search':

            data = {
                'bbox': request.params.get('ext_bbox',''),
                'default_extent': config.get('ckan.spatial.default_map_extent','')
            }
            stream = stream | Transformer('body//div[@id="dataset-search-ext"]')\
                .append(HTML(html.SPATIAL_SEARCH_FORM % data))
            stream = stream | Transformer('head')\
                .append(HTML(html.SPATIAL_SEARCH_FORM_EXTRA_HEADER % data))
            stream = stream | Transformer('body')\
                .append(HTML(html.SPATIAL_SEARCH_FORM_EXTRA_FOOTER % data))

        return stream


class DatasetExtentMap(SingletonPlugin):

    implements(IGenshiStreamFilter)
    implements(IConfigurer, inherit=True)

    def filter(self, stream):
        from pylons import request, tmpl_context as c

        route_dict = request.environ.get('pylons.routes_dict')
        route = '%s/%s' % (route_dict.get('controller'), route_dict.get('action'))
        routes_to_filter = config.get('ckan.spatial.dataset_extent_map.routes', 'package/read').split(' ')
        if route in routes_to_filter and c.pkg.id:

            extent = c.pkg.extras.get('spatial',None)
            if extent:
                map_element_id = config.get('ckan.spatial.dataset_extent_map.element_id', 'dataset')
                title = config.get('ckan.spatial.dataset_extent_map.title', 'Geographic extent')
                body_html = html.PACKAGE_MAP_EXTENDED if title else html.PACKAGE_MAP_BASIC
                map_type = config.get('ckan.spatial.dataset_extent_map.map_type', 'osm')
                if map_type == 'osm':
                    js_library_links = '<script type="text/javascript" src="/ckanext/spatial/js/openlayers/OpenLayers_dataset_map.js"></script>'
                    map_attribution = html.MAP_ATTRIBUTION_OSM
                elif map_type == 'os':
                    js_library_links = '<script src="http://osinspiremappingprod.ordnancesurvey.co.uk/libraries/openlayers-openlayers-56e25fc/lib/OpenLayers.js" type="text/javascript"></script>'
                    map_attribution = '' # done in the js instead
                
                data = {'extent': extent,
                        'title': _(title),
                        'map_type': map_type,
                        'js_library_links': js_library_links,
                        'map_attribution': map_attribution,
                        'element_id': map_element_id}
                stream = stream | Transformer('body//div[@id="%s"]' % map_element_id)\
                         .append(HTML(body_html % data))
                stream = stream | Transformer('head')\
                    .append(HTML(html.PACKAGE_MAP_EXTRA_HEADER % data))
                stream = stream | Transformer('body')\
                    .append(HTML(html.PACKAGE_MAP_EXTRA_FOOTER % data))



        return stream

    def update_config(self, config):
        here = os.path.dirname(__file__)

        template_dir = os.path.join(here, 'templates')
        public_dir = os.path.join(here, 'public')

        if config.get('extra_template_paths'):
            config['extra_template_paths'] += ','+template_dir
        else:
            config['extra_template_paths'] = template_dir
        if config.get('extra_public_paths'):
            config['extra_public_paths'] += ','+public_dir
        else:
            config['extra_public_paths'] = public_dir

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
