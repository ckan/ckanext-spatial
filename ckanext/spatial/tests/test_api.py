import logging
import json
from pprint import pprint
from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_raises
from ckan.logic.action.create import package_create
from ckan.logic.action.delete import package_delete
from ckan.logic.schema import default_create_package_schema
from ckan import model

from ckan.model import Package, Session
import ckan.lib.search as search
from ckan.tests import CreateTestData, setup_test_search_index,WsgiAppCase
from ckan.tests.functional.api.base import ApiTestCase
from ckan.tests import TestController as ControllerTestCase
from ckanext.spatial.tests.base import SpatialTestBase

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
        schema = default_create_package_schema()
        context = {'model':model,'session':Session,'user':'tester','extras_as_string':True,'schema':schema,'api_version':2}
        package_dict = package_create(context,self.package_fixture_data)
        package_id = context.get('id')

        # Point inside bbox
        offset = self._offset_with_bbox()

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 1
        assert res_dict['results'][0] == package_id

        # Point outside bbox
        offset = self._offset_with_bbox(-10,10,-20,20)

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 0
        assert res_dict['results'] == []

        # Delete the package and ensure it does not come up on
        # search results
        package_delete(context,{'id':package_id})
        offset = self._offset_with_bbox()

        res = self.app.get(offset, status=200)
        res_dict = self.data_from_res(res)

        assert res_dict['count'] == 0
        assert res_dict['results'] == []



class TestActionPackageSearch(SpatialTestBase,WsgiAppCase):

    @classmethod
    def setup_class(self):
        super(TestActionPackageSearch,self).setup_class()
        setup_test_search_index()
        self.package_fixture_data_1 = {
            'name' : u'test-spatial-dataset-search-point-1',
            'title': 'Some Title 1',
            'extras': [{'key':'spatial','value':self.geojson_examples['point']}]
        }
        self.package_fixture_data_2 = {
            'name' : u'test-spatial-dataset-search-point-2',
            'title': 'Some Title 2',
            'extras': [{'key':'spatial','value':self.geojson_examples['point_2']}]
        }

        CreateTestData.create()

    @classmethod
    def teardown_class(self):
        model.repo.rebuild_db()

    def test_1_basic(self):
        schema = default_create_package_schema()
        context = {'model':model,'session':Session,'user':'tester','extras_as_string':True,'schema':schema,'api_version':2}
        package_dict_1 = package_create(context,self.package_fixture_data_1)
        del context['package']
        package_dict_2 = package_create(context,self.package_fixture_data_2)

        postparams = '%s=1' % json.dumps({
                'q': 'test',
                'facet.field': ('groups', 'tags', 'res_format', 'license'),
                'rows': 20,
                'start': 0,
                'extras': {
                    'ext_bbox': '%s,%s,%s,%s' % (10,10,40,40)
                }
            })
        res = self.app.post('/api/action/package_search', params=postparams)
        res = json.loads(res.body)
        result = res['result']

        # Only one dataset returned
        assert_equal(res['success'], True)
        assert_equal(result['count'], 1)
        assert_equal(result['results'][0]['name'], 'test-spatial-dataset-search-point-2')


class TestHarvestedMetadataAPI(WsgiAppCase):


    @classmethod
    def setup_class(cls):
        try:
            from ckanext.harvest.model import HarvestObject, HarvestJob, HarvestSource, HarvestObjectExtra
        except ImportError:
            raise SkipTest('The harvester extension is needed for these tests')

        cls.content1 = '<xml>Content 1</xml>'
        ho1 = HarvestObject(guid='test-ho-1',
                job=HarvestJob(source=HarvestSource(url='http://', type='xx')),
                            content=cls.content1)

        cls.content2 = '<xml>Content 2</xml>'
        cls.original_content2 = '<xml>Original Content 2</xml>'
        ho2 = HarvestObject(guid='test-ho-2',
                job=HarvestJob(source=HarvestSource(url='http://', type='xx')),
                            content=cls.content2)

        hoe = HarvestObjectExtra(key='original_document',
                value=cls.original_content2,
                object=ho2)

        Session.add(ho1)
        Session.add(ho2)
        Session.add(hoe)
        Session.commit()

        cls.object_id_1 = ho1.id
        cls.object_id_2 = ho2.id


    def test_api(self):

        # Test redirects for old URLs
        url = '/api/2/rest/harvestobject/{0}/xml'.format(self.object_id_1)
        r = self.app.get(url)
        assert r.status == 301
        assert '/harvest/object/{0}'.format(self.object_id_1) in r.header_dict['Location']

        url = '/api/2/rest/harvestobject/{0}/html'.format(self.object_id_1)
        r = self.app.get(url)
        assert r.status == 301
        assert '/harvest/object/{0}/html'.format(self.object_id_1) in r.header_dict['Location']


        # Access object content
        url = '/harvest/object/{0}'.format(self.object_id_1)
        r = self.app.get(url)
        assert r.status == 200
        assert r.header_dict['Content-Type'] == 'application/xml; charset=utf-8'
        assert r.body == self.content1

        # Access original content in object extra (if present)
        url = '/harvest/object/{0}/original'.format(self.object_id_1)
        r = self.app.get(url, status=404)
        assert r.status == 404

        url = '/harvest/object/{0}/original'.format(self.object_id_2)
        r = self.app.get(url)
        assert r.status == 200
        assert r.header_dict['Content-Type'] == 'application/xml; charset=utf-8'
        assert r.body == self.original_content2

        # Access HTML transformation
        url = '/harvest/object/{0}/html'.format(self.object_id_1)
        r = self.app.get(url)
        assert r.status == 200
        assert r.header_dict['Content-Type'] == 'text/html; charset=utf-8'
        assert 'GEMINI record about' in r.body

        url = '/harvest/object/{0}/html/original'.format(self.object_id_1)
        r = self.app.get(url, status=404)
        assert r.status == 404

        url = '/harvest/object/{0}/html'.format(self.object_id_2)
        r = self.app.get(url)
        assert r.status == 200
        assert r.header_dict['Content-Type'] == 'text/html; charset=utf-8'
        assert 'GEMINI record about' in r.body

        url = '/harvest/object/{0}/html/original'.format(self.object_id_2)
        r = self.app.get(url)
        assert r.status == 200
        assert r.header_dict['Content-Type'] == 'text/html; charset=utf-8'
        assert 'GEMINI record about' in r.body
