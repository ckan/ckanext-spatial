import logging
import urllib

from pylons import response

from ckan.lib.base import request, abort
from ckan.controllers.api import ApiController as BaseApiController
from ckan.model import Session

from ckanext.harvest.model import HarvestObject, HarvestObjectExtra
from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query, polygon_query, validate_polygon
from ckanext.spatial import util

log = logging.getLogger(__name__)


class ApiController(BaseApiController):

    def spatial_query(self):

        error_400_msg = \
            'Please provide a suitable "bbox" parameter [minx,miny,maxx,maxy], ' \
            'or "poly" parameter [POLYGON((x1 y1,x2 y2, ....)) | MULTIPOLYGON(((x1 y1,x2 y2, ....)),((x1 y1,x2 y2, ....)))] | BOX(minx,miny,maxx,maxy)'

        bbox = poly = []
        if request.method == 'POST':
            request_data = request.get_json()
        else:
            request_data = request.params

        if 'bbox' in request_data:
            bbox = validate_bbox(request_data['bbox'])
        elif 'poly' in request_data:
            poly_str = urllib.parse.unquote_plus(request_data['poly'])
            if poly_str.startswith('BOX'):
                bbox = validate_bbox(poly_str[4:-1])
            else:
                poly = validate_polygon(poly_str)
        else:
            abort(400, error_400_msg)

        if not bbox and not poly:
            abort(400, error_400_msg)

        srid = get_srid(request_data.get('crs')) if 'crs' in \
            request_data else None

        if bbox:
            extents = bbox_query(bbox, srid)
        if poly:
            extents = polygon_query(poly, srid)

        try:
            output = self._output_results(extents)
        except (Exception) as e:
            abort(400, error_400_msg + '\n\n' + e.message)
            output = None

        return output

    def _output_results(self, extents):

        ids = [extent.package_id for extent in extents]
        output = dict(count=len(ids), results=ids)

        return self._finish_ok(output)


class HarvestMetadataApiController(BaseApiController):

    def _get_content(self, id):

        obj = Session.query(HarvestObject) \
            .filter(HarvestObject.id == id).first()
        if obj:
            return obj.content
        else:
            return None

    def _get_original_content(self, id):
        extra = Session.query(HarvestObjectExtra).join(HarvestObject) \
            .filter(HarvestObject.id == id) \
            .filter(
                HarvestObjectExtra.key == 'original_document'
        ).first()
        if extra:
            return extra.value
        else:
            return None

    def _get_xslt(self, original=False):

        return util.get_xslt(original)

    def display_xml_original(self, id):
        content = util.get_harvest_object_original_content(id)

        if not content:
            abort(404)

        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        response.headers['Content-Length'] = len(content)

        if '<?xml' not in content.split('\n')[0]:
            content = u'<?xml version="1.0" encoding="UTF-8"?>\n' + content
        return content.encode('utf-8')

    def display_html(self, id):
        content = self._get_content(id)

        if not content:
            abort(404)

        xslt_package, xslt_path = self._get_xslt()
        out = util.transform_to_html(content, xslt_package, xslt_path)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Length'] = len(out)

        return out

    def display_html_original(self, id):
        content = util.get_harvest_object_original_content(id)

        if content is None:
            abort(404)

        xslt_package, xslt_path = self._get_xslt(original=True)

        out = util.transform_to_html(content, xslt_package, xslt_path)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Length'] = len(out)

        return out
