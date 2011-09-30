from ckan.lib.base import config
from ckan.model import Session
from ckan.model.meta import *
from ckan.model.domain_object import DomainObject
from geoalchemy import *
from geoalchemy.postgis import PGComparator

db_srid = int(config.get('ckan.spatial.srid', '4326'))
package_extent_table = Table('package_extent', metadata,
                    Column('package_id', types.UnicodeText, primary_key=True),
                    GeometryExtensionColumn('the_geom', Geometry(2,srid=db_srid)))

class PackageExtent(DomainObject):
    def __init__(self, package_id=None, the_geom=None):
        self.package_id = package_id
        self.the_geom = the_geom

mapper(PackageExtent, package_extent_table, properties={
            'the_geom': GeometryColumn(package_extent_table.c.the_geom,
                                            comparator=PGComparator)})

# enable the DDL extension
GeometryDDL(package_extent_table)



DEFAULT_SRID = 4326

def setup(srid=None):

    if not srid:
        srid = DEFAULT_SRID

    srid = str(srid)

    connection = Session.connection()
    connection.execute('CREATE TABLE package_extent(package_id text PRIMARY KEY)')

    connection.execute('SELECT AddGeometryColumn(\'package_extent\',\'the_geom\', %s, \'GEOMETRY\', 2)',srid)

    Session.commit()
