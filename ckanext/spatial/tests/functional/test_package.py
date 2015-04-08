import json
from nose.tools import assert_equals

from ckan.model import Session
from ckan.lib.helpers import url_for

import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

from ckanext.spatial.model import PackageExtent
from ckanext.spatial.geoalchemy_common import legacy_geoalchemy
from ckanext.spatial.tests.base import SpatialTestBase


class TestSpatialExtra(SpatialTestBase, helpers.FunctionalTestBase):

    def test_spatial_extra(self):
        app = self._get_test_app()

        user = factories.User()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        dataset = factories.Dataset(user=user)

        offset = url_for(controller='package', action='edit', id=dataset['id'])
        res = app.get(offset, extra_environ=env)

        form = res.forms[1]
        form['extras__0__key'] = u'spatial'
        form['extras__0__value'] = self.geojson_examples['point']

        res = helpers.submit_and_follow(app, form, env, 'save')

        assert 'Error' not in res, res

        package_extent = Session.query(PackageExtent) \
            .filter(PackageExtent.package_id == dataset['id']).first()

        geojson = json.loads(self.geojson_examples['point'])

        assert_equals(package_extent.package_id, dataset['id'])
        if legacy_geoalchemy:
            assert_equals(Session.scalar(package_extent.the_geom.x),
                          geojson['coordinates'][0])
            assert_equals(Session.scalar(package_extent.the_geom.y),
                          geojson['coordinates'][1])
            assert_equals(Session.scalar(package_extent.the_geom.srid),
                          self.db_srid)
        else:
            from sqlalchemy import func
            assert_equals(
                Session.query(func.ST_X(package_extent.the_geom)).first()[0],
                geojson['coordinates'][0])
            assert_equals(
                Session.query(func.ST_Y(package_extent.the_geom)).first()[0],
                geojson['coordinates'][1])
            assert_equals(package_extent.the_geom.srid, self.db_srid)

    def test_spatial_extra_edit(self):
        app = self._get_test_app()

        user = factories.User()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        dataset = factories.Dataset(user=user)

        offset = url_for(controller='package', action='edit', id=dataset['id'])
        res = app.get(offset, extra_environ=env)

        form = res.forms[1]
        form['extras__0__key'] = u'spatial'
        form['extras__0__value'] = self.geojson_examples['point']

        res = helpers.submit_and_follow(app, form, env, 'save')

        assert 'Error' not in res, res

        res = app.get(offset, extra_environ=env)

        form = res.forms[1]
        form['extras__0__key'] = u'spatial'
        form['extras__0__value'] = self.geojson_examples['polygon']

        res = helpers.submit_and_follow(app, form, env, 'save')

        assert 'Error' not in res, res

        package_extent = Session.query(PackageExtent) \
            .filter(PackageExtent.package_id == dataset['id']).first()

        assert_equals(package_extent.package_id, dataset['id'])
        if legacy_geoalchemy:
            assert_equals(
                Session.scalar(package_extent.the_geom.geometry_type),
                'ST_Polygon')
            assert_equals(
                Session.scalar(package_extent.the_geom.srid),
                self.db_srid)
        else:
            from sqlalchemy import func
            assert_equals(
                Session.query(
                    func.ST_GeometryType(package_extent.the_geom)).first()[0],
                'ST_Polygon')
            assert_equals(package_extent.the_geom.srid, self.db_srid)

    def test_spatial_extra_bad_json(self):
        app = self._get_test_app()

        user = factories.User()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        dataset = factories.Dataset(user=user)

        offset = url_for(controller='package', action='edit', id=dataset['id'])
        res = app.get(offset, extra_environ=env)

        form = res.forms[1]
        form['extras__0__key'] = u'spatial'
        form['extras__0__value'] = u'{"Type":Bad Json]'

        res = helpers.webtest_submit(form, extra_environ=env, name='save')

        assert 'Error' in res, res
        assert 'Spatial' in res
        assert 'Error decoding JSON object' in res

    def test_spatial_extra_bad_geojson(self):
        app = self._get_test_app()

        user = factories.User()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        dataset = factories.Dataset(user=user)

        offset = url_for(controller='package', action='edit', id=dataset['id'])
        res = app.get(offset, extra_environ=env)

        form = res.forms[1]
        form['extras__0__key'] = u'spatial'
        form['extras__0__value'] = u'{"Type":"Bad_GeoJSON","a":2}'

        res = helpers.webtest_submit(form, extra_environ=env, name='save')

        assert 'Error' in res, res
        assert 'Spatial' in res
        assert 'Error creating geometry' in res
