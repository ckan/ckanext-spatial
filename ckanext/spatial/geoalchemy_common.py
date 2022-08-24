from ckan.model import meta, Session

from sqlalchemy import types, Column, Table

from geoalchemy2.elements import WKTElement
from geoalchemy2 import Geometry
from sqlalchemy import func
ST_Transform = func.ST_Transform
ST_Equals = func.ST_Equals

legacy_geoalchemy = False


def postgis_version():

    result = Session.execute('SELECT postgis_lib_version()')

    return result.scalar()


def setup_spatial_table(package_extent_class, db_srid=None):

    # PostGIS 1.5 requires management=True when defining the Geometry
    # field
    management = (postgis_version()[:1] == '1')

    package_extent_table = Table(
        'package_extent', meta.metadata,
        Column('package_id', types.UnicodeText, primary_key=True),
        Column('the_geom', Geometry('GEOMETRY', srid=db_srid,
                                    management=management)),
        extend_existing=True
    )

    meta.mapper(package_extent_class, package_extent_table)

    return package_extent_table


def compare_geometry_fields(geom_field1, geom_field2):

    return Session.scalar(ST_Equals(geom_field1, geom_field2))
