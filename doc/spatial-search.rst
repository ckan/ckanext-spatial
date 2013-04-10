Spatial Search
==============

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


Spatial Search Widget
---------------------

**Note**: this plugin requires CKAN 1.6 or higher.

To enable the search map widget you need to add the `spatial_query_widget` plugin to your
ini file (See `Configuration`_). You also need to load both the `spatial_metadata`
and the `spatial_query` plugins.

When the plugin is enabled, a map widget will be shown in the dataset search form,
where users can refine their searchs drawing an area of interest.

