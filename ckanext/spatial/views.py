# -*- coding: utf-8 -*-

import logging

from flask import Blueprint, make_response

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckantoolkit import request
from ckan.views.api import _finish_ok, _finish_bad_request

from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query
from ckanext.spatial import util


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
