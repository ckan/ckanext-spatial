# -*- coding: utf-8 -*-

import logging

from flask import Blueprint, make_response
from lxml import etree
from pkg_resources import resource_stream

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckan.common import request, config
from ckan.model import Session
from ckan.views.api import _finish_ok, _finish_bad_request

from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query

from six import StringIO

log = logging.getLogger(__name__)

api = Blueprint("spatial_api", __name__)


def spatial_query(register):
    error_400_msg = \
        'Please provide a suitable bbox parameter [minx,miny,maxx,maxy]'

    if 'bbox' not in request.args:
        return _finish_bad_request(error_400_msg)

    bbox = validate_bbox(request.params['bbox'])

    if not bbox:
        return _finish_bad_request(error_400_msg)

    srid = get_srid(request.args.get('crs')) if 'crs' in \
        request.args else None

    extents = bbox_query(bbox, srid)

    ids = [extent.package_id for extent in extents]
    output = dict(count=len(ids), results=ids)

    return _finish_ok(output)


api.add_url_rule('/api/2/search/<register>/geo', view_func=spatial_query)

harvest_metadata = Blueprint("spatial_harvest_metadata", __name__)


def harvest_object_redirect_xml(id):
    return h.redirect_to('/harvest/object/{}'.format(id))


def harvest_object_redirect_html(id):
    return h.redirect_to('/harvest/object/{}/html'.format(id))


def _get_original_content(id):
    from ckanext.harvest.model import HarvestObject, HarvestObjectExtra

    extra = Session.query(
        HarvestObjectExtra
    ).join(HarvestObject).filter(HarvestObject.id == id).filter(
        HarvestObjectExtra.key == 'original_document'
    ).first()

    if extra:
        return extra.value
    else:
        return None


def _get_content(id):
    from ckanext.harvest.model import HarvestObject
    obj = Session.query(HarvestObject).filter(HarvestObject.id == id).first()
    if obj:
        return obj.content
    else:
        return None


def _transform_to_html(content, xslt_package=None, xslt_path=None):

    xslt_package = xslt_package or __name__
    xslt_path = xslt_path or \
        '../templates/ckanext/spatial/gemini2-html-stylesheet.xsl'

    # optimise -- read transform only once and compile rather
    # than at each request
    with resource_stream(xslt_package, xslt_path) as style:
        style_xml = etree.parse(style)
        transformer = etree.XSLT(style_xml)

    xml = etree.parse(StringIO(content.encode('utf-8')))
    html = transformer(xml)

    result = etree.tostring(html, pretty_print=True)

    return result


def _get_xslt(original=False):

    if original:
        config_option = \
            'ckanext.spatial.harvest.xslt_html_content_original'
    else:
        config_option = 'ckanext.spatial.harvest.xslt_html_content'

    xslt_package = None
    xslt_path = None
    xslt = config.get(config_option, None)
    if xslt:
        if ':' in xslt:
            xslt = xslt.split(':')
            xslt_package = xslt[0]
            xslt_path = xslt[1]
        else:
            log.error('XSLT should be defined in the form <package>:<path>' +
                      ', eg ckanext.myext:templates/my.xslt')

    return xslt_package, xslt_path


def display_xml_original(id):
    content = _get_original_content(id)

    if not content:
        return tk.abort(404)

    headers = {'Content-Type': 'application/xml; charset=utf-8'}

    if '<?xml' not in content.split('\n')[0]:
        content = u'<?xml version="1.0" encoding="UTF-8"?>\n' + content
    return make_response((content, 200, headers))


def display_html(id):
    content = _get_content(id)

    if not content:
        return tk.abort(404)
    headers = {'Content-Type': 'text/html; charset=utf-8'}

    xslt_package, xslt_path = _get_xslt()
    content = _transform_to_html(content, xslt_package, xslt_path)
    return make_response((content, 200, headers))


def display_html_original(id):
    content = _get_original_content(id)

    if content is None:
        return tk.abort(404)
    headers = {'Content-Type': 'text/html; charset=utf-8'}

    xslt_package, xslt_path = _get_xslt(original=True)
    content = _transform_to_html(content, xslt_package, xslt_path)
    return make_response((content, 200, headers))


harvest_metadata.add_url_rule('/api/2/rest/harvestobject/<id>/xml',
                              view_func=harvest_object_redirect_xml)
harvest_metadata.add_url_rule('/api/2/rest/harvestobject/<id>/html',
                              view_func=harvest_object_redirect_html)

harvest_metadata.add_url_rule('/harvest/object/<id>/original',
                              view_func=display_xml_original)
harvest_metadata.add_url_rule('/harvest/object/<id>/html',
                              view_func=display_html)
harvest_metadata.add_url_rule('/harvest/object/<id>/html/original',
                              view_func=display_html_original)
