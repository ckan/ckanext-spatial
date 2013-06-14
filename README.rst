==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================

This extension contains plugins that add geospatial capabilities to CKAN.
The following plugins are currently available:

* `Spatial model <#geo-indexing-your-datasets>`_ for CKAN datasets and automatic geo-indexing (``spatial_metadata``)
* `Spatial Search`_ - Spatial filtering for the dataset search (``spatial_query``).
* `Spatial Harvesters`_ - for importing spatial metadata into CKAN (``csw_harvester``, ``doc_harvester``, ``waf_harvester``)
* `Harvest Metadata API`_ - a way for a user to view the harvested metadata XML, either as a raw file or styled to view in a web browser. (``spatial_harvest_metadata_api``)
* `WMS Preview`_ - a Web Map Service (WMS) previewer (``wms_preview``).
* `CSW Server`_ - a basic CSW server - to server metadata from the CKAN instance (``cswserver``)

These snippets (to be used with CKAN>=2.0):

* `Dataset Extent Map`_ - Map widget showing a dataset extent.
* `Spatial Search Widget`_ - Map widget integrated on the search form (``spatial_query_widget``).

These libraries:

* `CSW Client`_  - a basic client for accessing a CSW server
* `Validators`_ - uses XSD / Schematron to validate geographic metadata XML. Used by the Spatial Harvesters
* Validators for ISO19139/INSPIRE/GEMINI2 metadata. Used by the Validator.

And these command-line tools:

* `cswinfo`_ - a command-line tool to help making requests of any CSW server

As of October 2012, ckanext-csw and ckanext-inspire were merged into this extension.

About the components
====================

Spatial Search
--------------

The spatial extension allows to index datasets with spatial information so
they can be filtered via a spatial query. This includes both via the web
interface (see the `Spatial Search Widget`_) or via the `action API`__, e.g.::

    POST http://localhost:5000/api/action/package_search
    {
        "q": "Pollution",
        "facet": "true",
        "facet.field": "country",
        "extras": {
            "ext_bbox": "-7.535093,49.208494,3.890688,57.372349"
        }
    }

__ http://docs.ckan.org/en/latest/apiv3.html

To enable the spatial query you need to add the ``spatial_query`` plugin to your
ini file (See `Configuration`_). This plugin requires the ``spatial_metadata``
plugin.

There are different backends supported for the spatial search, it is important
to understand their differences and the necessary setup required when choosing
which one to use. The backend to use is defined with the configuration option
``ckanext.spatial.search_backend``, eg::

    ckanext.spatial.search_backend = solr

The following table summarizes the different spatial search backends:

+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+
| Backend                | Solr Versions | Supported geometries                | Sorting and relevance                                     | Performance with large number of datasets |
+========================+===============+=====================================+===========================================================+===========================================+
| ``solr``               | 3.1 to 4.x    | Bounding Box                        | Yes, spatial sorting combined with other query parameters | Good                                      |
+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+
| ``solr-spatial-field`` | 4.x           | Bounding Box, Point and Polygon (1) | Not implemented                                           | Good                                      |
+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+
| ``postgis``            | 1.3 to 4.x    | Bounding Box                        | Partial, only spatial sorting supported (2)               | Poor                                      |
+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+

(1) Requires JTS
(2) Needs ``ckanext.spatial.use_postgis_sorting`` set to True


We recommend to use the ``solr`` backend whenever possible. Here are more
details about the available options:

* ``solr`` (Recommended)
    This option uses normal Solr fields to index the relevant bits of
    information about the geometry and uses an algorithm function to
    sort results by relevance, keeping any other non-spatial filtering. It only
    supports bounding boxes both for the geometries to be indexed and the input
    query shape. It requires `EDisMax`_ query parser, so it will only work on
    versions of Solr greater than 3.1 (We recommend using Solr 4.x).

    You will need to add the following fields to your Solr schema file to enable it::

        <fields>
            <!-- ... -->
            <field name="bbox_area" type="float" indexed="true" stored="true" />
            <field name="maxx" type="float" indexed="true" stored="true" />
            <field name="maxy" type="float" indexed="true" stored="true" />
            <field name="minx" type="float" indexed="true" stored="true" />
            <field name="miny" type="float" indexed="true" stored="true" />
        </fields>


