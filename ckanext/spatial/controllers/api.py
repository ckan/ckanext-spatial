try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

from geoalchemy import WKTSpatialElement, functions
from pylons import response
from pkg_resources import resource_stream
from lxml import etree

from ckan.lib.base import request, config, abort
from ckan.controllers.api import ApiController as BaseApiController
from ckan.model import Session

from ckanext.harvest.model import HarvestObject
from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query


class ApiController(BaseApiController):

    def spatial_query(self):

        error_400_msg = 'Please provide a suitable bbox parameter [minx,miny,maxx,maxy]'

        if not 'bbox' in request.params:
            abort(400,error_400_msg)

        bbox = validate_bbox(request.params['bbox'])

        if not bbox:
            abort(400,error_400_msg)

        srid = get_srid(request.params.get('crs')) if 'crs' in request.params else None

        extents = bbox_query(bbox,srid)

        format = request.params.get('format','')

        return self._output_results(extents,format)

    def _output_results(self,extents,format=None):

        ids = [extent.package_id for extent in extents]

        output = dict(count=len(ids),results=ids)

        return self._finish_ok(output)

class HarvestMetadataApiController(BaseApiController):

    def _get_harvest_object(self,id):

        obj = Session.query(HarvestObject) \
                        .filter(HarvestObject.id==id).first()
        return obj

    def display_xml(self,id):
        obj = self._get_harvest_object(id)

        if obj is None:
            abort(404)
        response.content_type = "application/xml"
        response.headers["Content-Length"] = len(obj.content)
        return obj.content

    def display_html(self,id):
        obj = self._get_harvest_object(id)

        if obj is None:
            abort(404)
        ## optimise -- read transform only once and compile rather
        ## than at each request
        with resource_stream("ckanext.inspire",
                             "xml/gemini2-html-stylesheet.xsl") as style:
            style_xml = etree.parse(style)
            transformer = etree.XSLT(style_xml)
        xml = etree.parse(StringIO(obj.content.encode("utf-8")))
        html = transformer(xml)
        return etree.tostring(html, pretty_print=True)

