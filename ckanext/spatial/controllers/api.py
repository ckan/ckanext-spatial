import logging

from pylons import response

from ckan.lib.base import request, abort
from ckan.controllers.api import ApiController as BaseApiController
from ckan.model import Session

from ckanext.harvest.model import HarvestObject, HarvestObjectExtra
from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query
from ckanext.spatial import util

log = logging.getLogger(__name__)


class ApiController(BaseApiController):

    def spatial_query(self):

        error_400_msg = \
            'Please provide a suitable bbox parameter [minx,miny,maxx,maxy]'

        if 'bbox' not in request.params:
            abort(400, error_400_msg)

        bbox = validate_bbox(request.params['bbox'])

        if not bbox:
            abort(400, error_400_msg)

        srid = get_srid(request.params.get('crs')) if 'crs' in \
            request.params else None

        extents = bbox_query(bbox, srid)

        format = request.params.get('format', '')

        return self._output_results(extents, format)

    def _output_results(self, extents, format=None):

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
