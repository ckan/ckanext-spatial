import pytest

import ckantoolkit as tk
import ckan.tests.factories as factories
from ckanext.spatial.tests.base import SpatialTestBase
import ckan.tests.helpers as helpers


@pytest.fixture
def env():
    if tk.check_ckan_version(min_version="2.10"):
        user = factories.SysadminWithToken()
        env = {"Authorization": user["token"]}
    else:
        user = factories.User()
        env = {"REMOTE_USER": user["name"]}

    return env


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index", "harvest_setup")
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app, env):

        dataset = factories.Dataset()

        offset = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": u"spatial",
            "extras__0__value": self.geojson_examples["point"],
        }

        app.post(offset, headers=env, data=data, follow_redirects=False)

        dataset_dict = tk.get_action("package_show")({}, {"id": dataset["id"]})

        assert dataset_dict["extras"][0]["key"] == "spatial"
        assert dataset_dict["extras"][0]["value"] == self.geojson_examples["point"]

    def test_spatial_extra_bad_json(self, app, env):

        dataset = factories.Dataset()

        offset = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":Bad Json]',
        }
        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error decoding JSON object" in res

    def test_spatial_extra_bad_geojson(self, app, env):

        dataset = factories.Dataset()

        offset = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":"Bad_GeoJSON","a":2}',
        }
        res = app.post(offset, environ_overrides=env, data=data)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Wrong GeoJSON object" in res
