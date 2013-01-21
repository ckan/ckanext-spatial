import logging
from pprint import pprint

from geoalchemy import WKTSpatialElement

from shapely.geometry import asShape
from ckan.model import Session, Package
from ckan import model
from ckan.lib.helpers import json
from ckan.tests import CreateTestData
from ckanext.spatial.model import PackageExtent

from ckanext.spatial.tests.base import SpatialTestBase

log = logging.getLogger(__name__)



class TestPackageExtent(SpatialTestBase):
    def setup(self):
        CreateTestData.create()

    def teardown(self):
        model.repo.rebuild_db()

    def test_create_extent(self):
        package = Package.get('annakarenina')
        assert package

        geojson = json.loads(self.geojson_examples['point'])

        shape = asShape(geojson)
        package_extent = PackageExtent(package_id=package.id,the_geom=WKTSpatialElement(shape.wkt, self.db_srid))
        package_extent.save()

        assert package_extent.package_id == package.id
        assert Session.scalar(package_extent.the_geom.x) == geojson['coordinates'][0]
        assert Session.scalar(package_extent.the_geom.y) == geojson['coordinates'][1]
        assert Session.scalar(package_extent.the_geom.srid) == self.db_srid

    def test_update_extent(self):

        package = Package.get('annakarenina')

        geojson = json.loads(self.geojson_examples['point'])

        shape = asShape(geojson)
        package_extent = PackageExtent(package_id=package.id,the_geom=WKTSpatialElement(shape.wkt, self.db_srid))
        package_extent.save()
        assert Session.scalar(package_extent.the_geom.geometry_type) == 'ST_Point'

        # Update the geometry (Point -> Polygon)
        geojson = json.loads(self.geojson_examples['polygon'])

        shape = asShape(geojson)
        package_extent.the_geom=WKTSpatialElement(shape.wkt, self.db_srid)
        package_extent.save()

        assert package_extent.package_id == package.id
        assert Session.scalar(package_extent.the_geom.geometry_type) == 'ST_Polygon'
        assert Session.scalar(package_extent.the_geom.srid) == self.db_srid
