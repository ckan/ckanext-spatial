'''
Common codebase for GeoAlchemy and GeoAlchemy2

It is assumed that the relevant library is already installed, as we check
it against the CKAN version on startup
'''

from ckan.plugins import toolkit
from ckan.model import meta, Session

from sqlalchemy import types, Column, Table

if toolkit.check_ckan_version(min_version='2.3'):
    # CKAN >= 2.3, use GeoAlchemy2

    from geoalchemy2.elements import WKTElement
    from geoalchemy2 import Geometry
    from sqlalchemy import func
    ST_Transform = func.ST_Transform
    ST_Equals = func.ST_Equals

    legacy_geoalchemy = False
else:
    # CKAN < 2.3, use GeoAlchemy

    from geoalchemy import WKTSpatialElement as WKTElement
    from geoalchemy import functions
    ST_Transform = functions.transform
    ST_Equals = functions.equals

    from geoalchemy import (Geometry, GeometryColumn, GeometryDDL,
                            GeometryExtensionColumn)
    from geoalchemy.postgis import PGComparator

    legacy_geoalchemy = True


def postgis_version():

    result = Session.execute('SELECT postgis_lib_version()')

    return result.scalar()


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

        # PostGIS 1.5 requires management=True when defining the Geometry
        # field
        management = (postgis_version()[:1] == '1')

        package_extent_table = Table(
            'package_extent', meta.metadata,
            Column('package_id', types.UnicodeText, primary_key=True),
            Column('the_geom', Geometry('GEOMETRY', srid=db_srid,
                                        management=management)),
        )

        meta.mapper(package_extent_class, package_extent_table)

    return package_extent_table


def compare_geometry_fields(geom_field1, geom_field2):

    return Session.scalar(ST_Equals(geom_field1, geom_field2))
