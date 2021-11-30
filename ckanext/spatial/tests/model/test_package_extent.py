import pytest

from shapely.geometry import asShape

from ckan.model import Session
from ckan.lib.helpers import json

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.spatial.model import PackageExtent
from ckanext.spatial.geoalchemy_common import WKTElement, legacy_geoalchemy
from ckanext.spatial.tests.base import SpatialTestBase


@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index', 'harvest_setup', 'spatial_setup')
class TestPackageExtent(SpatialTestBase):
    def test_create_extent(self):

        package = factories.Dataset()

        geojson = json.loads(self.geojson_examples["point"])

        shape = asShape(geojson)
        package_extent = PackageExtent(
            package_id=package["id"],
            the_geom=WKTElement(shape.wkt, self.db_srid),
        )
        package_extent.save()

        assert(package_extent.package_id == package["id"])
        if legacy_geoalchemy:
            assert(
                Session.scalar(package_extent.the_geom.x) ==
                geojson["coordinates"][0]
            )
            assert(
                Session.scalar(package_extent.the_geom.y) ==
                geojson["coordinates"][1]
            )
            assert(
                Session.scalar(package_extent.the_geom.srid) == self.db_srid
            )
        else:
            from sqlalchemy import func

            assert(
                Session.query(func.ST_X(package_extent.the_geom)).first()[0] ==
                geojson["coordinates"][0]
            )
            assert(
                Session.query(func.ST_Y(package_extent.the_geom)).first()[0] ==
                geojson["coordinates"][1]
            )
            assert(package_extent.the_geom.srid == self.db_srid)

    def test_update_extent(self):

        package = factories.Dataset()

        geojson = json.loads(self.geojson_examples["point"])

        shape = asShape(geojson)
        package_extent = PackageExtent(
            package_id=package["id"],
            the_geom=WKTElement(shape.wkt, self.db_srid),
        )
        package_extent.save()
        if legacy_geoalchemy:
            assert(
                Session.scalar(package_extent.the_geom.geometry_type) ==
                "ST_Point"
            )
        else:
            from sqlalchemy import func

            assert(
                Session.query(
                    func.ST_GeometryType(package_extent.the_geom)
                ).first()[0] ==
                "ST_Point"
            )

        # Update the geometry (Point -> Polygon)
        geojson = json.loads(self.geojson_examples["polygon"])

        shape = asShape(geojson)
        package_extent.the_geom = WKTElement(shape.wkt, self.db_srid)
        package_extent.save()

        assert(package_extent.package_id == package["id"])
        if legacy_geoalchemy:
            assert(
                Session.scalar(package_extent.the_geom.geometry_type) ==
                "ST_Polygon"
            )
            assert(
                Session.scalar(package_extent.the_geom.srid) == self.db_srid
            )
        else:
            assert(
                Session.query(
                    func.ST_GeometryType(package_extent.the_geom)
                ).first()[0] ==
                "ST_Polygon"
            )
            assert(package_extent.the_geom.srid == self.db_srid)

