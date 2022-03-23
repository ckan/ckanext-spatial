# -*- coding: utf-8 -*-

import logging
import urllib

from flask import Blueprint, make_response

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckantoolkit import request
from ckan.views.api import _finish_ok, _finish_bad_request

from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query, polygon_query, validate_polygon
from ckanext.spatial import util


log = logging.getLogger(__name__)

api = Blueprint("spatial_api", __name__)


def spatial_query(register):
    error_400_msg = \
        'Please provide a suitable "bbox" parameter [minx,miny,maxx,maxy], ' \
        'or "poly" parameter [POLYGON((x1 y1,x2 y2, ....)) | MULTIPOLYGON(((x1 y1,x2 y2, ....)),((x1 y1,x2 y2, ....)))] | BOX(minx,miny,maxx,maxy)'

    if request.method == 'POST':
        request_data = request.get_json()
    else:
        request_data = request.args

    srid = get_srid(str(request_data.get('crs'))) if 'crs' in \
        request_data else None

    bbox = poly = []
    if 'bbox' in request_data:
        bbox = validate_bbox(request.params['bbox'])
    elif 'poly' in request_data:
        poly_str = urllib.parse.unquote_plus(request_data['poly'])
        if poly_str.startswith('BOX'):
            bbox = validate_bbox(poly_str[4:-1])
        else:
            poly = validate_polygon(poly_str)
    else:
        return _finish_bad_request(error_400_msg)

    if not (bbox or poly):
        return _finish_bad_request(error_400_msg)

    extents = bbox_query(bbox, srid) if bbox \
        else polygon_query(poly, srid)

    try:
        ids = [extent.package_id for extent in extents]
        output = dict(count=len(ids), results=ids)
    except (Exception) as e:
        return _finish_bad_request(error_400_msg + '\n\n' + e.message)

    return _finish_ok(output)


api.add_url_rule('/api/2/search/<register>/geo', methods=[u'GET', u'POST'], view_func=spatial_query)

harvest_metadata = Blueprint("spatial_harvest_metadata", __name__)


def harvest_object_redirect_xml(id):
    return h.redirect_to('/harvest/object/{}'.format(id))


def harvest_object_redirect_html(id):
    return h.redirect_to('/harvest/object/{}/html'.format(id))


def display_xml_original(id):
    content = util.get_harvest_object_original_content(id)

    if not content:
        return tk.abort(404)

    headers = {'Content-Type': 'application/xml; charset=utf-8'}

    if '<?xml' not in content.split('\n')[0]:
        content = u'<?xml version="1.0" encoding="UTF-8"?>\n' + content
    return make_response((content, 200, headers))


def display_html(id):
    content = util.get_harvest_object_content(id)

    if not content:
        return tk.abort(404)
    headers = {'Content-Type': 'text/html; charset=utf-8'}

    xslt_package, xslt_path = util.get_xslt()
    content = util.transform_to_html(content, xslt_package, xslt_path)
    return make_response((content, 200, headers))


def display_html_original(id):
    content = util.get_harvest_object_original_content(id)

    if content is None:
        return tk.abort(404)
    headers = {'Content-Type': 'text/html; charset=utf-8'}

    xslt_package, xslt_path = util.get_xslt(original=True)
    content = util.transform_to_html(content, xslt_package, xslt_path)
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
