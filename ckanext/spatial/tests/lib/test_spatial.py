import six

import time
import random

import pytest

from shapely.geometry import asShape

from ckan import model
from ckan import plugins
from ckan.lib.helpers import json
from ckan.logic.action.create import package_create
from ckan.lib.munge import munge_title_to_name

from ckanext.spatial.model import PackageExtent
from ckanext.spatial.lib import validate_bbox, bbox_query, bbox_query_ordered
from ckanext.spatial.geoalchemy_common import (
    WKTElement,
    compare_geometry_fields,
)
from ckanext.spatial.tests.base import SpatialTestBase


def create_package(**package_dict):
    user = plugins.toolkit.get_action("get_site_user")(
        {"model": model, "ignore_auth": True}, {}
    )
    context = {
        "model": model,
        "session": model.Session,
        "user": user["name"],
        "extras_as_string": True,
        "api_version": 2,
        "ignore_auth": True,
    }
    package_dict = package_create(context, package_dict)
    return context.get("id")


@pytest.mark.usefixtures("spatial_clean_db")
class TestCompareGeometries(SpatialTestBase):
    def _get_extent_object(self, geometry):
        if isinstance(geometry, six.string_types):
            geometry = json.loads(geometry)
        shape = asShape(geometry)
        return PackageExtent(
            package_id="xxx", the_geom=WKTElement(shape.wkt, 4326)
        )

    def test_same_points(self):

        extent1 = self._get_extent_object(self.geojson_examples["point"])
        extent2 = self._get_extent_object(self.geojson_examples["point"])

        assert compare_geometry_fields(extent1.the_geom, extent2.the_geom)

    def test_different_points(self):

        extent1 = self._get_extent_object(self.geojson_examples["point"])
        extent2 = self._get_extent_object(self.geojson_examples["point_2"])

        assert not compare_geometry_fields(extent1.the_geom, extent2.the_geom)


class TestValidateBbox(object):
    bbox_dict = {"minx": -4.96, "miny": 55.70, "maxx": -3.78, "maxy": 56.43}

    def test_string(self):
        res = validate_bbox("-4.96,55.70,-3.78,56.43")
        assert(res == self.bbox_dict)

    def test_list(self):
        res = validate_bbox([-4.96, 55.70, -3.78, 56.43])
        assert(res == self.bbox_dict)

    def test_bad(self):
        res = validate_bbox([-4.96, 55.70, -3.78])
        assert(res is None)

    def test_bad_2(self):
        res = validate_bbox("random")
        assert(res is None)


def bbox_2_geojson(bbox_dict):
    return (
        '{"type":"Polygon","coordinates":[[[%(minx)s, %(miny)s],'
        '[%(minx)s, %(maxy)s], [%(maxx)s, %(maxy)s], '
        '[%(maxx)s, %(miny)s], [%(minx)s, %(miny)s]]]}'
        % bbox_dict
    )


class SpatialQueryTestBase(SpatialTestBase):
    """Base class for tests of spatial queries"""

    miny = 0
    maxy = 1

    @pytest.fixture(autouse=True)
    def initial_data(self, spatial_clean_db):
        for fixture_x in self.fixtures_x:
            bbox = self.x_values_to_bbox(fixture_x)
            bbox_geojson = bbox_2_geojson(bbox)
            create_package(
                name=munge_title_to_name(six.text_type(fixture_x)),
                title=six.text_type(fixture_x),
                extras=[{"key": "spatial", "value": bbox_geojson}],
            )

    @classmethod
    def x_values_to_bbox(cls, x_tuple):
        return {
            "minx": x_tuple[0],
            "maxx": x_tuple[1],
            "miny": cls.miny,
            "maxy": cls.maxy,
        }


class TestBboxQuery(SpatialQueryTestBase):
    # x values for the fixtures
    fixtures_x = [(0, 1), (0, 3), (0, 4), (4, 5), (6, 7)]

    def test_query(self):
        bbox_dict = self.x_values_to_bbox((2, 5))
        package_ids = [res.package_id for res in bbox_query(bbox_dict)]
        package_titles = [model.Package.get(id_).title for id_ in package_ids]
        assert(set(package_titles) == set(("(0, 3)", "(0, 4)", "(4, 5)")))


class TestBboxQueryOrdered(SpatialQueryTestBase):
    # x values for the fixtures
    fixtures_x = [(0, 9), (1, 8), (2, 7), (3, 6), (4, 5), (8, 9)]

    def test_query(self):
        bbox_dict = self.x_values_to_bbox((2, 7))
        q = bbox_query_ordered(bbox_dict)
        package_ids = [res.package_id for res in q]
        package_titles = [model.Package.get(id_).title for id_ in package_ids]
        # check the right items are returned
        assert(
            set(package_titles) ==
            set(("(0, 9)", "(1, 8)", "(2, 7)", "(3, 6)", "(4, 5)"))
        )
        # check the order is good
        assert(
            package_titles == ["(2, 7)", "(1, 8)", "(3, 6)", "(0, 9)", "(4, 5)"]
        )


class TestBboxQueryPerformance(SpatialQueryTestBase):
    # x values for the fixtures
    fixtures_x = [
        (random.uniform(0, 3), random.uniform(3, 9)) for x in range(10)
    ]  # increase the number to 1000 say

    def test_query(self):
        bbox_dict = self.x_values_to_bbox((2, 7))
        t0 = time.time()
        bbox_query(bbox_dict)
        t1 = time.time()
        print("bbox_query took: ", t1 - t0)

    def test_query_ordered(self):
        bbox_dict = self.x_values_to_bbox((2, 7))
        t0 = time.time()
        bbox_query_ordered(bbox_dict)
        t1 = time.time()
        print("bbox_query_ordered took: ", t1 - t0)
