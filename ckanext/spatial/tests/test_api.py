import logging
from pprint import pprint

from ckan.logic.action.create import package_create
from ckan.logic.action.delete import package_delete
from ckan import model

from ckan.model import Package, Session
import ckan.lib.search as search
from ckan.tests import CreateTestData, setup_test_search_index
from ckan.tests.functional.api.base import ApiTestCase
from ckan.tests import TestController as ControllerTestCase
from ckanext.spatial.tests import SpatialTestBase

log = logging.getLogger(__name__)



class TestSpatialApi(ApiTestCase,SpatialTestBase,ControllerTestCase):

    api_version = '2'

    @classmethod
    def setup_class(self):
        super(TestSpatialApi,self).setup_class()
        setup_test_search_index()
        CreateTestData.create_test_user()
        self.package_fixture_data = {
            'name' : u'test-spatial-dataset-search-point',
            'title': 'Some Title',
            'extras': [{'key':'spatial','value':self.geojson_examples['point']}]
        }
        self.base_url = self.offset('/search/dataset/geo')

    def _offset_with_bbox(self,minx=-180,miny=-90,maxx=180,maxy=90,crs=None):
        offset = self.base_url + '?bbox=%s,%s,%s,%s' % (minx,miny,maxx,maxy)
        if crs:
            offset = offset + '&crs=%s' % crs
        return offset

    def test_basic_query(self):
        context = {'model':model,'session':Session,'user':'tester','extras_as_string':True}
        package_dict = package_create(context,self.package_fixture_data)

        # Point inside bbox
        offset = self._offset_with_bbox()

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 1
        assert res_dict['results'][0] == package_dict['id']

        # Point outside bbox
        offset = self._offset_with_bbox(-10,10,-20,20)

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 0
        assert res_dict['results'] == []

        # Delete the package and ensure it does not come up on
        # search results
        package_delete(context,{'id':package_dict['id']})

        offset = self._offset_with_bbox()

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 0
        assert res_dict['results'] == []

