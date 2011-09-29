from string import Template

from ckan.lib.base import request, config, abort
from ckan.controllers.api import ApiController as BaseApiController
from ckan.model import Session

from ckanext.spatial.lib import get_srid
from ckanext.spatial.model import PackageExtent

from geoalchemy import WKTSpatialElement, functions

class ApiController(BaseApiController):

    db_srid = int(config.get('ckan.spatial.srid', '4326'))

    bbox_template = Template('POLYGON (($minx $miny, $minx $maxy, $maxx $maxy, $maxx $miny, $minx $miny))')

    def spatial_query(self):

        error_400_msg = 'Please provide a suitable bbox parameter [minx,miny,maxx,maxy]'

        if not 'bbox' in request.params:
            abort(400,error_400_msg)

        bbox = request.params['bbox'].split(',')
        if len(bbox) is not 4:
            abort(400,error_400_msg)

        try:
            minx = float(bbox[0])
            miny = float(bbox[1])
            maxx = float(bbox[2])
            maxy = float(bbox[3])
        except ValueError,e:
            abort(400,error_400_msg)


        wkt = self.bbox_template.substitute(minx=minx,miny=miny,maxx=maxx,maxy=maxy)

        srid = get_srid(request.params.get('crs')) if 'crs' in request.params else None
        if srid and srid != self.db_srid:
            # Input geometry needs to be transformed to the one used on the database
            input_geometry = functions.transform(WKTSpatialElement(wkt,srid),self.db_srid)
        else:
            input_geometry = WKTSpatialElement(wkt,self.db_srid)

        extents = Session.query(PackageExtent).filter(PackageExtent.the_geom.intersects(input_geometry))
        ids = [extent.package_id for extent in extents]

        output = dict(count=len(ids),results=ids)

        return self._finish_ok(output)
