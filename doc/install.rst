======================
Installation and Setup
======================

Check the Troubleshooting_ section if you get errors at any stage.

.. _install_postgis:

Install PostGIS and system packages
-----------------------------------

.. note:: If you *only* want to load the :doc:`previews` you don't need to
          install any of the packages on this section and can skip to the
          next one.

.. note:: The package names and paths shown are the defaults on an Ubuntu
          12.04 install (PostgreSQL 9.1 and PostGIS 1.5). Adjust the
          package names and the paths if you are using a different version of
          any of them.

All commands assume an existing CKAN database named ``ckan_default``.


#. Install PostGIS::

        sudo apt-get install postgresql-9.1-postgis

#. Run the following commands. The first one will create the necessary
   tables and functions in the database, and the second will populate
   the spatial reference table::

        sudo -u postgres psql -d ckan_default -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
        sudo -u postgres psql -d ckan_default -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql

   .. note:: If using PostgreSQL 8.x, run the following command to enable
            the necessary language::

                sudo -u postgres createlang plpgsql ckan_default

#. Change the owner to spatial tables to the CKAN user to avoid errors later
   on::
   
   Open the Postgres console::
   
        $ sudo -u postgres psql
        
   Connect to the ``ckan_default`` database::
        
        postgres=# \c ckan_default
        
   Change the ownership for two spatial tables::

        ALTER TABLE spatial_ref_sys OWNER TO ckan_default;
        ALTER TABLE geometry_columns OWNER TO ckan_default;

#. Execute the following command to see if PostGIS was properly
   installed::

        sudo -u postgres psql -d ckan_default -c "SELECT postgis_full_version()"

   You should get something like::

                                             postgis_full_version
        ------------------------------------------------------------------------------------------------------
        POSTGIS="1.5.2" GEOS="3.2.2-CAPI-1.6.2" PROJ="Rel. 4.7.1, 23 September 2009" LIBXML="2.7.7" USE_STATS
        (1 row)


#. Install some other packages needed by the extension dependencies::

     sudo apt-get install python-dev libxml2-dev libxslt1-dev libgeos-c1


Install the extension
---------------------

1. Install this extension into your python environment (where CKAN is also
   installed).

   .. note:: Depending on the CKAN core version you are targeting you will need
             to use a different branch from the extension.

   For a production site, use the ``stable`` branch, unless there is a specific
   branch that targets the CKAN core version that you are using.

   To target the latest CKAN core release::

     (pyenv) $ pip install -e "git+https://github.com/okfn/ckanext-spatial.git@stable#egg=ckanext-spatial"

   To target an old release (if a release branch exists, otherwise use
   ``stable``)::

     (pyenv) $ pip install -e "git+https://github.com/okfn/ckanext-spatial.git@release-v1.8#egg=ckanext-spatial"

   To target CKAN ``master``, use the extension ``master`` branch (ie no
   branch defined)::

    (pyenv) $ pip install -e "git+https://github.com/okfn/ckanext-spatial.git#egg=ckanext-spatial"


2. Install the rest of python modules required by the extension::

     (pyenv) $ pip install -r pip-requirements.txt

To use the :doc:`harvesters`, you will need to install and configure the
harvester extension: `ckanext-harvest`_. Follow the install instructions on
its documentation for details on how to set it up.


Configuration
-------------

Once PostGIS is installed and configured in the database the extension needs
to create a table to store the datasets extent, called ``package_extent``.

This will happen automatically the next CKAN is restarted after adding the
plugins on the configuration ini file (eg when restarting Apache).

If for some reason you need to explicitly create the table beforehand, you can
do it with the following command (with the virtualenv activated)::

  (pyenv) $ paster --plugin=ckanext-spatial spatial initdb [srid] --config=mysite.ini

You can define the SRID of the geometry column. Default is 4326. If you are not
familiar with projections, we recommend to use the default value. To know more
about PostGIS tables, see :doc:`postgis-manual`

Each plugin can be enabled by adding its name to the ``ckan.plugins`` in the
CKAN ini file. For example::

    ckan.plugins = spatial_metadata spatial_query

