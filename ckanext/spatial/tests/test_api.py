from nose.plugins.skip import SkipTest
from nose.tools import assert_equals, assert_raises

from ckan.model import Session
from ckan.lib.search import SearchError
import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

from ckanext.spatial.tests.base import SpatialTestBase


class TestAction(SpatialTestBase):

    def test_spatial_query(self):

        dataset = factories.Dataset(
            extras=[{'key': 'spatial',
                     'value': self.geojson_examples['point']}]
        )

        result = helpers.call_action(
            'package_search',
            extras={'ext_bbox': '-180,-90,180,90'})

        assert_equals(result['count'], 1)
        assert_equals(result['results'][0]['title'], dataset['title'])

    def test_spatial_query_outside_bbox(self):

        factories.Dataset(
            extras=[{'key': 'spatial',
                     'value': self.geojson_examples['point']}]
        )

        result = helpers.call_action(
            'package_search',
            extras={'ext_bbox': '-10,-20,10,20'})

        assert_equals(result['count'], 0)

    def test_spatial_query_wrong_bbox(self):

        assert_raises(SearchError, helpers.call_action,
                      'package_search', extras={'ext_bbox': '-10,-20,10,a'})


class TestHarvestedMetadataAPI(SpatialTestBase, helpers.FunctionalTestBase):

    def test_api(self):
        try:
            from ckanext.harvest.model import (HarvestObject, HarvestJob,
                                               HarvestSource,
                                               HarvestObjectExtra)
        except ImportError:
            raise SkipTest('The harvester extension is needed for these tests')

        content1 = '<xml>Content 1</xml>'
        ho1 = HarvestObject(
            guid='test-ho-1',
            job=HarvestJob(source=HarvestSource(url='http://', type='xx')),
            content=content1)

        content2 = '<xml>Content 2</xml>'
        original_content2 = '<xml>Original Content 2</xml>'
        ho2 = HarvestObject(
            guid='test-ho-2',
            job=HarvestJob(source=HarvestSource(url='http://', type='xx')),
            content=content2)

        hoe = HarvestObjectExtra(
            key='original_document',
            value=original_content2,
            object=ho2)

        Session.add(ho1)
        Session.add(ho2)
        Session.add(hoe)
        Session.commit()

        object_id_1 = ho1.id
        object_id_2 = ho2.id

        app = self._get_test_app()

        # Test redirects for old URLs
        url = '/api/2/rest/harvestobject/{0}/xml'.format(object_id_1)
        r = app.get(url)
        assert_equals(r.status_int, 301)
        assert ('/harvest/object/{0}'.format(object_id_1)
                in r.headers['Location'])

        url = '/api/2/rest/harvestobject/{0}/html'.format(object_id_1)
        r = app.get(url)
        assert_equals(r.status_int, 301)
        assert ('/harvest/object/{0}/html'.format(object_id_1)
                in r.headers['Location'])

        # Access object content
        url = '/harvest/object/{0}'.format(object_id_1)
        r = app.get(url)
        assert_equals(r.status_int, 200)
        assert_equals(r.headers['Content-Type'],
                      'application/xml; charset=utf-8')
        assert_equals(
            r.body,
            '<?xml version="1.0" encoding="UTF-8"?>\n<xml>Content 1</xml>')

        # Access original content in object extra (if present)
        url = '/harvest/object/{0}/original'.format(object_id_1)
        r = app.get(url, status=404)
        assert_equals(r.status_int, 404)

        url = '/harvest/object/{0}/original'.format(object_id_2)
        r = app.get(url)
        assert_equals(r.status_int, 200)
        assert_equals(r.headers['Content-Type'],
                      'application/xml; charset=utf-8')
        assert_equals(
            r.body,
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + '<xml>Original Content 2</xml>')

        # Access HTML transformation
        url = '/harvest/object/{0}/html'.format(object_id_1)
        r = app.get(url)
        assert_equals(r.status_int, 200)
        assert_equals(r.headers['Content-Type'],
                      'text/html; charset=utf-8')
        assert 'GEMINI record about' in r.body

        url = '/harvest/object/{0}/html/original'.format(object_id_1)
        r = app.get(url, status=404)
        assert_equals(r.status_int, 404)

        url = '/harvest/object/{0}/html'.format(object_id_2)
        r = app.get(url)
        assert_equals(r.status_int, 200)
        assert_equals(r.headers['Content-Type'],
                      'text/html; charset=utf-8')
        assert 'GEMINI record about' in r.body

        url = '/harvest/object/{0}/html/original'.format(object_id_2)
        r = app.get(url)
        assert_equals(r.status_int, 200)
        assert_equals(r.headers['Content-Type'],
                      'text/html; charset=utf-8')
        assert 'GEMINI record about' in r.body
