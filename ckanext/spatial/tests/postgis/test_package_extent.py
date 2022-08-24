import pytest
import six
import time
import random

from shapely.geometry import shape

from sqlalchemy import func

import ckantoolkit as tk
from ckantoolkit.tests import helpers

from ckan import model
from ckan.model import Session
from ckan.lib.helpers import json
from ckan.lib.search import SearchError

from ckan.lib.munge import munge_title_to_name

import ckan.tests.factories as factories

from ckanext.spatial.tests.base import SpatialTestBase

use_postgis = tk.asbool(tk.config.get("ckan.spatial.use_postgis", False))

if use_postgis:
    from ckanext.spatial.postgis.model import (
        PackageExtent,
        WKTElement,  # type: ignore
        bbox_query,
        bbox_query_ordered,
        compare_geometry_fields,
        setup as spatial_db_setup,
    )


def _create_postgis_extension():
    Session.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Session.commit()


def create_postgis_tables():
    _create_postgis_extension()


@pytest.fixture
def clean_postgis():
    Session.execute("DROP TABLE IF EXISTS package_extent")
    Session.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
    Session.commit()


@pytest.fixture
def spatial_setup():
    create_postgis_tables()
    spatial_db_setup()


pytestmark = pytest.mark.skipif(
    use_postgis is False, reason="PostGIS is no longer used by default"
)


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestPackageExtent(SpatialTestBase):
    def test_create_extent(self):

        package = factories.Dataset()

        geojson = json.loads(self.geojson_examples["point"])

        geom_obj = shape(geojson)
        package_extent = PackageExtent(
            package_id=package["id"],
            the_geom=WKTElement(geom_obj.wkt, self.db_srid),
        )
        package_extent.save()

        assert package_extent.package_id == package["id"]

        assert (
            Session.query(func.ST_X(package_extent.the_geom)).first()[0]
            == geojson["coordinates"][0]
        )
        assert (
            Session.query(func.ST_Y(package_extent.the_geom)).first()[0]
            == geojson["coordinates"][1]
        )
        assert package_extent.the_geom.srid == self.db_srid  # type: ignore

    def test_update_extent(self):

        package = factories.Dataset()

        geojson = json.loads(self.geojson_examples["point"])

        geom_obj = shape(geojson)
        package_extent = PackageExtent(
            package_id=package["id"],
            the_geom=WKTElement(geom_obj.wkt, self.db_srid),
        )
        package_extent.save()
        assert (
            Session.query(func.ST_GeometryType(package_extent.the_geom)).first()[0]
            == "ST_Point"
        )

        # Update the geometry (Point -> Polygon)
        geojson = json.loads(self.geojson_examples["polygon"])

        geom_obj = shape(geojson)
        package_extent.the_geom = WKTElement(geom_obj.wkt, self.db_srid)
        package_extent.save()

        assert package_extent.package_id == package["id"]
        assert (
            Session.query(func.ST_GeometryType(package_extent.the_geom)).first()[0]
            == "ST_Polygon"
        )
        assert package_extent.the_geom.srid == self.db_srid


def create_package(**package_dict):
    user = tk.get_action("get_site_user")({"model": model, "ignore_auth": True}, {})
    context = {
        "model": model,
        "session": model.Session,
        "user": user["name"],
        "extras_as_string": True,
        "api_version": 2,
        "ignore_auth": True,
    }
    package_dict = tk.get_action("package_create")(context, package_dict)
    return context.get("id")


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestCompareGeometries(SpatialTestBase):
    def _get_extent_object(self, geometry):
        if isinstance(geometry, six.string_types):
            geometry = json.loads(geometry)
        geom_obj = shape(geometry)
        return PackageExtent(package_id="xxx", the_geom=WKTElement(geom_obj.wkt, 4326))

    def test_same_points(self):

        extent1 = self._get_extent_object(self.geojson_examples["point"])
        extent2 = self._get_extent_object(self.geojson_examples["point"])

        assert compare_geometry_fields(extent1.the_geom, extent2.the_geom)

    def test_different_points(self):

        extent1 = self._get_extent_object(self.geojson_examples["point"])
        extent2 = self._get_extent_object(self.geojson_examples["point_2"])

        assert not compare_geometry_fields(extent1.the_geom, extent2.the_geom)


def bbox_2_geojson(bbox_dict):
    return (
        '{"type":"Polygon","coordinates":[[[%(minx)s, %(miny)s],'
        "[%(minx)s, %(maxy)s], [%(maxx)s, %(maxy)s], "
        "[%(maxx)s, %(miny)s], [%(minx)s, %(miny)s]]]}" % bbox_dict
    )


