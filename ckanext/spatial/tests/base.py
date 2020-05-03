# -*- coding: utf-8 -*-

import pytest

geojson_examples = {
    "point": '{"type":"Point","coordinates":[100.0,0.0]}',
    "point_2": '{"type":"Point","coordinates":[20,10]}',
    "line": '{"type":"LineString","coordinates":[[100.0,0.0],[101.0,1.0]]}',
    "polygon": '{"type":"Polygon","coordinates":[[[100.0,0.0],[101.0,0.0],'
    '[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}',
    "polygon_holes": '{"type":"Polygon","coordinates":[[[100.0,0.0],'
    '[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],'
    '[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]}',
    "multipoint": '{"type":"MultiPoint","coordinates":'
    '[[100.0,0.0],[101.0,1.0]]}',
    "multiline": '{"type":"MultiLineString","coordinates":[[[100.0,0.0],'
    '[101.0,1.0]],[[102.0,2.0],[103.0,3.0]]]}',
    "multipolygon": '{"type":"MultiPolygon","coordinates":[[[[102.0,2.0],'
    '[103.0,2.0],[103.0,3.0],[102.0,3.0],[102.0,2.0]]],[[[100.0,0.0],'
    '[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]],[[100.2,0.2],'
    '[100.8,0.2],[100.8,0.8],[100.2,0.8],[100.2,0.2]]]]}',
}


class SpatialTestBase(object):
    db_srid = 4326
    geojson_examples = geojson_examples
