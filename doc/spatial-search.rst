==============
Spatial Search
==============

The spatial extension allows to index datasets with spatial information so they
can be filtered via a spatial search query. This includes both via the web
interface (see the `Spatial Search Widget`_) or via the `action API`_, e.g.::

   http://localhost:5000/api/action/package_search?q=Pollution&ext_bbox=-7.535093,49.208494,3.890688,57.372349

The ``ext_bbox`` parameter must be provided in the form ``ext_bbox={minx},{miny},{maxx},{maxy}``


Setup
-----

To enable the spatial search you need to add the ``spatial_query`` plugin to
your ini file. This plugin in turn requires the ``spatial_metadata`` plugin, eg::

  ckan.plugins = ... spatial_metadata spatial_query

To define which backend to use for the spatial search use the following
configuration option (see `Choosing a backend for the spatial search`_)::

  ckanext.spatial.search_backend = solr-bbox


Geo-Indexing your datasets
--------------------------

Regardless of the backend that you are using, in order to make a dataset
searchable by location, it must have a the location information (a geometry), indexed in
Solr. You can provide this information in two ways.

The ``spatial`` extra field
+++++++++++++++++++++++++++

The easiest way to get your geometries indexed is to use an extra field named ``spatial``.
The value of this extra should be a valid GeoJSON_ geometry, for example::

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
index the information stored in the ``spatial`` in Solr, so it can be reflected on spatial searches.

If you already have datasets when you enable Spatial Search then you'll need to
`rebuild the search index <https://docs.ckan.org/en/latest/maintaining/cli.html?#search-index-rebuild-search-index>`_.


Custom indexing logic
+++++++++++++++++++++

You might not want to use the ``spatial`` extra field. Perhaps you don't want to store the geometries
in the dataset metadata but prefer to do so in a separate table, or you simply want to perform a different
processing on the geometries before indexing.

In this case you need to implement the ``before_dataset_index()`` method of the `IPackageController <https://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IPackageController.before_dataset_index>`_ interface::

    def before_dataset_index(self, dataset_dict):

        # When using the default `solr-bbox` backend (based on bounding boxes), you need to
        # include the following fields in the returned dataset_dict:

        dataset_dict["minx"] = minx
        dataset_dict["maxx"] = maxx
        dataset_dict["miny"] = miny
        dataset_dict["maxy"] = maxy

        # When using the `solr-spatial-field` backend, you need to include the `spatial_geom`
        # field in the returned dataset_dict. This should be a valid geometry in WKT format.
        # Shapely can help you get the WKT representation of your gemetry if you have it in GeoJSON:

        shape = shapely.geometry.shape(geometry)
        wkt = shape.wkt

        dataset_dict["spatial_geom"] = wkt

        # Don't forget to actually return the dict!

        return dataset_dict

Some things to keep in mind:

* Remember, you only need to provide one field, either ``spatial_bbox`` or ``spatial_geom``, depending on
  the backend chosen.
* All indexed geometries should fall within the -180, -90, 180, 90 bounds. If you have polygons crossing the antimeridian (i.e. with longituded lower than -180 or bigger than 180) you'll have to split them across the antimeridian.
* Check the default implementation of ``before_dataset_index()`` in `ckanext/spatial/plugins/__init__.py <https://github.com/ckan/ckanext-spatial/blob/master/ckanext/spatial/plugin/__init__.py>`_ for extra useful checks and validations.
* If you want to store the geometry in the ``spatial`` field but don't want to apply the default automatic indexing logic applied by ckanext-spatial just remove the field from the dict (this won't remove it from the dataset metadata, just from the indexed data)::

    def before_dataset_search(self, dataset_dict):

        dataset_dict.pop("spatial", None)

        return dataset_dict

Choosing a backend for the spatial search
+++++++++++++++++++++++++++++++++++++++++

Ckanext-spatial uses Solr to power the spatial search. The current implementation is tested on Solr 8, which is the supported version, although it might work on previous Solr versions.

.. note:: The are official `Docker images for Solr <https://github.com/ckan/ckan-solr>`_ that have all the configuration needed to perform spatial searches (look for the ones with a ``-spatial`` suffix). This is the easiest way to get started but if you need to customize Solr yourself see below for the modifications needed.

There are different backends supported for the spatial search, it is important
to understand their differences and the necessary setup required when choosing
which one to use. To configure the search backend use the following configuration option::

    ckanext.spatial.search_backend = solr-bbox | solr-spatial-field

The following table summarizes the different spatial search backends:

+-------------------------+--------------------------------------+--------------------+
| Backend                 | Supported geometries indexed in Solr | Solr setup needed  |
+=========================+======================================+====================+
| ``solr-bbox`` (default) | Bounding Box, Polygon (extents only) | Custom fields      |
+-------------------------+--------------------------------------+--------------------+
| ``solr-spatial-field``  | Bounding Box, Point and Polygon      | Custom field + JTS |
+-------------------------+--------------------------------------+--------------------+

.. note:: The default ``solr-bbox`` search backend was previously known as ``solr``. Please update
    your configuration if using this version as it will be removed in the future.


The ``solr-bbox`` backend is probably a good starting point. Here are more
details about the available options (again, you don't need to modify Solr if you are using one of the spatially enabled official Docker images):

* ``solr-bbox``
    This option always indexes just the extent of the provided geometries, whether if it's an
    actual bounding box or not. It supports spatial sorting of the returned results (based on the closeness of their bounding box to the query bounding box). It uses standard Solr float fields so you just need to add the following to your Solr schema::

        <fields>
            <!-- ... -->
            <field name="minx" type="float" indexed="true" stored="true" />
            <field name="maxx" type="float" indexed="true" stored="true" />
            <field name="miny" type="float" indexed="true" stored="true" />
            <field name="maxy" type="float" indexed="true" stored="true" />
        </fields>

* ``solr-spatial-field``
    This option uses the `RPT <https://solr.apache.org/guide/8_11/spatial-search.html#rpt>`_ Solr field, which allows
    to index points, rectangles and more complex geometries like polygons. This requires the install of the `JTS`_ library. See the linked Solr documentation for details on this. Note that it does not support spatial sorting of the returned results.
    You will need to add the following field type and field to your Solr
    schema file to enable it ::

        <types>
            <!-- ... -->
            <fieldType name="location_rpt"   class="solr.SpatialRecursivePrefixTreeFieldType"
                spatialContextFactory="JTS"
                autoIndex="true"
                validationRule="repairBuffer0"
                distErrPct="0.025"
                maxDistErr="0.001"
                distanceUnits="kilometers" />
        </types>

        <fields>
            <!-- ... -->
            <field name="spatial_geom" type="location_rpt" indexed="true" multiValued="true" />
        </fields>

    By default, the ``solr-sptatial-field`` backend uses the following query. This can be customized by setting the ``ckanext.spatial.solr_query`` configuration option, but note that all placeholders must be included::

    "{{!field f=spatial_geom}}Intersects(ENVELOPE({minx}, {maxx}, {maxy}, {miny}))"

.. note:: The old ``postgis`` search backend is no longer supported. You should migrate to one of the other backends instead.



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
.. _JTS: https://github.com/locationtech/jts
.. _GeoJSON: http://geojson.org
