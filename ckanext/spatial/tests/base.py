import os
import re

from sqlalchemy import Table
from nose.plugins.skip import SkipTest

from ckan.model import Session, repo, meta, engine_is_sqlite
from ckanext.spatial.model.package_extent import setup as spatial_db_setup, define_spatial_tables
from ckanext.harvest.model import setup as harvest_model_setup

def setup_postgis_tables():

    conn = Session.connection()
    script_path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), 'scripts', 'postgis.sql')
    script = open(script_path,'r').read()
    for cmd in script.split(';'):
        cmd = re.sub(r'--(.*)|[\n\t]','',cmd)
        if len(cmd):
            conn.execute(cmd)

    Session.commit()


class SpatialTestBase:

    db_srid = 4326

    geojson_examples = {
        'point':'{"type":"Point","coordinates":[100.0,0.0]}',
        'point_2':'{"type":"Point","coordinates":[20,10]}',
        'line':'{"type":"LineString","coordinates":[[100.0,0.0],[101.0,1.0]]}',
        'polygon':'{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}',
        'polygon_holes':'{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]}',
        'multipoint':'{"type":"MultiPoint","coordinates":[[100.0,0.0],[101.0,1.0]]}',
        'multiline':'{"type":"MultiLineString","coordinates":[[[100.0,0.0],[101.0,1.0]],[[102.0,2.0],[103.0,3.0]]]}',
        'multipolygon':'{"type":"MultiPolygon","coordinates":[[[[102.0,2.0],[103.0,2.0],[103.0,3.0],[102.0,3.0],[102.0,2.0]]],[[[100.0,0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]]}'}

    @classmethod
    def setup_class(cls):
        if engine_is_sqlite():
            raise SkipTest("PostGIS is required for this test")
        
        # This will create the PostGIS tables (geometry_columns and
        # spatial_ref_sys) which were deleted when rebuilding the database
        table = Table('geometry_columns', meta.metadata)
        if not table.exists():
            setup_postgis_tables()

        spatial_db_setup()

        # Setup the harvest tables
        harvest_model_setup()

    @classmethod
    def teardown_class(cls):
        repo.rebuild_db()

