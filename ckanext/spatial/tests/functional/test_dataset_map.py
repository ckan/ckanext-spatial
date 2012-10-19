import logging
from pprint import pprint

from ckan.model import Package, Session
from ckan import model
from ckan.lib.helpers import url_for,json

from ckan.tests import CreateTestData
from ckan.tests.functional.base import FunctionalTestCase
from ckanext.spatial.tests.base import SpatialTestBase

log = logging.getLogger(__name__)


class TestDatasetMap(FunctionalTestCase,SpatialTestBase):
    def setup(self):
        CreateTestData.create()

    def teardown(self):
        model.repo.rebuild_db()

    def test_map_shown(self):
        extra_environ = {'REMOTE_USER': 'annafan'}
        name = 'annakarenina'

        offset = url_for(controller='package', action='edit',id=name)
        res = self.app.get(offset, extra_environ=extra_environ)
        assert 'Edit - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix+'extras__1__key'] = u'spatial'
        fv[prefix+'extras__1__value'] = self.geojson_examples['point']

        res = fv.submit('save', extra_environ=extra_environ)
        assert not 'Error' in res, res

        # Load the dataset page and check if the libraries have been loaded
        offset = url_for(controller='package', action='read',id=name)
        res = self.app.get(offset)

        assert '<div class="dataset-map subsection">' in res, res
        assert '<script type="text/javascript" src="/ckanext/spatial/js/dataset_map.js"></script>' in res
        assert self.geojson_examples['point'] in res
