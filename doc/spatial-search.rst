==============
Spatial Search
==============

The spatial extension allows to index datasets with spatial information so they
can be filtered via a spatial search query. This includes both via the web
interface (see the `Spatial Search Widget`_) or via the `action API`_, e.g.::

    POST http://localhost:5000/api/action/package_search
        { "q": "Pollution",
          "facet": "true",
          "facet.field": "country",
          "extras": {
              "ext_bbox": "-7.535093,49.208494,3.890688,57.372349" }
        }

.. versionchanged:: 2.0.1
   Starting from this version the spatial filter it is also supported on GET
   requests:

   http://localhost:5000/api/action/package_search?q=Pollution&ext_bbox=-7.535093,49.208494,3.890688,57.372349


Setup
-----

To enable the spatial search you need to add the ``spatial_query`` plugin to
your ini file. This plugin requires the ``spatial_metadata`` plugin, eg::

  ckan.plugins = [other plugins] spatial_metadata spatial_query

To define which backend to use for the spatial search use the following
configuration option (see `Choosing a backend for the spatial search`_)::

  ckanext.spatial.search_backend = solr


Geo-Indexing your datasets
--------------------------

Regardless of the backend that you are using, in order to make a dataset
searchable by location, it must have a special extra, with its key named
'spatial'. The value must be a valid GeoJSON_ geometry, for example::

    {
      "type":"Polygon",
      "coordinates":[[[2.05827, 49.8625],[2.05827, 55.7447], [-6.41736, 55.7447], [-6.41736, 49.8625], [2.05827, 49.8625]]]
    }

or::

    {
      "type": "Point",
      "coordinates": [-3.145,53.078]
    }


Every time a dataset is created, updated or deleted, the extension will
synchronize the information stored in the extra with the geometry table.

If you already have datasets when you enable Spatial Search then you'll need to
reindex them:

   ckan --config=/etc/ckan/default/development.ini search-index rebuild

..note:: For CKAN 2.8 and below use:

   paster --plugin=ckan search-index rebuild --config=/etc/ckan/default/development.ini


Choosing a backend for the spatial search
+++++++++++++++++++++++++++++++++++++++++

There are different backends supported for the spatial search, it is important
to understand their differences and the necessary setup required when choosing
which one to use.

The following table summarizes the different spatial search backends:

+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+
| Backend                | Solr Versions | Supported geometries                | Sorting and relevance                                     | Performance with large number of datasets |
+========================+===============+=====================================+===========================================================+===========================================+
| ``solr``               | >= 3.1        | Bounding Box                        | Yes, spatial sorting combined with other query parameters | Good                                      |
+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+
| ``solr-spatial-field`` | >= 4.x        | Bounding Box, Point and Polygon [1] | Not implemented                                           | Good                                      |
+------------------------+---------------+-------------------------------------+-----------------------------------------------------------+-------------------------------------------+


[1] Requires JTS


We recommend to use the ``solr`` backend whenever possible. Here are more
details about the available options:

* ``solr`` (Recommended)
    This option uses normal Solr fields to index the relevant bits of
    information about the geometry and uses an algorithm function to sort
    results by relevance, keeping any other non-spatial filtering. It only
    supports bounding boxes both for the geometries to be indexed and the
    input query shape. It requires `EDisMax`_ query parser, so it will only
    work on versions of Solr greater than 3.1 (We recommend using Solr 4.x).

    You will need to add the following fields to your Solr schema file to
    enable it::

        <fields>
            <!-- ... -->
            <field name="bbox_area" type="float" indexed="true" stored="true" />
            <field name="maxx" type="float" indexed="true" stored="true" />
            <field name="maxy" type="float" indexed="true" stored="true" />
            <field name="minx" type="float" indexed="true" stored="true" />
            <field name="miny" type="float" indexed="true" stored="true" />
        </fields>

    The solr schema file is typically located at: (..)/src/ckan/ckan/config/solr/schema.xml

