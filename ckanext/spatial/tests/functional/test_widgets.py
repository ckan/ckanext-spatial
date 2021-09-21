import pytest
from ckan.lib.helpers import url_for

from ckanext.spatial.tests.base import SpatialTestBase

import ckan.tests.factories as factories

import ckan.plugins.toolkit as tk

class TestSpatialWidgets(SpatialTestBase):
    @pytest.mark.usefixtures('with_plugins', 'clean_postgis', 'clean_db', 'clean_index', 'harvest_setup', 'spatial_setup')
    def test_dataset_map(self, app):
        dataset = factories.Dataset(
            extras=[
                {"key": "spatial", "value": self.geojson_examples["point"]}
            ],
        )
        if tk.check_ckan_version(min_version="2.9"):
            offset = url_for("dataset.read", id=dataset["id"])
        else:
            offset = url_for(controller="package", action="read", id=dataset["id"])
        res = app.get(offset)

        assert 'data-module="dataset-map"' in res
        assert "dataset_map.js" in res

    def test_spatial_search_widget(self, app):
        if tk.check_ckan_version(min_version="2.9"):
            offset = url_for("dataset.search")
        else:
            offset = url_for(controller="package", action="search")
        res = app.get(offset)

        assert 'data-module="spatial-query"' in res
        assert "spatial_query.js" in res
