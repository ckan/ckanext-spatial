import logging
from pylons import config

from ckan.lib.helpers import url_for

from ckan.tests.functional.base import FunctionalTestCase

from ckanext.spatial.tests.base import SpatialTestBase

log = logging.getLogger(__name__)


class TestSpatialQueryWidget(FunctionalTestCase,SpatialTestBase):

    def test_widget_shown(self):
        # Load the dataset search page and check if the libraries have been loaded
        offset = url_for(controller='package', action='search')
        res = self.app.get(offset)

        assert '<div id="spatial-search-container">' in res, res
        assert '<script type="text/javascript" src="/ckanext/spatial/js/spatial_search_form.js"></script>' in res
        assert config.get('ckan.spatial.default_extent') in res
