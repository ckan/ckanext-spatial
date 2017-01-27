======================
Installation and Setup
======================

Check the Troubleshooting_ section if you get errors at any stage.

.. _install_postgis:

Install PostGIS and system packages
-----------------------------------

.. warning:: If you are looking for the geospatial preview plugins to render (eg GeoJSON
          or WMS services), these are now located in ckanext-geoview_. They have a much simpler
          installation, so you can skip all the following steps if you just want the previews.


.. note:: The package names and paths shown are the defaults on Ubuntu installs.
          Adjust the package names and the paths if you are using a different platform.

All commands assume an existing CKAN database named ``ckan_default``.

Ubuntu 14.04 (PostgreSQL 9.3 and PostGIS 2.1)
+++++++++++++++++++++++++++++++++++++++++++++

#. Install PostGIS::

        sudo apt-get install postgresql-9.3-postgis-2.1

#. Run the following commands. The first one will create the necessary
   tables and functions in the database, and the second will populate
   the spatial reference table::

        sudo -u postgres psql -d ckan_default -f /usr/share/postgresql/9.3/contrib/postgis-2.1/postgis.sql
        sudo -u postgres psql -d ckan_default -f /usr/share/postgresql/9.3/contrib/postgis-2.1/spatial_ref_sys.sql

#. Change the owner of spatial tables to the CKAN user to avoid errors later
   on::

        sudo -u postgres psql -d ckan_default -c 'ALTER VIEW geometry_columns OWNER TO ckan_default;'
        sudo -u postgres psql -d ckan_default -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan_default;'

#. Execute the following command to see if PostGIS was properly
   installed::

        sudo -u postgres psql -d ckan_default -c "SELECT postgis_full_version()"

   You should get something like::

                                                                 postgis_full_version
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
         POSTGIS="2.1.2 r12389" GEOS="3.4.2-CAPI-1.8.2 r3921" PROJ="Rel. 4.8.0, 6 March 2012" GDAL="GDAL 1.10.1, released 2013/08/26" LIBXML="2.9.1" LIBJSON="UNKNOWN" RASTER
        (1 row)

#. Install some other packages needed by the extension dependencies::

     sudo apt-get install python-dev libxml2-dev libxslt1-dev libgeos-c1


Ubuntu 12.04 (PostgreSQL 9.1 and PostGIS 1.5)
+++++++++++++++++++++++++++++++++++++++++++++

.. note:: You can also install PostGIS 2.x on Ubuntu 12.04 using the packages
    on the UbuntuGIS_ repository. Check the documentation there for details.

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

        sudo -u postgres psql -d ckan_default -c 'ALTER TABLE geometry_columns OWNER TO ckan_default;'
        sudo -u postgres psql -d ckan_default -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan_default;'

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


.. _UbuntuGIS: https://wiki.ubuntu.com/UbuntuGIS

Install the extension
---------------------

1. Install this extension into your python environment (where CKAN is also
   installed)::

    (pyenv) $ pip install -e "git+https://github.com/okfn/ckanext-spatial.git#egg=ckanext-spatial"


2. Install the rest of python modules required by the extension::

     (pyenv) $ pip install -r pip-requirements.txt

To use the :doc:`harvesters`, you will need to install and configure the
harvester extension: `ckanext-harvest`_. Follow the install instructions on
its documentation for details on how to set it up.


Configuration
-------------

Once PostGIS is installed and configured in the database, the extension needs
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

When upgrading the extension to a newer version
+++++++++++++++++++++++++++++++++++++++++++++++

This version of ckanext-spatial requires geoalchemy2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    File "/home/adria/dev/pyenvs/spatial/src/ckanext-spatial/ckanext/spatial/plugin.py", line 39, in <module>
        check_geoalchemy_requirement()
    File "/home/adria/dev/pyenvs/spatial/src/ckanext-spatial/ckanext/spatial/plugin.py", line 37, in check_geoalchemy_requirement
        raise ImportError(msg.format('geoalchemy'))
    ImportError: This version of ckanext-spatial requires geoalchemy2. Please install it by running `pip install geoalchemy2`.
    For more details see the "Troubleshooting" section of the install documentation

Starting from CKAN 2.3, the spatial requires GeoAlchemy2_ instead of GeoAlchemy, as this
is incompatible with the SQLAlchemy version that CKAN core uses. GeoAlchemy2 will get
installed on a new deployment, but if you are upgrading an existing ckanext-spatial
install you'll need to install it manually. With the virtualenv CKAN is installed on
activated, run::

    pip install GeoAlchemy2

Restart the server for the changes to take effect.

