from ckan.lib.base import request, config, abort
from ckan.controllers.api import ApiController as BaseApiController
from ckan.model import Session, Package

from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query

from geoalchemy import WKTSpatialElement, functions

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
