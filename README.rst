==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================

This extension contains plugins that add geospatial capabilities to CKAN.
The following plugins are currently available:

* Spatial model for CKAN datasets and automatic geo-indexing (`spatial_metadata`)
* Spatial search integration and API call (`spatial_query`).
* Map widget integrated on the search form (`spatial_query_widget`).
* Map widget showing a dataset extent (`dataset_extent_map`).
* A Web Map Service (WMS) previewer (`wms_preview`).

All plugins except the WMS previewer require the `spatial_metadata` plugin.


Dependencies
============

You will need CKAN installed. The present module should be installed at least
with `setup.py develop` if not installed in the normal way with
`setup.py install` or using pip or easy_install.

The extension uses the GeoAlchemy_ and Shapely_ libraries. You can install them
via `pip install -r pip-requirements.txt` from the extension directory.

.. _GeoAlchemy: http://www.geoalchemy.org
.. _Shapely: https://github.com/sgillies/shapely

If you want to use the spatial search API, you will need PostGIS installed
and enable the spatial features of your PostgreSQL database. See the
"Setting up PostGIS" section for details.

Note that Shapely requires libgeos to be installed. If you installed PostGIS on
the same machine you already got it, but if PostGIS is located on another server
you will need to install GEOS::

    sudo apt-get install libgeos-c1



Configuration
=============

You will first need to have have PostGIS installed and configured in your
database (see the "Setting up PostGIS" section for details)

Once this is done, you need to create the necessary DB tables running the
following command (with your python env activated)::

    paster spatial initdb [srid] --config=../ckan/development.ini

You can define the SRID of the geometry column. Default is 4326. If you
are not familiar with projections, we recommend to use the default value.

