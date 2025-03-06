import pytest

import ckantoolkit as tk
import ckan.tests.factories as factories
from ckanext.spatial.tests.base import SpatialTestBase
import ckan.tests.helpers as helpers


@pytest.fixture
def sysadmin_env():
    try:
        from ckan.tests.factories import SysadminWithToken
        user = SysadminWithToken()
        return {'Authorization': user['token']}
    except ImportError:
        # ckan <= 2.9
        from ckan.tests.factories import Sysadmin
        user = Sysadmin()
        return {"REMOTE_USER": user["name"].encode("ascii")}



def _post_data(app, url, data, env):

    if tk.check_ckan_version(min_version="2.11.0a0"):
        res = app.post(url, headers=env, data=data, follow_redirects=False)
    else:
        res = app.post(
            url, environ_overrides=env, data=data, follow_redirects=False
        )
    return res


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
@pytest.mark.ckan_config("ckan.plugins", "spatial_metadata spatial_query")
class TestSpatialExtra(SpatialTestBase):
    def test_spatial_extra_base(self, app, sysadmin_env):

        dataset = factories.Dataset()

        url = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": "spatial",
            "extras__0__value": self.geojson_examples["point"],
        }

        res = _post_data(app, url, data, sysadmin_env)

        assert "Error" not in res, res

        dataset_dict = tk.get_action("package_show")({}, {"id": dataset["id"]})

        assert dataset_dict["extras"][0]["key"] == "spatial"
        assert dataset_dict["extras"][0]["value"] == self.geojson_examples["point"]

    def test_spatial_extra_bad_json(self, app, sysadmin_env):

        dataset = factories.Dataset()

        url = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":Bad Json]',
        }

        res = _post_data(app, url, data, sysadmin_env)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Error decoding JSON object" in res

    def test_spatial_extra_bad_geojson(self, app, sysadmin_env):

        dataset = factories.Dataset()

        url = tk.url_for("dataset.edit", id=dataset["id"])

        data = {
            "name": dataset["name"],
            "extras__0__key": u"spatial",
            "extras__0__value": u'{"Type":"Bad_GeoJSON","a":2}',
        }

        res = _post_data(app, url, data, sysadmin_env)

        assert "Error" in res, res
        assert "Spatial" in res
        assert "Wrong GeoJSON object" in res
