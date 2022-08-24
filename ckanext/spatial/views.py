# -*- coding: utf-8 -*-

import logging

from flask import Blueprint, make_response

import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk

from ckanext.spatial import util


log = logging.getLogger(__name__)


harvest_metadata = Blueprint("spatial_harvest_metadata", __name__)


def harvest_object_redirect_xml(id):
    return h.redirect_to("/harvest/object/{}".format(id))


def harvest_object_redirect_html(id):
    return h.redirect_to("/harvest/object/{}/html".format(id))


def display_xml_original(id):
    content = util.get_harvest_object_original_content(id)

    if not content:
        return tk.abort(404)

    headers = {"Content-Type": "application/xml; charset=utf-8"}

    if "<?xml" not in content.split("\n")[0]:
        content = u'<?xml version="1.0" encoding="UTF-8"?>\n' + content
    return make_response((content, 200, headers))


def display_html(id):
    content = util.get_harvest_object_content(id)

    if not content:
        return tk.abort(404)
    headers = {"Content-Type": "text/html; charset=utf-8"}

    xslt_package, xslt_path = util.get_xslt()
    content = util.transform_to_html(content, xslt_package, xslt_path)
    return make_response((content, 200, headers))


def display_html_original(id):
    content = util.get_harvest_object_original_content(id)

    if content is None:
        return tk.abort(404)
    headers = {"Content-Type": "text/html; charset=utf-8"}

    xslt_package, xslt_path = util.get_xslt(original=True)
    content = util.transform_to_html(content, xslt_package, xslt_path)
    return make_response((content, 200, headers))


harvest_metadata.add_url_rule(
    "/api/2/rest/harvestobject/<id>/xml", view_func=harvest_object_redirect_xml
)
harvest_metadata.add_url_rule(
    "/api/2/rest/harvestobject/<id>/html", view_func=harvest_object_redirect_html
)

harvest_metadata.add_url_rule(
    "/harvest/object/<id>/original", view_func=display_xml_original
)
harvest_metadata.add_url_rule("/harvest/object/<id>/html", view_func=display_html)
harvest_metadata.add_url_rule(
    "/harvest/object/<id>/html/original", view_func=display_html_original
)