* ``solr-spatial-field``
    This option uses the `spatial field <http://wiki.apache.org/solr/SolrAdaptersForLuceneSpatial4>`_
    introduced in Solr 4, which allows to index points, rectangles and more
    complex geometries (complex geometries will require `JTS`_, check the
    documentation). Sorting has not yet been implemented, users willing to do so
    will  need to modify the query using the ``before_search`` extension point.

    You will need to add the following field type and field to your Solr schema
    file to enable it (Check the Solr documentation for more information on
    the different parameters, note that you don't need ``spatialContextFactory`` if
    you are not using JTS)::

        <types>
            <!-- ... -->
            <fieldType name="location_rpt"   class="solr.SpatialRecursivePrefixTreeFieldType"
                       spatialContextFactory="com.spatial4j.core.context.jts.JtsSpatialContextFactory"
                       distErrPct="0.025"
                       maxDistErr="0.000009"
                       units="degrees"
                    />
        </types>
        <fields>
            <!-- ... -->
            <field name="spatial_geom"  type="location_rpt"  indexed="true" stored="true" multiValued="true" />
        </fields>

* ``postgis``
    This is the original implementation of the spatial search. It does not
    require any change in the Solr schema and can run on Solr 1.x, but it is
    not as efficient as the previous ones. Basically the bounding box based
    query is performed in PostGIS first, and the ids of the matched datasets
    are added as a filter to the Solr request. This, apart from being much
    less efficient, can led to issues on Solr due to size of the requests (See
    `Solr configuration issues on legacy PostGIS backend`_). There is support
    for a spatial ranking on this backend (setting
    ``ckanext.spatial.use_postgis_sorting`` to True on the ini file), but it
    can not be combined with any other filtering.


.. _edismax: http://wiki.apache.org/solr/ExtendedDisMax
.. _JTS: http://www.vividsolutions.com/jts/JTSHome.htm


Geo-Indexing your datasets
++++++++++++++++++++++++++

Regardless of the backend that you are using, in order to make a dataset
queryable by location, an special extra must be defined, with its key named
'spatial'. The value must be a valid GeoJSON_ geometry, for example::

    {"type":"Polygon","coordinates":[[[2.05827, 49.8625],[2.05827, 55.7447], [-6.41736, 55.7447], [-6.41736, 49.8625], [2.05827, 49.8625]]]}

or::

    { "type": "Point", "coordinates": [-3.145,53.078] }

.. _GeoJSON: http://geojson.org

Every time a dataset is created, updated or deleted, the extension will synchronize
the information stored in the extra with the geometry table.


Spatial Search Widget
+++++++++++++++++++++

The extension provides a snippet to add a map widget to the search form, which allows
filtering results by an area of interest.

To add the map widget to the to the sidebar of the search page, add
this to the dataset search page template
(``myproj/ckanext/myproj/templates/package/search.html``)::

    {% block secondary_content %}

      {% snippet "spatial/snippets/spatial_query.html" %}

    {% endblock %}

By default the map widget will show the whole world. If you want to set
up a different default extent, you can pass an extra ``default_extent`` to the
snippet, either with a pair of coordinates like this::

  {% snippet "spatial/snippets/spatial_query.html", default_extent="[[15.62, -139.21], [64.92, -61.87]]" %}

or with a GeoJSON object describing a bounding box (note the escaped quotes)::

  {% snippet "spatial/snippets/spatial_query.html", default_extent="{ \"type\": \"Polygon\", \"coordinates\": [[[74.89, 29.39],[74.89, 38.45], [60.50, 38.45], [60.50, 29.39], [74.89, 29.39]]]}" %}

You need to load the `spatial_metadata` and `spatial_query` plugins to use this snippet.


Solr configuration issues on legacy PostGIS backend
+++++++++++++++++++++++++++++++++++++++++++++++++++

.. warning::

    If you find any of the issues described in this section it is strongly
    suggested that you consider switching to one of the Solr based backends
    which are much more efficient. These notes are just kept for informative
    purposes.


If using Spatial Query functionality then there is an additional SOLR/Lucene setting that should be used to set the limit on number of datasets searchable with a spatial value.

The setting is ``maxBooleanClauses`` in the solrconfig.xml and the value is the number of datasets spatially searchable. The default is ``1024`` and this could be increased to say ``16384``. For a SOLR single core this will probably be at `/etc/solr/conf/solrconfig.xml`. For a multiple core set-up, there will me several solrconfig.xml files a couple of levels below `/etc/solr`. For that case, *all* of the cores' `solrconfig.xml` should have this setting at the new value.

Example::

      <maxBooleanClauses>16384</maxBooleanClauses>

