import os
import mimetypes
from logging import getLogger

import six
import geojson

import shapely.geometry
try:
    from shapely.errors import GeometryTypeError
except ImportError:
    # Previous version of shapely uses ValueError and TypeError
    GeometryTypeError = (ValueError, TypeError)

import ckantoolkit as tk

from ckan import plugins as p
from ckan.lib.search import SearchError

from ckan.lib.helpers import json
from ckanext.spatial.lib import normalize_bbox, fit_bbox, fit_linear_ring

if tk.check_ckan_version(min_version="2.9.0"):
    from ckanext.spatial.plugin.flask_plugin import (
        SpatialQueryMixin, HarvestMetadataApiMixin
    )
else:
    from ckanext.spatial.plugin.pylons_plugin import (
        SpatialQueryMixin, HarvestMetadataApiMixin
    )

config = tk.config

log = getLogger(__name__)

DEFAULT_SEARCH_BACKEND = "solr-bbox"
ALLOWED_SEARCH_BACKENDS = [
    "solr",         # Deprecated, please update to "solr-bbox"
    "solr-bbox",
    "solr-spatial-field",
    "postgis",      # Deprecated: will be removed in the next version
]


class SpatialMetadata(p.SingletonPlugin):

    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers, inherit=True)

    use_postgis = False

    # IConfigurable

    def configure(self, config):

        # PostGIS is no longer required, support for it will be dropped in the future
        self.use_postgis = tk.asbool(config.get("ckan.spatial.use_postgis", False))

        if self.use_postgis:

            from ckanext.spatial.postgis.model import setup as setup_model

            if not tk.asbool(config.get("ckan.spatial.testing", False)):
                log.debug("Setting up the spatial model")
                setup_model()

    # IConfigure

    def update_config(self, config):
        ''' Set up the resource library, public directory and
        template directory for all the spatial extensions
        '''
        tk.add_public_directory(config, '../public')
        tk.add_template_directory(config, '../templates')
        tk.add_resource('../public', 'ckanext-spatial')

        # Add media types for common extensions not included in the mimetypes
        # module
        mimetypes.add_type('application/json', '.geojson')
        mimetypes.add_type('application/gml+xml', '.gml')

    # IPackageController

    def after_create(self, context, data_dict):
        return self.after_dataset_create(context, data_dict)

    def after_dataset_create(self, context, data_dict):
        self.check_spatial_extra(data_dict)

    def after_update(self, context, data_dict):
        return self.after_dataset_update(context, data_dict)

    def after_dataset_update(self, context, data_dict):
        self.check_spatial_extra(data_dict, update=True)

    def after_delete(self, context, data_dict):
        return self.after_dataset_delete(context, data_dict)

    def after_dataset_delete(self, context, data_dict):

        if self.use_postgis:
            from ckanext.spatial.postgis.model import save_package_extent
            save_package_extent(data_dict["id"], None)

    def check_spatial_extra(self, dataset_dict, update=False):
        '''
        For a given dataset, looks at the spatial extent (as given in the
        "spatial" field/extra in GeoJSON format) and stores it in the database.
        '''

        dataset_id = dataset_dict["id"]
        geometry = dataset_dict.get("spatial")
        delete = False

        if not geometry:
            # Check extras
            for extra in dataset_dict.get("extras", []):
                if extra["key"] == "spatial":
                    if extra.get("deleted"):
                        delete = True
                    else:
                        geometry = extra["value"]

        if ((geometry is None or geometry == "" or delete)
                and update
                and self.use_postgis):
            from ckanext.spatial.postgis.model import save_package_extent
            save_package_extent(dataset_id, None)
            return
        elif not geometry:
            return

        # Check valid JSON
        try:
            log.debug("Received geometry: {}".format(geometry))

            geometry = geojson.loads(six.text_type(geometry))
        except ValueError as e:
            error_dict = {
                "spatial": ["Error decoding JSON object: {}".format(six.text_type(e))]}
            raise tk.ValidationError(error_dict)

        if not hasattr(geometry, "is_valid") or not geometry.is_valid:
            msg = "Error: Wrong GeoJSON object"
            if hasattr(geometry, "errors"):
                msg = msg + ": {}".format(geometry.errors())
            error_dict = {"spatial": [msg]}
            raise tk.ValidationError(error_dict)

        if self.use_postgis:
            from ckanext.spatial.postgis.model import save_package_extent
            try:
                save_package_extent(dataset_id, geometry)
            except Exception as e:
                if bool(os.getenv('DEBUG')):
                    raise
                error_dict = {"spatial": ["Error: {}".format(six.text_type(e))]}
                raise tk.ValidationError(error_dict)

    # ITemplateHelpers

    def get_helpers(self):
        from ckanext.spatial import helpers as spatial_helpers
        return {
            "get_reference_date": spatial_helpers.get_reference_date,
            "get_responsible_party": spatial_helpers.get_responsible_party,
            "get_common_map_config": spatial_helpers.get_common_map_config,
        }


