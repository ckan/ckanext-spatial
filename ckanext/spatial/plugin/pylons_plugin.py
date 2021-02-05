import ckan.plugins as p



class SpatialQueryMixin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes
    def before_map(self, map):

        map.connect('api_spatial_query', '/api/2/search/{register:dataset|package}/geo',
            controller='ckanext.spatial.controllers.api:ApiController',
            action='spatial_query')
        return map

class HarvestMetadataApiMixin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

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