This setting is needed because PostGIS spatial query results are fed into SOLR using a Boolean expression, and the parser for that has a limit. So if your spatial area contains more than the limit (of which the default is 1024) then you will get this error::

 Dataset search error: ('SOLR returned an error running query...

and in the SOLR logs you see::

 too many boolean clauses
 ...
 Caused by: org.apache.lucene.search.BooleanQuery$TooManyClauses:
 maxClauseCount is set to 1024


Legacy API
++++++++++

The extension adds the following call to the CKAN search API, which returns
datasets with an extent that intersects with the bounding box provided::

    /api/2/search/dataset/geo?bbox={minx,miny,maxx,maxy}[&crs={srid}]

If the bounding box coordinates are not in the same projection as the one
defined in the database, a CRS must be provided, in one of the following
forms:

- urn:ogc:def:crs:EPSG::4326
- EPSG:4326
- 4326



Dataset Extent Map
------------------

Using the snippets provided, if datasets contain a 'spatial' extra like the one
described in the previous section, a map will be shown on the dataset details page.

There are snippets already created to laod the map on the left sidebar or in the main
bdoy of the dataset details page, but these can easily modified to suit your project
needs

To add a map to the sidebar, add this to the dataset details page template
(eg ``myproj/ckanext/myproj/templates/package/read.html``)::

    {% block secondary_content %}
      {{ super() }}

      {% set dataset_extent = h.get_pkg_dict_extra(c.pkg_dict, 'spatial', '') %}
      {% if dataset_extent %}
        {% snippet "spatial/snippets/dataset_map_sidebar.html", extent=dataset_extent %}
      {% endif %}

    {% endblock %}

For adding the map to the main body, add this::

    {% block primary_content %}

      <!-- ... -->

      <article class="module prose">

        <!-- ... -->

        {% set dataset_extent = h.get_pkg_dict_extra(c.pkg_dict, 'spatial', '') %}
        {% if dataset_extent %}
          {% snippet "spatial/snippets/dataset_map.html", extent=dataset_extent %}
        {% endif %}

      </article>
    {% endblock %}


You need to load the ``spatial_metadata`` plugin to use these snippets.

WMS Preview
-----------

To enable the WMS previewer you need to add the ``wms_preview`` plugin to your
ini file (See `Configuration`_). This plugin also requires the `resource_proxy <http://docs.ckan.org/en/latest/data-viewer.html#viewing-remote-resources-the-resource-proxy>`_
plugin (part of CKAN core).

Please note that this is an experimental plugin and may be unstable.

When the plugin is enabled, if datasets contain a resource that has 'WMS' format,
the resource page will load simple map viewer that will attempt to load the
remote service layers, based on the GetCapabilities response.


CSW Server
----------

CSW (Catalogue Service for the Web) is an OGC standard for a web interface that allows you to access metadata (which are records that describe data or services)

The currently supported methods with this CSW Server are:
 * GetCapabilities
 * GetRecords
 * GetRecordById

ckanext-csw provides the CSW service at ``/csw``.

For example you can ask the capabilities of the CSW server installed into CKAN running on 127.0.0.1:5000 like this::

 curl 'http://127.0.0.1:5000/csw?request=GetCapabilities&service=CSW'

The standard CSW response is in XML format.

Spatial Harvesters
------------------

The spatial extension provides some harvesters for importing ISO19139-based
metadata into CKAN, as well as providing a base class for writing new ones.
The harvesters use the interface provided by ckanext-harvest_, so you will need to
install and set it up first.

Once ckanext-harvest is installed, you can add the following plugins to your
ini file to enable the different harvesters (If you are upgrading from a
previous version to CKAN 2.0 see legacy_harvesters_):

 * ``csw_harvester`` - CSW server
 * ``waf_harvester`` - WAF (Web Accessible Folder): An online accessible index page with links to metadata documents
 * ``doc_harvester`` - A single online accessible metadata document.

Have a look at the ckanext-harvest `documentation
<https://github.com/okfn/ckanext-harvest#the-harvesting-interface>`_ if you want to have an
overview of how the CKAN harvesters work, but basically there are three
separate stages:

 * gather_stage - Aggregates all the remote identifiers for a particular source (ie identifiers for a CSW server, files for a WAF).
 * fetch_stage  - Fetches all the remote documents and stores them on the database.
 * import_stage - Performs all the processing for transforming the remote content into a CKAN dataset: validates the document, parses it, converts it to a CKAN dataset dict and saves it in the database.

The extension provides different XSD and schematron based validators. You can specify which validators to use for the remote documents with the following configuration option::

    ckan.spatial.validator.profiles = iso19193eden

By default, the import stage will stop if the validation of the harvested document fails. This can be
modified setting the ``ckanext.spatial.harvest.continue_on_validation_errors`` to True. The setting can
also be applied at the source level setting to True the ``continue_on_validation_errors`` key on the source
configuration object.

By default the harvesting actions (eg creating or updating datasets) will be performed by the internal site admin user.
This is the recommended setting, but if necessary, it can be overridden with the
``ckanext.spatial.harvest.user_name`` config option, eg to support the old hardcoded 'harvest' user::

    ckanext.spatial.harvest.user_name = harvest

Customizing the harvesters
++++++++++++++++++++++++++

The default harvesters provided in this extension can be overriden from
extensions to customize to your needs. You can either extend ``CswHarvester`` or
``WAFfHarverster`` or the main ``SpatialHarvester`` class. There are some extension points that can be safely overriden from your extension. Probably the most useful is ``get_package_dict``, which allows to tweak the dataset fields before creating or updating them. ``transform_to_iso`` allows to hook into transformation mechanisms to transform other formats into ISO1939, the only one directly supported byt he spatial harvesters. Finally, the whole ``import_stage`` can be overriden if the default logic does not suit your needs.

Check the source code of ``ckanext/spatial/harvesters/base.py`` for more details on these functions.

The `ckanext-geodatagov <https://github.com/okfn/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/>`_ extension contains live examples on how to extend the default spatial harvesters and create new ones for other spatial services.




.. _legacy_harvesters:

Legacy harvesters
+++++++++++++++++

Prior to CKAN 2.0, the spatial harvesters available on this extension were
based on the GEMINI2 format, an ISO19139 profile used by the UK Location Programme, and the logic for creating or updating datasets and the resulting fields were somehow adapted to the needs for this particular project. The harvesters were still generic enough and should work fine with other ISO19139 based sources, but extra care has been put to make the new harvesters more generic and robust, so these ones should only be used on existing instances:

 * ``gemini_csw_harvester``
 * ``gemini_waf_harvester``
 * ``gemini_doc_harvester``

If you are using these harvesters please consider upgrading to the new versions described on the previous section.

.. _ckanext-harvest: https://github.com/okfn/ckanext-harvest

Harvest Metadata API
--------------------

Enabled with the ``ckan.plugins = spatial_harvest_metadata_api`` (previous known as ``inspire_api``)

To view the harvest objects (containing the harvested metadata) in the web interface, these controller locations are added:

* raw XML document: /harvest/object/{id}
* HTML representation: /harvest/object/{id}/html

.. note::
    The old URLs are now deprecated and redirect to the previously defined.

    /api/2/rest/harvestobject/<id>/xml
    /api/2/rest/harvestobject/<id>/html


For those harvest objects that have an original document (which was transformed to ISO), this can be accessed via:

* raw XML document: /harvest/object/{id}/original
* HTML representation: /harvest/object/{id}/html/original

The HTML representation is created via an XSLT transformation. The extension provides an XSLT file that should work
on ISO 19139 based documents, but if you want to use your own on your extension, you can override it using
the following configuration options::

    ckanext.spatial.harvest.xslt_html_content = ckanext.myext:templates/xslt/custom.xslt
    ckanext.spatial.harvest.xslt_html_content_original = ckanext.myext:templates/xslt/custom2.xslt

If your project does not transform different metadata types you can ignore the second option.


CSW Client
----------

CswService is a client for python software (such as the CSW Harvester in ckanext-inspire) to conveniently access a CSW server, using the same three methods as the CSW Server supports. It is a wrapper around OWSLib's tool, dealing with the details of the calls and responses to make it very convenient to use, whereas OWSLib on its own is more complicated.

Validators
----------

This library can validate metadata records. It currently supports ISO19139 / INSPIRE / GEMINI2 formats, validating them with XSD and Schematron schemas. It is easily extensible.

To specify which validators to use during harvesting, specify their names in CKAN config. e.g.::

  ckan.spatial.validator.profiles = iso19139,gemini2,constraints


cswinfo
-------

When ckanext-csw is installed, it provides a command-line tool ``cswinfo``, for making queries on CSW servers and returns the info in nicely formatted JSON. This may be more convenient to type than using, for example, curl.

Currently available queries are:
 * getcapabilities
 * getidentifiers
 * getrecords
 * getrecordbyid

For details, type::

 cswinfo csw -h

There are options for querying by only certain types, keywords and typenames as well as configuring the ElementSetName.

The equivalent example to the one above for asking the cabailities is::

 $ cswinfo csw getcapabilities http://127.0.0.1:5000/csw

OWSLib is the library used to actually perform the queries.

Validator
---------

This python library uses Schematron and other schemas to validate the XML.

Here is a simple example of using the Validator library::

    from ckanext.csw.validation import Validator
    xml = etree.fromstring(gemini_string)
    validator = Validator(profiles=('iso19139', 'gemini2', 'constraints'))
    valid, messages = validator.isvalid(xml)
    if not valid:
        print "Validation error: " + messages[0] + ':\n' + '\n'.join(messages[1:])

In DGU, the Validator is integrated here:
https://github.com/okfn/ckanext-inspire/blob/master/ckanext/inspire/harvesters.py#L88

NOTE: The ISO19139 XSD Validator requires system library ``libxml2`` v2.9 (released Sept 2012). If you intend to use this validator then see the section below about installing libxml2.


Setup
=====

Install Python
--------------

1. Install this extension into your python environment (where CKAN is also installed).

   *Note:* Depending on the CKAN core version you are targeting you will need to
   use a different branch from the extension.

   For a production site, use the `stable` branch, unless there is a specific
   branch that targets the CKAN core version that you are using.

   To target the latest CKAN core release::

     (pyenv) $ pip install -e git+https://github.com/okfn/ckanext-spatial.git@stable#egg=ckanext-spatial

   To target an old release (if a release branch exists, otherwise use `stable`)::

     (pyenv) $ pip install -e git+https://github.com/okfn/ckanext-spatial.git@release-v1.8#egg=ckanext-spatial

   To target CKAN `master`, use the extension `master` branch (ie no branch defined)::

     (pyenv) $ pip install -e git+https://github.com/okfn/ckanext-spatial.git#egg=ckanext-spatial

   ``cswserver`` requires that ckanext-harvest is also installed (and enabled) - see https://github.com/okfn/ckanext-harvest

2. Install the rest of python modules required by the extension::

     (pyenv) $ pip install -r pip-requirements.txt

Install System Packages
-----------------------

There are also some system packages that are required:

* PostGIS must be installed and the database needs spatial features enabling to be able to use Spatial Search. See the `Setting up PostGIS`_ section for details.

* Shapely requires libgeos to be installed. If you installed PostGIS on
  the same machine you have already got it, but if PostGIS is located on another server
  you will need to install GEOS on it::

     sudo apt-get install libgeos-c1

* The Validator for ISO19139 requires the install of a particular version of libxml2 - see "Installing libxml2" for full details.

Configuration
-------------

Once PostGIS is installed and configured in your database (see the "Setting up PostGIS" section for details), you need to create some DB tables for the spatial search, by running the following command (with your python env activated)::

  (pyenv) $ paster --plugin=ckanext-spatial spatial initdb [srid] --config=mysite.ini

You can define the SRID of the geometry column. Default is 4326. If you
are not familiar with projections, we recommend to use the default value.

Check the Troubleshooting_ section if you get errors at this stage.

Each plugin can be enabled by adding its name to the ``ckan.plugins`` in the CKAN ini file. For example::

    ckan.plugins = spatial_metadata spatial_query wms_preview

**Note:** Plugin ``spatial_query`` depends on the ``spatial_metadata`` plugin also being enabled.

When enabling the spatial metadata, you can define the projection
in which extents are stored in the database with the following option. Use
the EPSG code as an integer (e.g 4326, 4258, 27700, etc). It defaults to
4326::

    ckan.spatial.srid = 4326


Configuration - CSW Server
--------------------------

Configure the CSW Server with the following keys in your CKAN config file (default values are shown)::

  cswservice.title = Untitled Service - set cswservice.title in config
  cswservice.abstract = Unspecified service description - set cswservice.abstract in config
  cswservice.keywords =
  cswservice.keyword_type = theme
  cswservice.provider_name = Unnamed provider - set cswservice.provider_name in config
  cswservice.contact_name = No contact - set cswservice.contact_name in config
  cswservice.contact_position =
  cswservice.contact_voice =
  cswservice.contact_fax =
  cswservice.contact_address =
  cswservice.contact_city =
  cswservice.contact_region =
  cswservice.contact_pcode =
  cswservice.contact_country =
  cswservice.contact_email =
  cswservice.contact_hours =
  cswservice.contact_instructions =
  cswservice.contact_role =
  cswservice.rndlog_threshold = 0.01
  cswservice.log_xml_length = 1000

cswservice.rndlog_threshold is the percentage of interactions to store in the log file.



SOLR Configuration
------------------

If using Spatial Query functionality then there is an additional SOLR/Lucene setting that should be used to set the limit on number of datasets searchable with a spatial value.

The setting is ``maxBooleanClauses`` in the solrconfig.xml and the value is the number of datasets spatially searchable. The default is ``1024`` and this could be increased to say ``16384``. For a SOLR single core this will probably be at ``/etc/solr/conf/solrconfig.xml``. For a multiple core set-up, there will me several solrconfig.xml files a couple of levels below ``/etc/solr``. For that case, *all* of the cores' ``solrconfig.xml`` should have this setting at the new value.

Example::

      <maxBooleanClauses>16384</maxBooleanClauses>

This setting is needed because PostGIS spatial query results are fed into SOLR using a Boolean expression, and the parser for that has a limit. So if your spatial area contains more than the limit (of which the default is 1024) then you will get this error::

 Dataset search error: ('SOLR returned an error running query...

and in the SOLR logs you see::

 too many boolean clauses
 ...
 Caused by: org.apache.lucene.search.BooleanQuery$TooManyClauses:
 maxClauseCount is set to 1024


Troubleshooting
===============

Here are some common problems you may find when installing or using the
extension:

* When initializing the spatial tables::

    LINE 1: SELECT AddGeometryColumn('package_extent','the_geom', E'4326...
           ^
    HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
     "SELECT AddGeometryColumn('package_extent','the_geom', %s, 'GEOMETRY', 2)" ('4326',)


  PostGIS was not installed correctly. Please check the "Setting up PostGIS" section.
  ::

    sqlalchemy.exc.ProgrammingError: (ProgrammingError) permission denied for relation spatial_ref_sys


  The user accessing the ckan database needs to be owner (or have permissions) of the geometry_columns and spatial_ref_sys tables.

* When performing a spatial query::

    InvalidRequestError: SQL expression, column, or mapped entity expected - got '<class 'ckanext.spatial.model.PackageExtent'>'

  The spatial model has not been loaded. You probably forgot to add the ``spatial_metadata`` plugin to your ini configuration file.
  ::

    InternalError: (InternalError) Operation on two geometries with different SRIDs

  The spatial reference system of the database geometry column and the one used by CKAN differ. Remember, if you are using a different spatial reference system from the default one (WGS 84 lat/lon, EPSG:4326), you must define it in the configuration file as follows::

    ckan.spatial.srid = 4258

Tests
=====

All of the tests need access to the spatial model in Postgres, so to run the tests, specify ``test-core.ini``::

  (pyenv) $ nosetests --ckan --with-pylons=test-core.ini -l ckanext ckanext/spatial/tests

In some places in this extension, ALL exceptions get caught and reported as errors. Since these could be basic coding errors, to aid debugging these during development, you can request exceptions are reraised by setting the DEBUG environment variable::

  export DEBUG=1

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

        paster spatial extents --config=../ckan/development.ini


Setting up PostGIS
==================

PostGIS Configuration
---------------------

*   Install PostGIS::

        sudo apt-get install postgresql-8.4-postgis

    (or ``postgresql-9.1-postgis``, depending on your postgres version)

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

    SELECT AddGeometryColumn('package_extent','the_geom', 4326, 'GEOMETRY', 2);

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
        "enforce_srid_the_geom" CHECK (st_srid(the_geom) = 4326)

Installing libxml2
==================

Version 2.9 is required for the ISO19139 XSD validation.

With CKAN you would probably have installed an older version from your distribution. (e.g. with ``sudo apt-get install libxml2-dev``). You need to find the SO files for the old version::

  $ find /usr -name "libxml2.so"

For example, it may show it here: ``/usr/lib/x86_64-linux-gnu/libxml2.so``. The directory of the SO file is used as a parameter to the ``configure`` next on.

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

Licence
=======

This code falls under different copyrights, depending on when it was contributed and by whom::
* (c) Copyright 2011-2012 Open Knowledge Foundation
* Crown Copyright
* XML/XSD files: copyright of their respective owners, held in the files themselves

All of this code is licensed for reuse under the Open Government Licence
http://www.nationalarchives.gov.uk/doc/open-government-licence/
