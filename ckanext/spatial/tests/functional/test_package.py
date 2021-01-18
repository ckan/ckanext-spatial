import json

import pytest

from ckan.model import Session
from ckan.lib.helpers import url_for

import ckan.plugins.toolkit as tk

import ckan.tests.factories as factories

from ckanext.spatial.model import PackageExtent
from ckanext.spatial.tests.base import SpatialTestBase

if not tk.check_ckan_version(min_version="2.9"):
    import ckan.tests.helpers as helpers

@pytest.mark.usefixtures('with_plugins', 'clean_db', 'clean_index', 'harvest_setup', 'spatial_setup')
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = url_for("dataset.edit", id=dataset["id"])
        else:
            offset = url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset['name'],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["point"]
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form['extras__0__key'] = u'spatial'
            form['extras__0__value'] = self.geojson_examples['point']
            res = helpers.submit_and_follow(app, form, env, 'save')

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
            offset = url_for("dataset.edit", id=dataset["id"])
        else:
            offset = url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)


        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset['name'],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["point"]
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form['extras__0__key'] = u'spatial'
            form['extras__0__value'] = self.geojson_examples['point']
            res = helpers.submit_and_follow(app, form, env, 'save')

        assert "Error" not in res, res

        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset['name'],
                "extras__0__key": u"spatial",
                "extras__0__value": self.geojson_examples["polygon"]
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form['extras__0__key'] = u'spatial'
            form['extras__0__value'] = self.geojson_examples['polygon']
            res = helpers.submit_and_follow(app, form, env, 'save')

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

        if tk.check_ckan_version(min_version="2.9"):
            offset = url_for("dataset.edit", id=dataset["id"])
        else:
            offset = url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset['name'],
                "extras__0__key": u"spatial",
                "extras__0__value": u'{"Type":Bad Json]'
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form['extras__0__key'] = u'spatial'
            form['extras__0__value'] = u'{"Type":Bad Json]'
            res = helpers.webtest_submit(form, extra_environ=env, name='save')

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error decoding JSON object" in res

    def test_spatial_extra_bad_geojson(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = url_for("dataset.edit", id=dataset["id"])
        else:
            offset = url_for(controller="package", action="edit", id=dataset["id"])
        res = app.get(offset, extra_environ=env)

        if tk.check_ckan_version(min_version="2.9"):
            data = {
                "name": dataset['name'],
                "extras__0__key": u"spatial",
                "extras__0__value": u'{"Type":"Bad_GeoJSON","a":2}'
            }
            res = app.post(offset, environ_overrides=env, data=data)
        else:
            form = res.forms[1]
            form['extras__0__key'] = u'spatial'
            form['extras__0__value'] = u'{"Type":"Bad_GeoJSON","a":2}'
            res = helpers.webtest_submit(form, extra_environ=env, name='save')

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error creating geometry" in res