class SpatialQueryTestBase(SpatialTestBase):
    """Base class for tests of spatial queries"""

    miny = 0
    maxy = 1

    def initial_data(self):
        for fixture_x in self.fixtures_x:  # type: ignore
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


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestBboxQuery(SpatialQueryTestBase):
    # x values for the fixtures
    fixtures_x = [(0, 1), (0, 3), (0, 4), (4, 5), (6, 7)]

    def test_query(self):
        self.initial_data()
        bbox_dict = self.x_values_to_bbox((2, 5))
        package_ids = [res.package_id for res in bbox_query(bbox_dict)]
        package_titles = [model.Package.get(id_).title for id_ in package_ids]
        assert set(package_titles) == {"(0, 3)", "(0, 4)", "(4, 5)"}


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestBboxQueryOrdered(SpatialQueryTestBase):
    # x values for the fixtures
    fixtures_x = [(0, 9), (1, 8), (2, 7), (3, 6), (4, 5), (8, 9)]

    def test_query(self):
        self.initial_data()
        bbox_dict = self.x_values_to_bbox((2, 7))
        q = bbox_query_ordered(bbox_dict)
        package_ids = [res.package_id for res in q]
        package_titles = [model.Package.get(id_).title for id_ in package_ids]
        # check the right items are returned
        assert set(package_titles) == set(
            ("(0, 9)", "(1, 8)", "(2, 7)", "(3, 6)", "(4, 5)")
        )
        # check the order is good
        assert package_titles == ["(2, 7)", "(1, 8)", "(3, 6)", "(0, 9)", "(4, 5)"]


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
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


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.edit", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset["name"],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["point"],
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form["extras__0__key"] = u"spatial"
            form["extras__0__value"] = self.geojson_examples["point"]
            res = helpers.submit_and_follow(app, form, env, "save")

        assert "Error" not in res, res

        package_extent = (
            Session.query(PackageExtent)
            .filter(PackageExtent.package_id == dataset["id"])
            .first()
        )

        geojson = json.loads(self.geojson_examples["point"])

        assert package_extent.package_id == dataset["id"]
        from sqlalchemy import func

        assert (
            Session.query(func.ST_X(package_extent.the_geom)).first()[0]
            == geojson["coordinates"][0]
        )
        assert (
            Session.query(func.ST_Y(package_extent.the_geom)).first()[0]
            == geojson["coordinates"][1]
        )
        assert package_extent.the_geom.srid == self.db_srid

    def test_spatial_extra_edit(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.edit", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset["name"],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["point"],
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form["extras__0__key"] = u"spatial"
            form["extras__0__value"] = self.geojson_examples["point"]
            res = helpers.submit_and_follow(app, form, env, "save")

        assert "Error" not in res, res

        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset["name"],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["polygon"],
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form["extras__0__key"] = u"spatial"
            form["extras__0__value"] = self.geojson_examples["polygon"]
            res = helpers.submit_and_follow(app, form, env, "save")

        assert "Error" not in res, res

        package_extent = (
            Session.query(PackageExtent)
            .filter(PackageExtent.package_id == dataset["id"])
            .first()
        )

        assert package_extent.package_id == dataset["id"]
        from sqlalchemy import func

        assert (
            Session.query(func.ST_GeometryType(package_extent.the_geom)).first()[0]
            == "ST_Polygon"
        )
        assert package_extent.the_geom.srid == self.db_srid

    def test_spatial_extra_bad_json(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.edit", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset["name"],
                "extras__0__key": u"spatial",
                "extras__0__value": u'{"Type":Bad Json]',
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form["extras__0__key"] = u"spatial"
            form["extras__0__value"] = u'{"Type":Bad Json]'
            res = helpers.webtest_submit(form, extra_environ=env, name="save")

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error decoding JSON object" in res

    def test_spatial_extra_bad_geojson(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.edit", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset["name"],
                "extras__0__key": u"spatial",
                "extras__0__value": u'{"Type":"Bad_GeoJSON","a":2}',
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form["extras__0__key"] = u"spatial"
            form["extras__0__value"] = u'{"Type":"Bad_GeoJSON","a":2}'
            res = helpers.webtest_submit(form, extra_environ=env, name="save")

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Wrong GeoJSON object" in res


extents = {
    "nz": '{"type":"Polygon","coordinates":[[[174,-38],[176,-38],[176,-40],[174,-40],[174,-38]]]}',
    "ohio": '{"type": "Polygon","coordinates": [[[-84,38],[-84,40],[-80,42],[-80,38],[-84,38]]]}',
    "dateline": '{"type":"Polygon","coordinates":[[[169,70],[169,60],[192,60],[192,70],[169,70]]]}',
    "dateline2": '{"type":"Polygon","coordinates":[[[170,60],[-170,60],[-170,70],[170,70],[170,60]]]}',
}


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_postgis",
    "clean_db",
    "clean_index",
    "harvest_setup",
    "spatial_setup",
)
class TestSearchActionPostgis(SpatialTestBase):
    def test_spatial_query(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_outside_bbox(self):

        factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-10,-20,10,20"}
        )

        assert result["count"] == 0

    def test_spatial_query_wrong_bbox(self):
        with pytest.raises(SearchError):
            helpers.call_action(
                "package_search",
                extras={"ext_bbox": "-10,-20,10,a"},
            )

    def test_spatial_query_nz(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_nz_wrap(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-203,-54,-167,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio_wrap(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "258,37,281,51"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]
