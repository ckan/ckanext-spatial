import logging
from pprint import pprint

from ckan.model import Package, Session
from ckan.lib.helpers import url_for,json

from ckan.tests import CreateTestData
from ckan.tests.functional.base import FunctionalTestCase
from ckanext.spatial.model import PackageExtent

from ckanext.spatial.tests.base import SpatialTestBase

log = logging.getLogger(__name__)


class TestPackageController(FunctionalTestCase,SpatialTestBase):

    @classmethod
    def setup_class(cls):
        SpatialTestBase.setup_class()
        cls.extra_environ = {'REMOTE_USER': 'annafan'}

    def setup(self):
        CreateTestData.create()

    def teardown(self):
        CreateTestData.delete()

    def test_new(self):
        name = 'test-spatial-dataset-1'

        offset = url_for(controller='package', action='new')
        res = self.app.get(offset, extra_environ=self.extra_environ)
        assert 'Add - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix + 'name'] = name
        fv[prefix+'extras__0__key'] = u'spatial'
        fv[prefix+'extras__0__value'] = self.geojson_examples['point']

        res = fv.submit('save', extra_environ=self.extra_environ)
        assert not 'Error' in res, res

        package = Package.get(name)

        # Check that a PackageExtent object has been created
        package_extent = Session.query(PackageExtent).filter(PackageExtent.package_id==package.id).first()

        geojson = json.loads(self.geojson_examples['point'])

        assert package_extent
        assert package_extent.package_id == package.id
        assert Session.scalar(package_extent.the_geom.x) == geojson['coordinates'][0]
        assert Session.scalar(package_extent.the_geom.y) == geojson['coordinates'][1]
        assert Session.scalar(package_extent.the_geom.srid) == self.db_srid

    def test_new_bad_json(self):
        name = 'test-spatial-dataset-2'

        offset = url_for(controller='package', action='new')
        res = self.app.get(offset, extra_environ=self.extra_environ)
        assert 'Add - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix + 'name'] = name
        fv[prefix+'extras__0__key'] = u'spatial'
        fv[prefix+'extras__0__value'] = u'{"Type":Bad Json]'

        res = fv.submit('save', extra_environ=self.extra_environ)
        assert 'Error' in res, res
        assert 'Spatial' in res
        assert 'Error decoding JSON object' in res

        # Check that package was not created
        assert not Package.get(name)

    def test_new_bad_geojson(self):
        name = 'test-spatial-dataset-3'

        offset = url_for(controller='package', action='new')
        res = self.app.get(offset, extra_environ=self.extra_environ)
        assert 'Add - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix + 'name'] = name
        fv[prefix+'extras__0__key'] = u'spatial'
        fv[prefix+'extras__0__value'] = u'{"Type":"Bad_GeoJSON","a":2}'

        res = fv.submit('save', extra_environ=self.extra_environ)
        assert 'Error' in res, res
        assert 'Spatial' in res
        assert 'Error creating geometry' in res

        # Check that package was not created
        assert not Package.get(name)

    def test_edit(self):

        name = 'annakarenina'

        offset = url_for(controller='package', action='edit',id=name)
        res = self.app.get(offset, extra_environ=self.extra_environ)
        assert 'Edit - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix+'extras__1__key'] = u'spatial'
        fv[prefix+'extras__1__value'] = self.geojson_examples['point']

        res = fv.submit('save', extra_environ=self.extra_environ)
        assert not 'Error' in res, res

        package = Package.get(name)

        # Check that a PackageExtent object has been created
        package_extent = Session.query(PackageExtent).filter(PackageExtent.package_id==package.id).first()
        geojson = json.loads(self.geojson_examples['point'])

        assert package_extent
        assert package_extent.package_id == package.id
        assert Session.scalar(package_extent.the_geom.x) == geojson['coordinates'][0]
        assert Session.scalar(package_extent.the_geom.y) == geojson['coordinates'][1]
        assert Session.scalar(package_extent.the_geom.srid) == self.db_srid

        # Update the spatial extra
        offset = url_for(controller='package', action='edit',id=name)
        res = self.app.get(offset, extra_environ=self.extra_environ)
        assert 'Edit - Datasets' in res
        fv = res.forms['dataset-edit']
        prefix = ''
        fv[prefix+'extras__1__value'] = self.geojson_examples['polygon']

        res = fv.submit('save', extra_environ=self.extra_environ)
        assert not 'Error' in res, res

        # Check that the PackageExtent object has been updated
        package_extent = Session.query(PackageExtent).filter(PackageExtent.package_id==package.id).first()
        assert package_extent
        assert package_extent.package_id == package.id
        assert Session.scalar(package_extent.the_geom.geometry_type) == 'ST_Polygon'
        assert Session.scalar(package_extent.the_geom.srid) == self.db_srid

