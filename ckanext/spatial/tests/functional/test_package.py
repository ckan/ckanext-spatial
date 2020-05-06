import json

import pytest

from ckan.model import Session
from ckan.lib.helpers import url_for

import ckan.tests.factories as factories

from ckanext.spatial.model import PackageExtent
from ckanext.spatial.tests.base import SpatialTestBase


@pytest.mark.usefixtures("spatial_clean_db")
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        offset = url_for("dataset.edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        data = {
            "name": dataset['name'],
            "extras__0__key": u"spatial",
            "extras__0__value": self.geojson_examples["point"]
        }

        res = app.post(offset, environ_overrides=env, data=data)

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

        offset = url_for("dataset.edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        data = {
            "name": dataset['name'],
            "extras__0__key": u"spatial",
            "extras__0__value": self.geojson_examples["point"]
        }

        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" not in res, res

        res = app.get(offset, extra_environ=env)

        data = {
            "name": dataset['name'],
            "extras__0__key": u"spatial",
            "extras__0__value": self.geojson_examples["polygon"]
        }

        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" not in res, res

        package_extent = (
            Session.query(PackageExtent)
            .filter(PackageExtent.package_id == dataset["id"])
            .first()
        )

        assert package_extent.package_id == dataset["id"]
        from sqlalchemy import func

        assert (
            Session.query(
                func.ST_GeometryType(package_extent.the_geom)
            ).first()[0]
            == "ST_Polygon"
        )
        assert package_extent.the_geom.srid == self.db_srid

    def test_spatial_extra_bad_json(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        offset = url_for("dataset.edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        data = {
            "name": dataset['name'],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":Bad Json]'
        }

        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error decoding JSON object" in res

    def test_spatial_extra_bad_geojson(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        offset = url_for("dataset.edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        data = {
            "name": dataset['name'],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":"Bad_GeoJSON","a":2}'
        }

        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error creating geometry" in res
