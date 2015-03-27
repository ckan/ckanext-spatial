'''
Common codebase for GeoAlchemy and GeoAlchemy2

It is assumed that the relevant library is already installed, as we check
it against the CKAN version on startup
'''

from ckan.plugins import toolkit
from ckan.model import meta

from sqlalchemy import types, Column, Table

if toolkit.check_ckan_version(min_version='2.3'):
    # CKAN >= 2.3, use GeoAlchemy2

    from geoalchemy2.elements import WKTElement
    from geoalchemy2 import Geometry
    from sqlalchemy import func
    ST_Transform = func.ST_Transform

    legacy_geoalchemy = False
else:
    # CKAN < 2.3, use GeoAlchemy

    from geoalchemy import WKTSpatialElement as WKTElement
    from geoalchemy.functions import transform as ST_Transform
    from geoalchemy import (Geometry, GeometryColumn, GeometryDDL,
                            GeometryExtensionColumn)
    from geoalchemy.postgis import PGComparator

    legacy_geoalchemy = True


def setup_spatial_table(package_extent_class, db_srid=None):

    if legacy_geoalchemy:

        package_extent_table = Table(
            'package_extent', meta.metadata,
            Column('package_id', types.UnicodeText, primary_key=True),
            GeometryExtensionColumn('the_geom', Geometry(2, srid=db_srid))
        )

        meta.mapper(
            package_extent_class,
            package_extent_table,
            properties={'the_geom':
                        GeometryColumn(package_extent_table.c.the_geom,
                                       comparator=PGComparator)}
        )

        GeometryDDL(package_extent_table)
    else:
        package_extent_table = Table(
            'package_extent', meta.metadata,
            Column('package_id', types.UnicodeText, primary_key=True),
            Column('the_geom', Geometry('GEOMETRY', srid=db_srid)),
        )

        meta.mapper(package_extent_class, package_extent_table)

    return package_extent_table
