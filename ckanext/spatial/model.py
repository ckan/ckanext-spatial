from logging import getLogger

from ckan.lib.base import config
from ckan import model
from ckan.model import Session
from ckan.model.meta import *
from ckan.model.domain_object import DomainObject
from geoalchemy import *
from geoalchemy.postgis import PGComparator

log = getLogger(__name__)

package_extent_table = None

DEFAULT_SRID = 4326

def setup(srid=None):

    if package_extent_table is None:
        define_spatial_tables(srid)
        log.debug('Spatial tables defined in memory')

    if model.repo.are_tables_created():
        if not Table('geometry_columns',metadata).exists() or \
            not Table('spatial_ref_sys',metadata).exists():
            raise Exception('The spatial extension is enabled, but PostGIS ' + \
                    'has not been set up in the database. ' + \
                    'Please refer to the "Setting up PostGIS" section in the README.')


        if not package_extent_table.exists():
            try:
                package_extent_table.create()
            except Exception,e:
                # Make sure the table does not remain incorrectly created
                # (eg without geom column or constraints)
                if package_extent_table.exists():
                    Session.execute('DROP TABLE package_extent')
                    Session.commit()

                raise e

            log.debug('Spatial tables created')
        else:
            log.debug('Spatial tables already exist')
            # Future migrations go here

    else:
        log.debug('Spatial tables creation deferred')


class PackageExtent(DomainObject):
    def __init__(self, package_id=None, the_geom=None):
        self.package_id = package_id
        self.the_geom = the_geom

def define_spatial_tables(db_srid=None):

    global package_extent_table

    if not db_srid:
        db_srid = int(config.get('ckan.spatial.srid', DEFAULT_SRID))
    else:
        db_srid = int(db_srid)

    package_extent_table = Table('package_extent', metadata,
                    Column('package_id', types.UnicodeText, primary_key=True),
                    GeometryExtensionColumn('the_geom', Geometry(2,srid=db_srid)))


    mapper(PackageExtent, package_extent_table, properties={
            'the_geom': GeometryColumn(package_extent_table.c.the_geom,
                                            comparator=PGComparator)})

    # enable the DDL extension
    GeometryDDL(package_extent_table)