When enabling the spatial metadata, you can define the projection in which
extents are stored in the database with the following option. Use the EPSG code
as an integer (e.g 4326, 4258, 27700, etc). It defaults to 4326::

    ckan.spatial.srid = 4326


Troubleshooting
---------------

Here are some common problems you may find when installing or using the
extension:

When initializing the spatial tables
++++++++++++++++++++++++++++++++++++

::

    LINE 1: SELECT AddGeometryColumn('package_extent','the_geom', E'4326...
           ^
    HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
     "SELECT AddGeometryColumn('package_extent','the_geom', %s, 'GEOMETRY', 2)" ('4326',)


PostGIS was not installed correctly. Please check the "Setting up PostGIS"
section.

::

    sqlalchemy.exc.ProgrammingError: (ProgrammingError) permission denied for relation spatial_ref_sys


The user accessing the ckan database needs to be owner (or have permissions)
of the geometry_columns and spatial_ref_sys tables.

When migrating to an existing PostGIS database
++++++++++++++++++++++++++++++++++++++++++++++

If you are loading a database dump to an existing PostGIS database, you may
find errors like ::

    ERROR:  type "spheroid" already exists

This means that the PostGIS functions are installed, but you may need to
create the necessary tables anyway. You can force psql to ignore these
errors and continue the transaction with the ON_ERROR_ROLLBACK=on::

    sudo -u postgres psql -d ckan_default -f /usr/share/postgresql/8.4/contrib/postgis-1.5/postgis.sql -v ON_ERROR_ROLLBACK=on

You will still need to populate the spatial_ref_sys table and change the
tables permissions. Refer to the previous section for details on how to do
it.

When performing a spatial query
+++++++++++++++++++++++++++++++

::

    InvalidRequestError: SQL expression, column, or mapped entity expected - got '<class 'ckanext.spatial.model.PackageExtent'>'

The spatial model has not been loaded. You probably forgot to add the
``spatial_metadata`` plugin to your ini configuration file.

::

    InternalError: (InternalError) Operation on two geometries with different SRIDs

The spatial reference system of the database geometry column and the one
used by CKAN differ. Remember, if you are using a different spatial
reference system from the default one (WGS 84 lat/lon, EPSG:4326), you must
define it in the configuration file as follows::

    ckan.spatial.srid = 4258

When running the spatial harvesters
+++++++++++++++++++++++++++++++++++

::

    File "xmlschema.pxi", line 102, in lxml.etree.XMLSchema.__init__ (src/lxml/lxml.etree.c:154475)
    lxml.etree.XMLSchemaParseError: local list type: A type, derived by list or union, must have the simple ur-type definition as base type, not '{http://www.opengis.net/gml}doubleList'., line 1

The XSD validation used by the spatial harvesters requires libxml2 ersion 2.9.

With CKAN you would probably have installed an older version from your
distribution. (e.g. with ``sudo apt-get install libxml2-dev``). You need to
find the SO files for the old version::

    $ find /usr -name "libxml2.so"

For example, it may show it here: ``/usr/lib/x86_64-linux-gnu/libxml2.so``.
The directory of the SO file is used as a parameter to the ``configure`` next
on.

Download the libxml2 source::

    $ cd ~
    $ wget ftp://xmlsoft.org/libxml2/libxml2-2.9.0.tar.gz

Unzip it::

    $ tar zxvf libxml2-2.9.0.tar.gz
    $ cd libxml2-2.9.0/

Configure with the SO directory you found before::

    $ ./configure --libdir=/usr/lib/x86_64-linux-gnu

Now make it and install it::

    $ make
  $ sudo make install

Now check the install by running xmllint::

    $ xmllint --version
    xmllint: using libxml version 20900
     compiled with: Threads Tree Output Push Reader Patterns Writer SAXv1 FTP HTTP DTDValid HTML Legacy C14N Catalog XPath XPointer XInclude Iconv ISO8859X Unicode Regexps Automata Expr Schemas Schematron Modules Debug Zlib

.. _PostGIS: http://postgis.org
.. _ckanext-harvest: https://github.com/okfn/ckanext-harvest
