import os
from logging import getLogger
from pylons.i18n import _
from genshi.input import HTML
from genshi.filters import Transformer

import ckan.lib.helpers as h

from ckan.lib.helpers import json

from ckan.plugins import implements, SingletonPlugin
from ckan.plugins import IRoutes, IConfigurer
from ckan.plugins import IGenshiStreamFilter

import html


log = getLogger(__name__)

class WMSPreview(SingletonPlugin):

    implements(IGenshiStreamFilter)
    implements(IRoutes, inherit=True)
    implements(IConfigurer, inherit=True)

    def filter(self, stream):
        from pylons import request, tmpl_context as c
        routes = request.environ.get('pylons.routes_dict')

        if routes.get('controller') == 'package' and \
            routes.get('action') == 'read' and c.pkg.id:

            for res in c.pkg.resources:
                if res.format == "WMS":
                    data = {'name': c.pkg.name}
                    stream = stream | Transformer('body//div[@class="resources subsection"]')\
                        .append(HTML(html.MAP_VIEW % data))

                    break



        return stream

    def before_map(self, map):

        map.redirect('/package/{id}/map','/dataset/{id}/map')
        map.connect('map_view', '/dataset/:id/map',
            controller='ckanext.spatial.controllers.view:ViewController',
            action='wms_preview')

        map.connect('proxy', '/proxy',
            controller='ckanext.spatial.controllers.view:ViewController',
            action='proxy')

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

