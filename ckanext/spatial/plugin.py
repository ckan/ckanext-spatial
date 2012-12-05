import os
import re
from logging import getLogger

from pylons import config
from genshi.input import HTML
from genshi.filters import Transformer

from ckan import plugins as p

from ckan.lib.search import SearchError
from ckan.lib.helpers import json

import html

from ckanext.spatial.lib import save_package_extent,validate_bbox, bbox_query
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
                if extra.state == 'active':
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

                elif extra.state == 'deleted':
                    # Delete extent from table
                    save_package_extent(package.id,None)

                break


    def delete(self, package):
        save_package_extent(package.id,None)

class SpatialQuery(p.SingletonPlugin):

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IPackageController, inherit=True)

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

            extents = bbox_query(bbox)

            if extents.count() == 0:
                # We don't need to perform the search
                search_params['abort_search'] = True
            else:
                # We'll perform the existing search but also filtering by the ids
                # of datasets within the bbox
                bbox_query_ids = [extent.package_id for extent in extents]

                q = search_params.get('q','')
                new_q = '%s AND ' % q if q else ''
                new_q += '(%s)' % ' OR '.join(['id:%s' % id for id in bbox_query_ids])

                search_params['q'] = new_q

        return search_params

class SpatialQueryWidget(p.SingletonPlugin):

    p.implements(p.IGenshiStreamFilter)

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

        route_map.connect("/api/2/rest/harvestobject/:id/xml", controller=controller,
                          action="display_xml")
        route_map.connect("/api/2/rest/harvestobject/:id/html", controller=controller,
                          action="display_html")

        return route_map

    def after_map(self, route_map):
        return route_map
