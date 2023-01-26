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

if tk.check_ckan_version(min_version="2.9.0"):
    from ckanext.spatial.plugin.flask_plugin import (
        SpatialQueryMixin, HarvestMetadataApiMixin
    )
else:
    from ckanext.spatial.plugin.pylons_plugin import (
        SpatialQueryMixin, HarvestMetadataApiMixin
    )

from ckanext.spatial.lib import normalize_bbox
from ckanext.spatial.search import search_backends

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

        pkg_dict = search_backends[search_backend]().index_dataset(pkg_dict)

        # Coupled resources are URL -> uuid links, they are not needed in SOLR
        # and might be huge if there are lot of coupled resources
        pkg_dict.pop('coupled-resource', None)
        pkg_dict.pop('extras_coupled-resource', None)

        # spatial field is geojson coordinate data, not needed in SOLR either
        pkg_dict.pop('spatial', None)
        pkg_dict.pop('extras_spatial', None)

        return pkg_dict

    def before_dataset_search(self, search_params):

        search_backend = self._get_search_backend()

        input_bbox = search_params.get('extras', {}).get('ext_bbox', None)

        if input_bbox:
            bbox = normalize_bbox(input_bbox)

            if not bbox:
                raise SearchError('Wrong bounding box provided')

            search_params = search_backends[search_backend]().search_params(
                bbox, search_params)

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
