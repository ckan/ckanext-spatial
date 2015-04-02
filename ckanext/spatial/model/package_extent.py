from logging import getLogger

from sqlalchemy import Table

from ckan.lib.base import config
from ckan import model
from ckan.model import Session
from ckan.model import meta
from ckan.model.domain_object import DomainObject

from ckanext.spatial.geoalchemy_common import setup_spatial_table

log = getLogger(__name__)

package_extent_table = None

DEFAULT_SRID = 4326 #(WGS 84)

def setup(srid=None):

    if package_extent_table is None:
        define_spatial_tables(srid)
        log.debug('Spatial tables defined in memory')

    if model.package_table.exists():
        if not Table('geometry_columns',meta.metadata).exists() or \
            not Table('spatial_ref_sys',meta.metadata).exists():
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

    package_extent_table = setup_spatial_table(PackageExtent, db_srid)