* ``solr-spatial-field``
    This option uses the `spatial field`_ introduced in Solr 4, which allows
    to index points, rectangles and more complex geometries (complex geometries
    will require `JTS`_, check the documentation).
    Sorting has not yet been implemented, users willing to do so will need to
    modify the query using the ``before_search`` extension point.

    You will need to add the following field type and field to your Solr
    schema file to enable it (Check the `Solr documentation`__ for more
    information on the different parameters, note that you don't need
    ``spatialContextFactory`` if you are not using JTS)::

        <types>
            <!-- ... -->
            <fieldType name="location_rpt" class="solr.SpatialRecursivePrefixTreeFieldType"
                spatialContextFactory="com.spatial4j.core.context.jts.JtsSpatialContextFactory"
                autoIndex="true"
                distErrPct="0.025"
                maxDistErr="0.000009"
                distanceUnits="degrees" />
        </types>
        <fields>
            <!-- ... -->
            <field name="spatial_geom"  type="location_rpt" indexed="true" stored="true" multiValued="true" />
        </fields>

.. note:: The old ``postgis`` search backend is deprecated and will be removed in future versions of the extension.
    You should migrate to one of the other backends instead but if you need to keep using it for a while see :ref:`legacy_postgis`.



Spatial Search Widget
---------------------


.. image:: _static/spatial-search-widget.png

The extension provides a snippet to add a map widget to the search form, which
allows filtering results by an area of interest.

To add the map widget to the sidebar of the search page, add the following
block to the dataset search page template
(``myproj/ckanext/myproj/templates/package/search.html``). If your custom
theme is simply extending the CKAN default theme, you will need to add ``{% ckan_extends %}``
to the start of your custom search.html, then continue with this::

    {% block secondary_content %}

      {% snippet "spatial/snippets/spatial_query.html" %}

    {% endblock %}

By default the map widget will show the whole world. If you want to set up a
different default extent, you can pass an extra ``default_extent`` to the
snippet, either with a pair of coordinates like this::

  {% snippet "spatial/snippets/spatial_query.html", default_extent="[[15.62,
      -139.21], [64.92, -61.87]]" %}

or with a GeoJSON object describing a bounding box (note the escaped quotes)::

  {% snippet "spatial/snippets/spatial_query.html", default_extent="{ \"type\":
      \"Polygon\", \"coordinates\": [[[74.89, 29.39],[74.89, 38.45], [60.50,
      38.45], [60.50, 29.39], [74.89, 29.39]]]}" %}

You need to load the ``spatial_metadata`` and ``spatial_query`` plugins to use this
snippet.



Dataset Extent Map
------------------

.. image:: _static/dataset-extent-map.png

Using the snippets provided, if datasets contain a ``spatial`` extra like the
one described in the previous section, a map will be shown on the dataset
details page.

There are snippets already created to load the map on the left sidebar or in
the main body of the dataset details page, but these can be easily modified to
suit your project needs

To add a map to the sidebar, add the following block to the dataset page template (eg
``ckanext-myproj/ckanext/myproj/templates/package/read_base.html``). If your custom
theme is simply extending the CKAN default theme, you will need to add ``{% ckan_extends %}``
to the start of your custom read.html, then continue with this::

    {% block secondary_content %}
      {{ super() }}

      {% set dataset_extent = h.get_pkg_dict_extra(c.pkg_dict, 'spatial', '') %}
      {% if dataset_extent %}
        {% snippet "spatial/snippets/dataset_map_sidebar.html", extent=dataset_extent %}
      {% endif %}

    {% endblock %}

For adding the map to the main body, add this to the main dataset page template (eg
``ckanext-myproj/ckanext/myproj/templates/package/read.html``)::

    {% block primary_content_inner %}

      {{ super() }}

      {% set dataset_extent = h.get_pkg_dict_extra(c.pkg_dict, 'spatial', '') %}
      {% if dataset_extent %}
        {% snippet "spatial/snippets/dataset_map.html", extent=dataset_extent %}
      {% endif %}

    {% endblock %}

You need to load the ``spatial_metadata`` plugin to use these snippets.

.. _action API: http://docs.ckan.org/en/latest/apiv3.html
.. _edismax: http://wiki.apache.org/solr/ExtendedDisMax
.. _JTS: http://www.vividsolutions.com/jts/JTSHome.htm
.. _spatial field: http://wiki.apache.org/solr/SolrAdaptersForLuceneSpatial4
__ `spatial field`_
.. _GeoJSON: http://geojson.org
