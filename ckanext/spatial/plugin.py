import os
from logging import getLogger

from genshi.input import HTML
from genshi.filters import Transformer

import ckan.lib.helpers as h

from ckan.lib.helpers import json

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes, IConfigurer
from ckan.plugins import IConfigurable, IGenshiStreamFilter
from ckan.plugins import IPackageController

from ckan.logic import ValidationError
from ckan.logic.action.update import package_error_summary

import html

from ckanext.spatial.lib import save_package_extent

log = getLogger(__name__)

class SpatialQuery(SingletonPlugin):

    implements(IRoutes, inherit=True)
    implements(IPackageController, inherit=True)

    def before_map(self, map):

        map.connect('api_spatial_query', '/api/2/search/package/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')

        return map

    def create(self, package):
        self.check_spatial_extra(package)

    def edit(self, package):
        self.check_spatial_extra(package)

    def check_spatial_extra(self,package):
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
                        error_dict = {'spatial':[u'Error: %s' % str(e)]}
                        raise ValidationError(error_dict, error_summary=package_error_summary(error_dict))

                elif extra.state == 'deleted':
                    # Delete extent from table
                    save_package_extent(package.id,None)

                break


    def delete(self, package):
        save_package_extent(package.id,None)


class WMSPreview(SingletonPlugin):

    implements(IGenshiStreamFilter)
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)

    def filter(self, stream):
        from pylons import request, tmpl_context as c
        routes = request.environ.get('pylons.routes_dict')

        if routes.get('controller') == 'package' and \
            routes.get('action') == 'read' and c.pkg.id:

            is_inspire = (c.pkg.extras.get('INSPIRE') == 'True')
            # TODO: What about WFS, WCS...
            is_wms = (c.pkg.extras.get('resource-type') == 'service')
            if is_inspire and is_wms:
                data = {'name': c.pkg.name}
                stream = stream | Transformer('body//div[@class="resources subsection"]')\
                    .append(HTML(html.MAP_VIEW % data))


        return stream

    def before_map(self, map):

        map.connect('map_view', '/package/:id/map',
            controller='ckanext.spatial.controllers.view:ViewController',
            action='wms_preview')

        map.connect('proxy', '/proxy',
            controller='ckanext.spatial.controllers.view:ViewController',
            action='proxy')

        map.connect('api_spatial_query', '/api/2/search/package/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')

        return map

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