Problems you may find::

    LINE 1: SELECT AddGeometryColumn('package_extent','the_geom', E'4326...
           ^
    HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
     "SELECT AddGeometryColumn('package_extent','the_geom', %s, 'GEOMETRY', 2)" ('4326',)

PostGIS was not installed correctly. Please check the "Setting up PostGIS" section.

    ::
    sqlalchemy.exc.ProgrammingError: (ProgrammingError) permission denied for relation spatial_ref_sys

The user accessing the ckan database needs to be owner (or have
permissions) of the geometry_columns and spatial_ref_sys tables


Plugins are configured as follows in the CKAN ini file (Add only the ones you
are interested in)::

    ckan.plugins = spatial_metadata spatial_query spatial_query_widget dataset_extent_map wms_preview

When enabling the spatial metadata, you can define the projection
in which extents are stored in the database with the following option. Use
the EPSG code as an integer (e.g 4326, 4258, 27700, etc). It defaults to
4326::

    ckan.spatial.srid = 4326

If you want to define a default map extent for the different map widgets,
(e.g. if you are running a national instace of CKAN) you can do so adding
this configuration option::

    ckan.spatial.default_map_extent=<minx>,<miny>,<maxx>,<maxy>

Coordinates must be in latitude/longitude, e.g.::

    ckan.spatial.default_map_extent=-6.88,49.74,0.50,59.2


Tests
=====

Please note that the tests currently only work with Postgres. You must use the
test-core.ini located in the extension directory to run them. Most of the time
you should run something like::

    nosetests --ckan --with-pylons=test-core.ini ckanext/spatial/tests

Command line interface
======================

The following operations can be run from the command line using the
``paster spatial`` command::

      initdb [srid]
        - Creates the necessary tables. You must have PostGIS installed
        and configured in the database.
        You can privide the SRID of the geometry column. Default is 4326.

      extents
         - creates or updates the extent geometry column for datasets with
          an extent defined in the 'spatial' extra.

The commands should be run from the ckanext-spatial directory and expect
a development.ini file to be present. Most of the time you will specify
the config explicitly though::

        paster extents update --config=../ckan/development.ini


Spatial Query
=============

To enable the spatial query you need to add the `spatial_query` plugin to your
ini file (See `Configuration`_). This plugin requires the `spatial_metadata`
plugin.

The extension adds the following call to the CKAN search API, which returns
datasets with an extent that intersects with the bounding box provided::

    /api/2/search/dataset/geo?bbox={minx,miny,maxx,maxy}[&crs={srid}]

If the bounding box coordinates are not in the same projection as the one
defined in the database, a CRS must be provided, in one of the following
forms:

- urn:ogc:def:crs:EPSG::4326
- EPSG:4326
- 4326

As of CKAN 1.6, you can integrate your spatial query in the full CKAN
search, via the web interface (see the `Spatial Query Widget`_) or
via the `action API`__, e.g.::

    POST http://localhost:5000/api/action/package_search
    {
        "q": "Pollution",
        "extras": {
            "ext_bbox": "-7.535093,49.208494,3.890688,57.372349"
        }
    }

__ http://docs.ckan.org/en/latest/apiv3.html

Geo-Indexing your datasets
--------------------------

In order to make a dataset queryable by location, an special extra must
be defined, with its key named 'spatial'. The value must be a valid GeoJSON_
geometry, for example::

    {"type":"Polygon","coordinates":[[[2.05827, 49.8625],[2.05827, 55.7447], [-6.41736, 55.7447], [-6.41736, 49.8625], [2.05827, 49.8625]]]}

or::

    { "type": "Point", "coordinates": [-3.145,53.078] }

.. _GeoJSON: http://geojson.org

Every time a dataset is created, updated or deleted, the extension will synchronize
the information stored in the extra with the geometry table.


Spatial Query Widget
====================

**Note**: this plugin requires CKAN 1.6 or higher.

To enable the search map widget you need to add the `spatial_query_widget` plugin to your
ini file (See `Configuration`_). You also need to load both the `spatial_metadata`
and the `spatial_query` plugins.

When the plugin is enabled, a map widget will be shown in the dataset search form,
where users can refine their searchs drawing an area of interest.


Dataset Map Widget
==================

To enable the dataset map you need to add the `dataset_map` plugin to your
ini file (See `Configuration`_). You need to load the `spatial_metadata` plugin also.

When the plugin is enabled, if datasets contain a 'spatial' extra like the one
described in the previous section, a map will be shown on the dataset details page.


WMS Previewer
=============

To enable the WMS previewer you need to add the `wms_preview` plugin to your
ini file (See `Configuration`_).

Please note that this is an experimental plugin and may be unstable.

When the plugin is enabled, if datasets contain a resource that has 'WMS' format,
a 'View available WMS layers' link will be displayed on the dataset details page.
It forwards to a simple map viewer that will attempt to load the remote service
layers, based on the GetCapabilities response.



Setting up PostGIS
==================

PostGIS Configuration
---------------------

*   Install PostGIS::

        sudo apt-get install postgresql-8.4-postgis

*   Create a new PostgreSQL database::

        sudo -u postgres createdb [database]

    (If you just want to spatially enable an exisiting database, you can
    ignore this point, but it's a good idea to create a template to
    make easier to create new databases)

*   Many of the PostGIS functions are written in the PL/pgSQL language,
    so we need to enable it in our database::

        sudo -u postgres createlang plpgsql [database]

*   Run the following commands. The first one will create the necessary
    tables and functions in the database, and the second will populate
    the spatial reference table::

        sudo -u postgres psql -d [database] -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql
        sudo -u postgres psql -d [database] -f /usr/share/postgresql/8.4/contrib/postgis-1.5/spatial_ref_sys.sql

    **Note**: depending on your distribution and PostGIS version, the
    scripts may be located on a slightly different location, e.g.::

    /usr/share/postgresql/8.4/contrib/postgis.sql

*   Execute the following command to see if PostGIS was properly
    installed::

        sudo -u postgres psql -d [database] -c "SELECT postgis_full_version()"

    You should get something like::

                                             postgis_full_version
        ------------------------------------------------------------------------------------------------------
        POSTGIS="1.5.2" GEOS="3.2.2-CAPI-1.6.2" PROJ="Rel. 4.7.1, 23 September 2009" LIBXML="2.7.7" USE_STATS
        (1 row)

    Also, if you log into the database, you should see two tables,
    ``geometry_columns`` and ``spatial_ref_sys`` (and probably a view
    called ``geography_columns``).

    Note: This commands will create the two tables owned by the postgres
    user. You probably should make owner the user that will access the
    database from ckan::

        ALTER TABLE spatial_ref_sys OWNER TO [your_user];
        ALTER TABLE geometry_columns OWNER TO [your_user];

More information on PostGIS installation can be found here:

http://postgis.refractions.net/docs/ch02.html#PGInstall

Migrating to an existing PostGIS database
-----------------------------------------

If you are loading a database dump to an existing PostGIS database, you may
find errors like ::

    ERROR:  type "spheroid" already exists

This means that the PostGIS functions are installed, but you may need to
create the necessary tables anyway. You can force psql to ignore these
errors and continue the transaction with the ON_ERROR_ROLLBACK=on::

    sudo -u postgres psql -d [database] -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql -v ON_ERROR_ROLLBACK=on

You will still need to populate the spatial_ref_sys table and change the
tables permissions. Refer to the previous section for details on how to do
it.


Setting up a spatial table
--------------------------

**Note:** If you run the ``initdb`` command, the table was already created for
you. This section just describes what's going on for those who want to know
more.

To be able to store geometries and perform spatial operations, PostGIS
needs to work with geometry fields. Geometry fields should always be
added via the ``AddGeometryColumn`` function::

    CREATE TABLE package_extent(
        package_id text PRIMARY KEY
    );

    ALTER TABLE package_extent OWNER TO [your_user];

    SELECT AddGeometryColumn('package_extent','the_geom', 4326, 'POLYGON', 2);

This will add a geometry column in the ``package_extent`` table called
``the_geom``, with the spatial reference system EPSG:4326. The stored
geometries will be polygons, with 2 dimensions (The actual table on CKAN
uses the GEOMETRY type to support multiple geometry types).

Have a look a the table definition, and see how PostGIS has created
three constraints to ensure that the geometries follow the parameters
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
        "enforce_geotype_the_geom" CHECK (geometrytype(the_geom) = 'POLYGON'::text OR the_geom IS NULL)
        "enforce_srid_the_geom" CHECK (st_srid(the_geom) = 4326)