class SpatialQuery(SpatialQueryMixin, p.SingletonPlugin):

    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IConfigurer, inherit=True)

    def _get_search_backend(self):
        search_backend = config.get(
            "ckanext.spatial.search_backend", DEFAULT_SEARCH_BACKEND)

        if search_backend not in ALLOWED_SEARCH_BACKENDS:
            raise ValueError(
                "Unknown spatial search backend: {}. Allowed values are: {}".format(
                    search_backend, ALLOWED_SEARCH_BACKENDS)
            )

        if search_backend == "solr":
            log.warning(
                "The `solr` spatial search backend has been renamed to `solr-bbox`, "
                "please update your configuration"
            )
            search_backend = "solr-bbox"

        elif search_backend == "postgis":
            log.warning(
                "The `postgis` spatial search backend is deprecated "
                "and will be removed in future versions"
            )

        return search_backend

    # IConfigure

    def update_config(self, config):

        self._get_search_backend()

    # IPackageController

    def before_index(self, pkg_dict):
        return self.before_dataset_index(pkg_dict)

    def before_search(self, search_params):
        return self.before_dataset_search(search_params)

    def after_search(self, search_results, search_params):
        return self.after_dataset_search(search_results, search_params)

    def before_dataset_index(self, pkg_dict):

        search_backend = self._get_search_backend()

        if search_backend not in ("solr-bbox", "solr-spatial-field"):
            return pkg_dict

        if not pkg_dict.get('extras_spatial'):
            return pkg_dict

        # Coupled resources are URL -> uuid links, they are not needed in SOLR
        # and might be huge if there are lot of coupled resources
        pkg_dict.pop('coupled-resource', None)
        pkg_dict.pop('extras_coupled-resource', None)

        # spatial field is geojson coordinate data, not needed in SOLR either
        geom_from_metadata = pkg_dict.pop('spatial', None)
        pkg_dict.pop('extras_spatial', None)

        try:
            geometry = json.loads(geom_from_metadata)
        except (AttributeError, ValueError) as e:
            log.error('Geometry not valid JSON {}, not indexing :: {}'.format(e, geom_from_metadata[:100]))
            return pkg_dict

        try:
            shape = shapely.geometry.shape(geometry)
        except GeometryTypeError as e:
            log.error('{}, not indexing :: {}'.format(e, geom_from_metadata[:100]))
            return pkg_dict

        if search_backend == "solr-bbox":
            # We always index the envelope of the geometry regardless of
            # if it's an actual bounding box (polygon)

            bounds = shape.bounds
            bbox = fit_bbox(normalize_bbox(list(bounds)))

            pkg_dict["spatial_bbox"] = "ENVELOPE({minx}, {maxx}, {maxy}, {miny})".format(
                **bbox)

        elif search_backend == 'solr-spatial-field':
            wkt = None

            # We allow multiple geometries as GeometryCollections
            if geometry['type'] == 'GeometryCollection':
                geometries = geometry['geometries']
            else:
                geometries = [geometry]

            # Check potential problems with bboxes in each geometry
            wkt = []
            for geom in geometries:
                if geom['type'] == 'Polygon' \
                and len(geom['coordinates']) == 1 \
                and len(geom['coordinates'][0]) == 5:

                    # Check wrong bboxes (4 same points)
                    xs = [p[0] for p in geom['coordinates'][0]]
                    ys = [p[1] for p in geom['coordinates'][0]]

                    if xs.count(xs[0]) == 5 and ys.count(ys[0]) == 5:
                        wkt.append('POINT({x} {y})'.format(x=xs[0], y=ys[0]))
                    else:
                        # Check if coordinates are defined counter-clockwise,
                        # otherwise we'll get wrong results from Solr
                        lr = shapely.geometry.polygon.LinearRing(geom['coordinates'][0])
                        lr_coords = (
                            list(lr.coords) if lr.is_ccw
                            else list(reversed(list(lr.coords)))
                        )
                        polygon = shapely.geometry.polygon.Polygon(
                            fit_linear_ring(lr_coords))
                        wkt.append(polygon.wkt)

            if not wkt:
                shape = shapely.geometry.shape(geometry)
                if not shape.is_valid:
                    log.error('Wrong geometry, not indexing')
                    return pkg_dict
                if shape.bounds[0] < -180 or shape.bounds[2] > 180:
                    log.error("""
Geometries outside the -180, -90, 180, 90 boundaries are not supported,
you need to split the geometry in order to fit the parts. Not indexing""")
                    return pkg_dict
                wkt = shape.wkt

            pkg_dict['spatial_geom'] = wkt

        return pkg_dict

    def before_dataset_search(self, search_params):

        search_backend = self._get_search_backend()

        input_bbox = search_params.get('extras', {}).get('ext_bbox', None)

        if input_bbox:
            bbox = normalize_bbox(input_bbox)
            if not bbox:
                raise SearchError('Wrong bounding box provided')

            if search_backend in ("solr-bbox", "solr-spatial-field"):

                bbox = fit_bbox(bbox)

                if not search_params.get("fq_list"):
                    search_params["fq_list"] = []

                spatial_field = (
                    "spatial_bbox" if search_backend == "solr-bbox" else "spatial_geom"
                )

                default_spatial_query = "{{!field f={spatial_field}}}Intersects(ENVELOPE({minx}, {maxx}, {maxy}, {miny}))"

                spatial_query = config.get(
                    "ckanext.spatial.solr_query", default_spatial_query)

                search_params["fq_list"].append(
                    spatial_query.format(
                        spatial_field=spatial_field, **bbox)
                )

            elif search_backend == 'postgis':
                search_params = self._params_for_postgis_search(bbox, search_params)

        return search_params

    def _params_for_postgis_search(self, bbox, search_params):
        """
        Note: The PostGIS search functionality will be removed in future versions
        """
        from ckanext.spatial.postgis.model import bbox_query, bbox_query_ordered
        from ckan.lib.search import SearchError

        # Adjust easting values
        while (bbox['minx'] < -180):
            bbox['minx'] += 360
            bbox['maxx'] += 360
        while (bbox['minx'] > 180):
            bbox['minx'] -= 360
            bbox['maxx'] -= 360

        # Note: This will be deprecated at some point in favour of the
        # Solr 4 spatial sorting capabilities
        if search_params.get('sort') == 'spatial desc' and \
           tk.asbool(config.get('ckanext.spatial.use_postgis_sorting', 'False')):
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
            # Note: `"" AND` query doesn't work in github ci
            new_q = '%s AND ' % q if q and q != '""' else ''
            new_q += '(%s)' % ' OR '.join(['id:%s' % id for id in bbox_query_ids])

            search_params['q'] = new_q

        return search_params

    def after_dataset_search(self, search_results, search_params):
        """
        Note: The PostGIS search functionality will be removed in future versions
        """
        from ckan.lib.search import PackageSearchQuery

        search_backend = self._get_search_backend()
        if search_backend == "postgis":
            # Note: This will be deprecated at some point in favour of the
            # Solr 4 spatial sorting capabilities
            if search_params.get('extras', {}).get('ext_spatial') and \
               tk.asbool(config.get('ckanext.spatial.use_postgis_sorting', 'False')):
                # Apply the spatial sort
                querier = PackageSearchQuery()
                pkgs = []
                for package_id, spatial_ranking in search_params['extras']['ext_spatial']:
                    # get package from SOLR
                    pkg = querier.get_index(package_id)['data_dict']
                    pkgs.append(json.loads(pkg))
                search_results['results'] = pkgs
        return search_results


class HarvestMetadataApi(HarvestMetadataApiMixin, p.SingletonPlugin):
    '''
    Harvest Metadata API
    (previously called "InspireApi")

    A way for a user to view the harvested metadata XML, either as a raw file or
    styled to view in a web browser.
    '''
    pass
