import logging
from pprint import pprint
from ckan import model
from ckan.model import Package, Resource
from ckan.lib.helpers import url_for,json

from ckan.tests import CreateTestData
from ckan.tests.functional.base import FunctionalTestCase
from ckanext.harvest.model import setup as harvest_model_setup
from ckanext.spatial.tests.base import SpatialTestBase

log = logging.getLogger(__name__)


class TestWMSPreview(FunctionalTestCase,SpatialTestBase):

    def setup(self):
        CreateTestData.create()

    def teardown(self):
        model.repo.rebuild_db()

    def test_link_and_map_shown(self):
        from nose.plugins.skip import SkipTest
        raise SkipTest('TODO: Need to update this to use logic functions')

        name = u'annakarenina'
        
        wms_url = 'http://maps.bgs.ac.uk/ArcGIS/services/BGS_Detailed_Geology/MapServer/WMSServer?'
        rev = model.repo.new_revision()
        pkg = Package.get(name)
        pr = Resource(url=wms_url,format='WMS')
        pkg.resources.append(pr)
        pkg.save()
        model.repo.commit_and_remove()
        # Load the dataset page and check if link appears
        offset = url_for(controller='package', action='read',id=name)
        res = self.app.get(offset)

        assert 'View available WMS layers' in res, res

        # Load the dataset map preview page and check if libraries are loaded
        offset = '/dataset/%s/map' % name 
        res = self.app.get(offset)
        assert '<script type="text/javascript" src="/ckanext/spatial/js/wms_preview.js"></script>' in res, res
        assert 'CKAN.WMSPreview.setup("%s");' % wms_url.split('?')[0] in res
 
    def test_link_and_map_not_shown(self):

        name = 'annakarenina'

        offset = url_for(controller='package', action='read',id=name)

        # Load the dataset page and check that link does not appear
        offset = url_for(controller='package', action='read',id=name)
        res = self.app.get(offset)

        assert not 'View available WMS layers' in res, res

        # Load the dataset map preview page and check that libraries are not loaded
        offset = '/dataset/%s/map' % name 
        res = self.app.get(offset, status=400)
        assert '400 Bad Request' in res, res
        assert 'This dataset does not have a WMS resource' in res
        assert not '<script type="text/javascript" src="/ckanext/spatial/js/wms_preview.js"></script>' in res
