import logging
from string import Template

import six
from sqlalchemy import Table, Column, types, func

from geoalchemy2.elements import WKTElement
from geoalchemy2 import Geometry

from shapely.geometry import shape

from ckan.lib.base import config
from ckan import model
from ckan.model import meta, Session, Package
from ckan.model.domain_object import DomainObject


log = logging.getLogger(__name__)

package_extent_table = None

DEFAULT_SRID = 4326  # (WGS 84)

ST_Transform = func.ST_Transform
ST_Equals = func.ST_Equals


def setup(srid=None):

    if package_extent_table is None:
        define_spatial_tables(srid)
        log.debug("Spatial tables defined in memory")

    if model.package_table.exists():
        if (
            not Table("geometry_columns", meta.metadata).exists()
            or not Table("spatial_ref_sys", meta.metadata).exists()
        ):
            raise Exception(
                "The spatial extension is enabled, but PostGIS "
                + "has not been set up in the database. "
                + 'Please refer to the "Setting up PostGIS" section in the README.'
            )

        if not package_extent_table.exists():
            try:
                package_extent_table.create()
            except Exception as e:
                # Make sure the table does not remain incorrectly created
                # (eg without geom column or constraints)
                if package_extent_table.exists():
                    Session.execute("DROP TABLE package_extent")
                    Session.commit()

                raise e

            log.debug("Spatial tables created")
        else:
            log.debug("Spatial tables already exist")
            # Future migrations go here

    else:
        log.debug("Spatial tables creation deferred")


class PackageExtent(DomainObject):
    def __init__(self, package_id=None, the_geom=None):
        self.package_id = package_id
        self.the_geom = the_geom


def define_spatial_tables(db_srid=None):

    global package_extent_table

    if not db_srid:
        db_srid = int(config.get("ckan.spatial.srid", DEFAULT_SRID))
    else:
        db_srid = int(db_srid)

    package_extent_table = setup_spatial_table(PackageExtent, db_srid)


def postgis_version():

    result = Session.execute("SELECT postgis_lib_version()")

    return result.scalar()


def setup_spatial_table(package_extent_class, db_srid=None):

    # PostGIS 1.5 requires management=True when defining the Geometry
    # field
    management = postgis_version()[:1] == "1"

    package_extent_table = Table(
        "package_extent",
        meta.metadata,
        Column("package_id", types.UnicodeText, primary_key=True),
        Column("the_geom", Geometry("GEOMETRY", srid=db_srid, management=management)),
        extend_existing=True,
    )

    meta.mapper(package_extent_class, package_extent_table)

    return package_extent_table


def compare_geometry_fields(geom_field1, geom_field2):

    return Session.scalar(ST_Equals(geom_field1, geom_field2))


def save_package_extent(package_id, geometry=None, srid=None):
    """Adds, updates or deletes the package extent geometry.

    package_id: Package unique identifier
    geometry: a Python object implementing the Python Geo Interface
             (i.e a loaded GeoJSON object)
    srid: The spatial reference in which the geometry is provided.
          If None, it defaults to the DB srid.

    Will throw ValueError if the geometry object does not provide a geo interface.

    The responsibility for calling model.Session.commit() is left to the
    caller.
    """
    db_srid = int(config.get("ckan.spatial.srid", "4326"))

    existing_package_extent = (
        Session.query(PackageExtent)
        .filter(PackageExtent.package_id == package_id)
        .first()
    )

    if geometry:
        geom_obj = shape(geometry)

        if not srid:
            srid = db_srid

        package_extent = PackageExtent(
            package_id=package_id, the_geom=WKTElement(geom_obj.wkt, srid)
        )

    # Check if extent exists
    if existing_package_extent:

        # If extent exists but we received no geometry, we'll delete the existing one
        if not geometry:
            existing_package_extent.delete()
            log.debug("Deleted extent for package %s" % package_id)
        else:
            # Check if extent changed
            if not compare_geometry_fields(
                package_extent.the_geom, existing_package_extent.the_geom
            ):
                # Update extent
                existing_package_extent.the_geom = package_extent.the_geom
                existing_package_extent.save()
                log.debug("Updated extent for package %s" % package_id)
            else:
                log.debug("Extent for package %s unchanged" % package_id)
    elif geometry:
        # Insert extent
        Session.add(package_extent)
        log.debug("Created new extent for package %s" % package_id)


def _bbox_2_wkt(bbox, srid):
    """
    Given a bbox dictionary, return a WKTSpatialElement, transformed
    into the database\'s CRS if necessary.

    returns e.g. WKTSpatialElement("POLYGON ((2 0, 2 1, 7 1, 7 0, 2 0))", 4326)
    """
    db_srid = int(config.get("ckan.spatial.srid", "4326"))

    bbox_template = Template(
        "POLYGON (($minx $miny, $minx $maxy, $maxx $maxy, $maxx $miny, $minx $miny))"
    )

    wkt = bbox_template.substitute(
        minx=bbox["minx"], miny=bbox["miny"], maxx=bbox["maxx"], maxy=bbox["maxy"]
    )

    if srid and srid != db_srid:
        # Input geometry needs to be transformed to the one used on the database
        input_geometry = ST_Transform(WKTElement(wkt, srid), db_srid)
    else:
        input_geometry = WKTElement(wkt, db_srid)
    return input_geometry


def bbox_query(bbox, srid=None):
    """
    Performs a spatial query of a bounding box.

    bbox - bounding box dict

    Returns a query object of PackageExtents, which each reference a package
    by ID.
    """

    input_geometry = _bbox_2_wkt(bbox, srid)

    extents = (
        Session.query(PackageExtent)
        .filter(PackageExtent.package_id == Package.id)
        .filter(PackageExtent.the_geom.intersects(input_geometry))
        .filter(Package.state == u"active")
    )
    return extents


def bbox_query_ordered(bbox, srid=None):
    """
    Performs a spatial query of a bounding box. Returns packages in order
    of how similar the data\'s bounding box is to the search box (best first).

    bbox - bounding box dict

    Returns a query object of PackageExtents, which each reference a package
    by ID.
    """

    input_geometry = _bbox_2_wkt(bbox, srid)

    params = {
        "query_bbox": six.text_type(input_geometry),
        "query_srid": input_geometry.srid,
    }

    # First get the area of the query box
    sql = "SELECT ST_Area(ST_GeomFromText(:query_bbox, :query_srid));"
    params["search_area"] = Session.execute(sql, params).fetchone()[0]

    # Uses spatial ranking method from "USGS - 2006-1279" (Lanfear)
    sql = """SELECT ST_AsBinary(package_extent.the_geom) AS package_extent_the_geom,
                    POWER(ST_Area(ST_Intersection(package_extent.the_geom, ST_GeomFromText(:query_bbox, :query_srid))),2)/ST_Area(package_extent.the_geom)/:search_area as spatial_ranking,
                    package_extent.package_id AS package_id
             FROM package_extent, package
             WHERE package_extent.package_id = package.id
                AND ST_Intersects(package_extent.the_geom, ST_GeomFromText(:query_bbox, :query_srid))
                AND package.state = 'active'
             ORDER BY spatial_ranking desc"""
    extents = Session.execute(sql, params).fetchall()
    log.debug(
        "Spatial results: %r",
        [
            ("%.2f" % extent.spatial_ranking, extent.package_id)
            for extent in extents[:20]
        ],
    )
    return extents