AttributeError: type object 'UserDefinedType' has no attribute 'Comparator'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  File "/home/adria/dev/pyenvs/spatial/src/ckanext-spatial/ckanext/spatial/plugin.py", line 30, in check_geoalchemy_requirement
    import geoalchemy2
  File "/home/adria/dev/pyenvs/spatial/local/lib/python2.7/site-packages/geoalchemy2/__init__.py", line 1, in <module>
    from .types import (  # NOQA
  File "/home/adria/dev/pyenvs/spatial/local/lib/python2.7/site-packages/geoalchemy2/types.py", line 15, in <module>
    from .comparator import BaseComparator, Comparator
  File "/home/adria/dev/pyenvs/spatial/local/lib/python2.7/site-packages/geoalchemy2/comparator.py", line 52, in <module>
    class BaseComparator(UserDefinedType.Comparator):
  AttributeError: type object 'UserDefinedType' has no attribute 'Comparator'

You are trying to run the extension against CKAN 2.3, but the requirements for CKAN haven't been updated
(GeoAlchemy2 is crashing against SQLAlchemy 0.7.x). Upgrade the CKAN requirements as described in the
`upgrade documentation`_.

.. _GeoAlchemy2: http://geoalchemy-2.readthedocs.org/en/0.2.4/
.. _upgrade documentation: http://docs.ckan.org/en/latest/maintaining/upgrading/upgrade-source.html

ckan.plugins.core.PluginNotFoundException: geojson_view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 149, in load
    service = _get_service(plugin)
  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 256, in _get_service
    raise PluginNotFoundException(plugin_name)
    ckan.plugins.core.PluginNotFoundException: geojson_view

Your CKAN instance is using the ``geojson_view`` (or ``geojson_preview``) plugin. This plugin has been
moved from ckanext-spatial to ckanext-geoview_. Please install ckanext-geoview following the instructions on the
README.

TemplateNotFound: Template dataviewer/geojson.html cannot be found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    File '/home/pyenvs/spatial/src/ckan/ckan/lib/base.py', line 129 in render_template
      template_path, template_type = render_.template_info(template_name)
    File '/home/pyenvs/spatial/src/ckan/ckan/lib/render.py', line 51 in template_info
      raise TemplateNotFound('Template %s cannot be found' % template_name)
    TemplateNotFound: Template dataviewer/geojson.html cannot be found

See the issue above for details. Install ckanext-geoview_ and additionally run the following on the
ckanext-spatial directory with your virtualenv activated::

     python setup.py develop


ImportError: No module named nongeos_plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 255, in _get_service
    return plugin.load()(name=plugin_name)
  File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pkg_resources.py", line 2147, in load
    ['__name__'])
  ImportError: No module named nongeos_plugin

See the issue above for details. Install ckanext-geoview_ and additionally run the following on the
ckanext-spatial directory with your virtualenv activated::

     python setup.py develop


Plugin class 'GeoJSONPreview' does not implement an interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 File "/home/pyenvs/spatial/src/ckanext-spatial/ckanext/spatial/nongeos_plugin.py", line 175, in <module>
   class GeoJSONPreview(GeoJSONView):
 File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pyutilib/component/core/core.py", line 732, in __new__
   return PluginMeta.__new__(cls, name, bases, d)
 File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pyutilib/component/core/core.py", line 659, in __new__
   raise PluginError("Plugin class %r does not implement an interface, and it has already been defined in environment '%r'." % (str(name), PluginGlobals.env().name))
   pyutilib.component.core.core.PluginError: Plugin class 'GeoJSONPreview' does not implement an interface, and it has already been defined in environment ''pca''

You have correctly installed ckanext-geoview_ but the ckanext-spatial source code is outdated, with references
to the view plugins previously part of this extension. Pull the latest version of the code and re-register the
extension. With the virtualenv CKAN is installed on activated, run::

     git pull
     python setup.py develop



When initializing the spatial tables
++++++++++++++++++++++++++++++++++++

No function matches the given name and argument types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    LINE 1: SELECT AddGeometryColumn('package_extent','the_geom', E'4326...
           ^
    HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
     "SELECT AddGeometryColumn('package_extent','the_geom', %s, 'GEOMETRY', 2)" ('4326',)


PostGIS was not installed correctly. Please check the "Setting up PostGIS"
section.

permission denied for relation spatial_ref_sys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

SQL expression, column, or mapped entity expected - got '<class 'ckanext.spatial.model.PackageExtent'>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


::

    InvalidRequestError: SQL expression, column, or mapped entity expected - got '<class 'ckanext.spatial.model.PackageExtent'>'

The spatial model has not been loaded. You probably forgot to add the
``spatial_metadata`` plugin to your ini configuration file.

Operation on two geometries with different SRIDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
.. _ckanext-geoview: https://github.com/ckan/ckanext-geoview
