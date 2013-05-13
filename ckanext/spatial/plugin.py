import os
import re
from logging import getLogger

from pylons import config

from ckan import plugins as p

from ckan.lib.search import SearchError, PackageSearchQuery
from ckan.lib.helpers import json

from ckanext.spatial.lib import save_package_extent,validate_bbox, bbox_query, bbox_query_ordered
from ckanext.spatial.model.package_extent import setup as setup_model

log = getLogger(__name__)

def package_error_summary(error_dict):
    ''' Do some i18n stuff on the error_dict keys '''

    def prettify(field_name):
        field_name = re.sub('(?<!\w)[Uu]rl(?!\w)', 'URL',
                            field_name.replace('_', ' ').capitalize())
        return p.toolkit._(field_name.replace('_', ' '))

    summary = {}
    for key, error in error_dict.iteritems():
        if key == 'resources':
            summary[p.toolkit._('Resources')] = p.toolkit._('Package resource(s) invalid')
        elif key == 'extras':
            summary[p.toolkit._('Extras')] = p.toolkit._('Missing Value')
        elif key == 'extras_validation':
            summary[p.toolkit._('Extras')] = error[0]
        else:
            summary[p.toolkit._(prettify(key))] = error[0]
    return summary

class SpatialMetadata(p.SingletonPlugin):

    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)

    def configure(self, config):

        if not p.toolkit.asbool(config.get('ckan.spatial.testing', 'False')):
            setup_model()

    def update_config(self, config):
        ''' Set up the resource library, public directory and
        template directory for all the spatial extensions
        '''
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-spatial')

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
                if extra.state == 'active' and extra.value:
                    try:
                        log.debug('Received: %r' % extra.value)
                        geometry = json.loads(extra.value)
                    except ValueError,e:
                        error_dict = {'spatial':[u'Error decoding JSON object: %s' % str(e)]}
                        raise p.toolkit.ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except TypeError,e:
                        error_dict = {'spatial':[u'Error decoding JSON object: %s' % str(e)]}
                        raise p.toolkit.ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                    try:
                        save_package_extent(package.id,geometry)

                    except ValueError,e:
                        error_dict = {'spatial':[u'Error creating geometry: %s' % str(e)]}
                        raise p.toolkit.ValidationError(error_dict, error_summary=package_error_summary(error_dict))
                    except Exception, e:
                        if bool(os.getenv('DEBUG')):
                            raise
                        error_dict = {'spatial':[u'Error: %s' % str(e)]}
                        raise p.toolkit.ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                elif (extra.state == 'active' and not extra.value) or extra.state == 'deleted':
                    # Delete extent from table
                    save_package_extent(package.id,None)

                break


    def delete(self, package):
        save_package_extent(package.id,None)

    ## ITemplateHelpers

    def get_helpers(self):
        from ckanext.spatial import helpers as spatial_helpers
        return {
                'get_reference_date' : spatial_helpers.get_reference_date,
                'get_responsible_party': spatial_helpers.get_responsible_party,
                }

class SpatialQuery(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IPackageController, inherit=True)

    def before_map(self, map):

        map.connect('api_spatial_query', '/api/2/search/{register:dataset|package}/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')
        return map

    def before_index(self, pkg_dict):
        from shapely.geometry import asShape
        if 'extras_spatial' in pkg_dict and config.get('ckanext.spatial.search_backend') == 'solr':
            try:
                geometry = json.loads(pkg_dict['extras_spatial'])
            except ValueError, e:
                log.error('Geometry not valid GeoJSON, not indexing')
                return pkg_dict
            # Check wrong bboxes (4 same points)
            if geometry['type'] == 'Polygon' and len(geometry['coordinates'][0]) == 5:
                x = [p[0] for p in geometry['coordinates'][0]]
                y = [p[1] for p in geometry['coordinates'][0]]

                if x.count(x[0]) == 5 and y.count(y[0]) == 5:
                    geometry = {'type': 'Point', 'coordinates': [x[0], y[0]]}

            shape = asShape(geometry)
            if not shape.is_valid:
                log.error('Wrong geometry, not indexing')
                return pkg_dict

            pkg_dict['spatial_geom'] = shape.wkt
        return pkg_dict


    def before_search(self,search_params):
        if 'extras' in search_params and 'ext_bbox' in search_params['extras'] \
            and search_params['extras']['ext_bbox']:

            bbox = validate_bbox(search_params['extras']['ext_bbox'])
            if not bbox:
                raise SearchError('Wrong bounding box provided')

            if config.get('ckanext.spatial.search_backend') == 'solr':
                search_params = self._params_for_solr_search(bbox, search_params)
            else:
                search_params = self._params_for_postgis_search(bbox, search_params)

        return search_params

    def _params_for_solr_search(self, bbox, search_params):
        search_params['fq'] += ' +spatial_geom:"Intersects({minx} {miny} {maxx} {maxy})"' \
                .format(minx=bbox['minx'],miny=bbox['miny'],maxx=bbox['maxx'],maxy=bbox['maxy'])

        #TODO: sorting

        return search_params

    def _params_for_postgis_search(self, bbox, search_params):

        # Note: This will be deprecated at some point in favour of the
        # Solr 4 spatial sorting capabilities
        if search_params['sort'] == 'spatial desc' and \
           p.toolkit.asbool(config.get('ckanext.spatial.use_postgis_sorting', 'False')):
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

        # Note: This will be deprecated at some point in favour of the
        # Solr 4 spatial sorting capabilities

        if search_params.get('extras', {}).get('ext_spatial') and \
           p.toolkit.asbool(config.get('ckanext.spatial.use_postgis_sorting', 'False')):
            # Apply the spatial sort
            querier = PackageSearchQuery()
            pkgs = []
            for package_id, spatial_ranking in search_params['extras']['ext_spatial']:
                # get package from SOLR
                pkg = querier.get_index(package_id)['data_dict']
                pkgs.append(json.loads(pkg))
            search_results['results'] = pkgs
        return search_results


class CatalogueServiceWeb(p.SingletonPlugin):
    p.implements(p.IConfigurable)
    p.implements(p.IRoutes)

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

class HarvestMetadataApi(p.SingletonPlugin):
    '''
    Harvest Metadata API
    (previously called "InspireApi")

    A way for a user to view the harvested metadata XML, either as a raw file or
    styled to view in a web browser.
    '''
    p.implements(p.IRoutes)

    def before_map(self, route_map):
        controller = "ckanext.spatial.controllers.api:HarvestMetadataApiController"

        # Showing the harvest object content is an action of the default
        # harvest plugin, so just redirect there
        route_map.redirect('/api/2/rest/harvestobject/{id:.*}/xml',
            '/harvest/object/{id}',
            _redirect_code='301 Moved Permanently')

        route_map.connect('/harvest/object/{id}/original', controller=controller,
                          action='display_xml_original')

        route_map.connect('/harvest/object/{id}/html', controller=controller,
                          action='display_html')
        route_map.connect('/harvest/object/{id}/html/original', controller=controller,
                          action='display_html_original')

        # Redirect old URL to a nicer and unversioned one
        route_map.redirect('/api/2/rest/harvestobject/:id/html',
           '/harvest/object/{id}/html',
            _redirect_code='301 Moved Permanently')

        return route_map

    def after_map(self, route_map):
        return route_map
