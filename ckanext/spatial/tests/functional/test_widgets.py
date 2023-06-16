import pytest

from ckanext.spatial.tests.base import SpatialTestBase

from ckan.tests import factories

import ckan.plugins.toolkit as tk


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index", "harvest_setup")
@pytest.mark.ckan_config(
    "ckan.plugins", "test_spatial_plugin spatial_metadata spatial_query")
class TestSpatialWidgets(SpatialTestBase):
    def test_dataset_map(self, app):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}],
        )
        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.read", id=dataset["id"])
        else:
            offset = tk.url_for(controller="package", action="read", id=dataset["id"])
        res = app.get(offset)

        assert 'data-module="dataset-map"' in res
        assert "dataset_map.js" in res

    def test_spatial_search_widget(self, app):
        if tk.check_ckan_version(min_version="2.9"):
            offset = tk.url_for("dataset.search")
        else:
            offset = tk.url_for(controller="package", action="search")
        res = app.get(offset)

        assert 'data-module="spatial-query"' in res
        assert "spatial_query.js" in res
