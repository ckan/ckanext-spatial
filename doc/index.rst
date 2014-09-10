==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================

This extension contains plugins that add geospatial capabilities to CKAN_.

You should have a CKAN instance installed before adding these plugins. Head to
the `CKAN documentation`_ for information on how to set up CKAN.

The extension adds a spatial field to the default CKAN dataset schema,
using PostGIS_ as the backend. This allows to perform spatial queries and
display the dataset extent on the frontend. It also provides harvesters to
import geospatial metadata into CKAN from other sources, as well as commands
to support the OGC CSW standard via pycsw_. Finally, it also includes plugins to preview
spatial formats such as GeoJSON_.


Contents:

.. toctree::
   :maxdepth: 2
   
   install
   spatial-search
   harvesters
   csw
   previews
   map-widgets

.. _CKAN: http://ckan.org
.. _CKAN Documentation: http://docs.ckan.org
.. _PostGIS: http://postgis.org
.. _GeoJSON: http://geojson.org
.. _pycsw: http://pycsw.org
