import pytest

import ckantoolkit as tk
import ckan.tests.factories as factories
from ckanext.spatial.tests.base import SpatialTestBase
import ckan.tests.helpers as helpers


@pytest.mark.usefixtures("with_plugins", "with_request_context", "clean_db", "clean_index", "harvest_setup")
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app):

        user = factories.User()
        env = {"REMOTE_USER": user["name"].encode("ascii")}
        dataset = factories.Dataset(user=user)

        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.edit", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="edit", id=dataset["id"])

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

            res = app.get(offset, extra_environ=env)
            res = helpers.submit_and_follow(app, form, env, "save")

        assert "Error" not in res, res

        dataset_dict = tk.get_action("package_show")({}, {"id": dataset["id"]})

        assert dataset_dict["extras"][0]["key"] == "spatial"
        assert dataset_dict["extras"][0]["value"] == self.geojson_examples["point"]

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
