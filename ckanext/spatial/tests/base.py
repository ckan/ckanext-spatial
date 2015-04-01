import os
import re

from sqlalchemy import Table
from nose.plugins.skip import SkipTest

from ckan.model import Session, repo, meta, engine_is_sqlite
from ckanext.spatial.geoalchemy_common import postgis_version
from ckanext.spatial.model.package_extent import setup as spatial_db_setup
from ckanext.harvest.model import setup as harvest_model_setup

geojson_examples = {
        'point':'{"type":"Point","coordinates":[100.0,0.0]}',
        'point_2':'{"type":"Point","coordinates":[20,10]}',
        'line':'{"type":"LineString","coordinates":[[100.0,0.0],[101.0,1.0]]}',
        'polygon':'{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}',
        'polygon_holes':'{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]}',
        'multipoint':'{"type":"MultiPoint","coordinates":[[100.0,0.0],[101.0,1.0]]}',
        'multiline':'{"type":"MultiLineString","coordinates":[[[100.0,0.0],[101.0,1.0]],[[102.0,2.0],[103.0,3.0]]]}',
        'multipolygon':'{"type":"MultiPolygon","coordinates":[[[[102.0,2.0],[103.0,2.0],[103.0,3.0],[102.0,3.0],[102.0,2.0]]],[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]]}'}


def _execute_script(script_path):

    conn = Session.connection()
    script = open(script_path, 'r').read()
    for cmd in script.split(';'):
        cmd = re.sub(r'--(.*)|[\n\t]', '', cmd)
        if len(cmd):
            conn.execute(cmd)

    Session.commit()


def create_postgis_tables():
    scripts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'scripts')
    if postgis_version()[:1] == '1':
        _execute_script(os.path.join(scripts_path, 'spatial_ref_sys.sql'))
        _execute_script(os.path.join(scripts_path, 'geometry_columns.sql'))
    else:
        _execute_script(os.path.join(scripts_path, 'spatial_ref_sys.sql'))


class SpatialTestBase(object):

    db_srid = 4326

    geojson_examples = geojson_examples

    @classmethod
    def setup_class(cls):
        if engine_is_sqlite():
            raise SkipTest("PostGIS is required for this test")

        # This will create the PostGIS tables (geometry_columns and
        # spatial_ref_sys) which were deleted when rebuilding the database
        table = Table('spatial_ref_sys', meta.metadata)
        if not table.exists():
            create_postgis_tables()

            # When running the tests with the --reset-db option for some
            # reason the metadata holds a reference to the `package_extent`
            # table after being deleted, causing an InvalidRequestError
            # exception when trying to recreate it further on
            if 'package_extent' in meta.metadata.tables:
                meta.metadata.remove(meta.metadata.tables['package_extent'])

        spatial_db_setup()

        # Setup the harvest tables
        harvest_model_setup()

    @classmethod
    def teardown_class(cls):
        repo.rebuild_db()

