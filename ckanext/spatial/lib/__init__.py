import logging
from string import Template

from ckan.model import Session, Package
from ckan.lib.base import config

from ckanext.spatial.model import PackageExtent
from shapely.geometry import asShape

from geoalchemy import WKTSpatialElement

log = logging.getLogger(__name__)

def get_srid(crs):
    """Returns the SRID for the provided CRS definition
        The CRS can be defined in the following formats
        - urn:ogc:def:crs:EPSG::4326
        - EPSG:4326
        - 4326
       """

    if ':' in crs:
        crs = crs.split(':')
        srid = crs[len(crs)-1]
    else:
       srid = crs

    return int(srid)

def save_package_extent(package_id, geometry = None, srid = None):
    '''Adds, updates or deletes the package extent geometry.

       package_id: Package unique identifier
       geometry: a Python object implementing the Python Geo Interface
                (i.e a loaded GeoJSON object)
       srid: The spatial reference in which the geometry is provided.
             If None, it defaults to the DB srid.

       Will throw ValueError if the geometry object does not provide a geo interface.

    '''
    db_srid = int(config.get('ckan.spatial.srid', '4326'))


    existing_package_extent = Session.query(PackageExtent).filter(PackageExtent.package_id==package_id).first()

    if geometry:
        shape = asShape(geometry)

        if not srid:
            srid = db_srid

        package_extent = PackageExtent(package_id=package_id,the_geom=WKTSpatialElement(shape.wkt, srid))

    # Check if extent exists
    if existing_package_extent:

        # If extent exists but we received no geometry, we'll delete the existing one
        if not geometry:
            existing_package_extent.delete()
            log.debug('Deleted extent for package %s' % package_id)
        else:
            # Check if extent changed
            if Session.scalar(package_extent.the_geom.wkt) <> Session.scalar(existing_package_extent.the_geom.wkt):
                # Update extent
                existing_package_extent.the_geom = package_extent.the_geom
                existing_package_extent.save()
                log.debug('Updated extent for package %s' % package_id)
            else:
                log.debug('Extent for package %s unchanged' % package_id)
    elif geometry:
        # Insert extent
        Session.add(package_extent)
        log.debug('Created new extent for package %s' % package_id)

def validate_bbox(bbox_values):

    if isinstance(bbox_values,basestring):
        bbox_values = bbox_values.split(',')

    if len(bbox_values) is not 4:
        return None

    try:
        bbox = {}
        bbox['minx'] = float(bbox_values[0])
        bbox['miny'] = float(bbox_values[1])
        bbox['maxx'] = float(bbox_values[2])
        bbox['maxy'] = float(bbox_values[3])
    except ValueError,e:
        return None

    return bbox

def bbox_query(bbox,srid=None):

    db_srid = int(config.get('ckan.spatial.srid', '4326'))

    bbox_template = Template('POLYGON (($minx $miny, $minx $maxy, $maxx $maxy, $maxx $miny, $minx $miny))')

    wkt = bbox_template.substitute(minx=bbox['minx'],
                                        miny=bbox['miny'],
                                        maxx=bbox['maxx'],
                                        maxy=bbox['maxy'])

    if srid and srid != db_srid:
        # Input geometry needs to be transformed to the one used on the database
        input_geometry = functions.transform(WKTSpatialElement(wkt,srid),db_srid)
    else:
        input_geometry = WKTSpatialElement(wkt,db_srid)

    extents = Session.query(PackageExtent) \
              .filter(PackageExtent.package_id==Package.id) \
              .filter(PackageExtent.the_geom.intersects(input_geometry)) \
              .filter(Package.state==u'active')

    return extents

