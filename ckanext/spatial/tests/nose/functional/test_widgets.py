from ckan.lib.helpers import url_for

from ckanext.spatial.tests.base import SpatialTestBase

try:
    import ckan.new_tests.helpers as helpers
    import ckan.new_tests.factories as factories
except ImportError:
    import ckan.tests.helpers as helpers
    import ckan.tests.factories as factories


class TestSpatialWidgets(SpatialTestBase, helpers.FunctionalTestBase):

    def test_dataset_map(self):
        app = self._get_test_app()

        user = factories.User()
        dataset = factories.Dataset(
            user=user,
            extras=[{'key': 'spatial',
                     'value': self.geojson_examples['point']}]
        )
        offset = url_for(controller='package', action='read', id=dataset['id'])
        res = app.get(offset)

        assert 'data-module="dataset-map"' in res
        assert 'dataset_map.js' in res

    def test_spatial_search_widget(self):

        app = self._get_test_app()

        offset = url_for(controller='package', action='search')
        res = app.get(offset)

        assert 'data-module="spatial-query"' in res
        assert 'spatial_query.js' in res
