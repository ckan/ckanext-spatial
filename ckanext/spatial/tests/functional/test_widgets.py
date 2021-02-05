import pytest
from ckan.lib.helpers import url_for

from ckanext.spatial.tests.base import SpatialTestBase

import ckan.tests.factories as factories


class TestSpatialWidgets(SpatialTestBase):
    @pytest.mark.usefixtures("spatial_clean_db")
    def test_dataset_map(self, app):
        dataset = factories.Dataset(
            extras=[
                {"key": "spatial", "value": self.geojson_examples["point"]}
            ],
        )
        offset = url_for("dataset.read", id=dataset["id"])
        res = app.get(offset)

        assert 'data-module="dataset-map"' in res
        assert "dataset_map.js" in res

    def test_spatial_search_widget(self, app):
        offset = url_for("dataset.search")
        res = app.get(offset)

        assert 'data-module="spatial-query"' in res
        assert "spatial_query.js" in res
