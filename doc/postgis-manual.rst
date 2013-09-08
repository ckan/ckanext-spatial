==========================
Setting up a PostGIS table
==========================

.. note:: The extension will generally set up the table automatically for you,
    and also running the ``initdb`` command will have the same effect. This
    section just describes what's going on for those who want to know more.

To be able to store geometries and perform spatial operations, PostGIS_
needs to work with geometry fields. Geometry fields should always be
added via the ``AddGeometryColumn`` function::

    CREATE TABLE package_extent(
        package_id text PRIMARY KEY
    );

    ALTER TABLE package_extent OWNER TO ckan_default;

    SELECT AddGeometryColumn('package_extent','the_geom', 4326, 'GEOMETRY', 2);

This will add a geometry column in the ``package_extent`` table called
``the_geom``, with the spatial reference system EPSG:4326. The stored
geometries will be polygons, with 2 dimensions (The CKAN table uses the
GEOMETRY type to support multiple geometry types).

Have a look a the table definition, and see how PostGIS has created
some constraints to ensure that the geometries follow the parameters
defined in the geometry column creation::

    # \d package_extent

       Table "public.package_extent"
       Column   |   Type   | Modifiers
    ------------+----------+-----------
     package_id | text     | not null
     the_geom   | geometry |
    Indexes:
        "package_extent_pkey" PRIMARY KEY, btree (package_id)
    Check constraints:
        "enforce_dims_the_geom" CHECK (st_ndims(the_geom) = 2)
        "enforce_srid_the_geom" CHECK (st_srid(the_geom) = 4326)

.. _PostGIS: http://postgis.org
