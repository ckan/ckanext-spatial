# TODO: Move these to ckanext-geoviews

import mimetypes
from logging import getLogger

from ckan import plugins as p


log = getLogger(__name__)


class DataViewBase(p.SingletonPlugin):
    '''This base class is for view extensions. '''
    if p.toolkit.check_ckan_version(min_version='2.3'):
        p.implements(p.IResourceView, inherit=True)
    else:
        p.implements(p.IResourcePreview, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)

    proxy_is_enabled = False
    same_domain = False

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('public', 'ckanext-spatial')

        config['ckan.resource_proxy_enabled'] = p.plugin_loaded('resource_proxy')

    def configure(self, config):
        enabled = config.get('ckan.resource_proxy_enabled', False)
        self.proxy_is_enabled = enabled

    def setup_template_variables(self, context, data_dict):
        import ckanext.resourceproxy.plugin as proxy
        self.same_domain = data_dict['resource'].get('on_same_domain')
        if self.proxy_is_enabled and not self.same_domain:
            data_dict['resource']['original_url'] = data_dict['resource']['url']
            data_dict['resource']['url'] = proxy.get_proxified_resource_url(data_dict)



class WMSView(DataViewBase):
    WMS = ['wms']

    # IResourceView (CKAN >=2.3)
    def info(self):
        return {'name': 'wms_view',
                'title': 'WMS',
                'icon': 'map-marker',
                'iframed': True,
                'default_title': p.toolkit._('WMS'),
                }

    def can_view(self, data_dict):
        resource = data_dict['resource']
        format_lower = resource['format'].lower()

        if format_lower in self.WMS:
            return self.same_domain or self.proxy_is_enabled
        return False

    def view_template(self, context, data_dict):
        return 'dataviewer/wms.html'

    # IResourcePreview (CKAN < 2.3)

    def can_preview(self, data_dict):
        format_lower = data_dict['resource']['format'].lower()

        correct_format = format_lower in self.WMS
        can_preview_from_domain = self.proxy_is_enabled or data_dict['resource']['on_same_domain']
        quality = 2

        if p.toolkit.check_ckan_version('2.1'):
            if correct_format:
                if can_preview_from_domain:
                    return {'can_preview': True, 'quality': quality}
                else:
                    return {'can_preview': False,
                            'fixable': 'Enable resource_proxy',
                            'quality': quality}
            else:
                return {'can_preview': False, 'quality': quality}

        return correct_format and can_preview_from_domain

    def preview_template(self, context, data_dict):
        return 'dataviewer/wms.html'

    def setup_template_variables(self, context, data_dict):
        import ckanext.resourceproxy.plugin as proxy
        self.same_domain = data_dict['resource'].get('on_same_domain')
        if self.proxy_is_enabled and not self.same_domain:
            data_dict['resource']['proxy_url'] = proxy.get_proxified_resource_url(data_dict)

        else:
            data_dict['resource']['proxy_url'] = data_dict['resource']['url']


class WMSPreview(WMSView):
    pass


class GeoJSONView(DataViewBase):
    p.implements(p.ITemplateHelpers, inherit=True)

    GeoJSON = ['gjson', 'geojson']

    def update_config(self, config):
        ''' Set up the resource library, public directory and
        template directory for the preview
        '''

        mimetypes.add_type('application/json', '.geojson')

    # IResourceView (CKAN >=2.3)
    def info(self):
        return {'name': 'geojson_view',
                'title': 'GeoJSON',
                'icon': 'map-marker',
                'iframed': True,
                'default_title': p.toolkit._('GeoJSON'),
                }

    def can_view(self, data_dict):
        resource = data_dict['resource']
        format_lower = resource['format'].lower()

        if format_lower in self.GeoJSON:
            return self.same_domain or self.proxy_is_enabled
        return False

    def view_template(self, context, data_dict):
        return 'dataviewer/geojson.html'

    # IResourcePreview (CKAN < 2.3)

    def can_preview(self, data_dict):
        format_lower = data_dict['resource']['format'].lower()

        correct_format = format_lower in self.GeoJSON
        can_preview_from_domain = self.proxy_is_enabled or data_dict['resource']['on_same_domain']
        quality = 2

        if p.toolkit.check_ckan_version('2.1'):
            if correct_format:
                if can_preview_from_domain:
                    return {'can_preview': True, 'quality': quality}
                else:
                    return {'can_preview': False,
                            'fixable': 'Enable resource_proxy',
                            'quality': quality}
            else:
                return {'can_preview': False, 'quality': quality}

        return correct_format and can_preview_from_domain

    def preview_template(self, context, data_dict):
        return 'dataviewer/geojson.html'

    # ITemplateHelpers

    def get_helpers(self):
        from ckanext.spatial import helpers as spatial_helpers

        # CKAN does not allow to define two helpers with the same name
        # As this plugin can be loaded independently of the main spatial one
        # We define a different helper pointing to the same function
        return {
                'get_common_map_config_geojson' : spatial_helpers.get_common_map_config,
                }

class GeoJSONPreview(GeoJSONView):
    pass
