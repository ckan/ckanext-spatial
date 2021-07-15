==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================

.. image:: https://github.com/ckan/ckanext-spatial/workflows/Tests/badge.svg?branch=master
    :target: https://github.com/ckan/ckanext-spatial/actions


This extension contains plugins that add geospatial capabilities to CKAN_,
including:

* A spatial field on the default CKAN dataset schema, that uses PostGIS_
  as the backend and allows to perform spatial queries and to display the
  dataset extent on the frontend.
* Harvesters to import geospatial metadata into CKAN from other sources
  in ISO 19139 format and others.
* Commands to support the CSW standard using pycsw_.

**Note**: The view plugins for rendering spatial formats like GeoJSON_ have
been moved to ckanext-geoview_.

Full documentation, including installation instructions, can be found at:

https://docs.ckan.org/projects/ckanext-spatial/en/latest/


Community
---------

* `Developer mailing list <https://groups.google.com/a/ckan.org/forum/#!forum/ckan-dev>`_
* `Gitter channel <https://gitter.im/ckan/chat>`_
* `Issue tracker <https://github.com/ckan/ckanext-spatial/issues>`_


Contributing
------------

For contributing to ckanext-spatial or its documentation, follow the same
guidelines that apply to CKAN core, described in
`CONTRIBUTING <https://github.com/ckan/ckan/blob/master/CONTRIBUTING.rst>`_.


Copying and License
-------------------

This material is copyright (c) 2011-2021 Open Knowledge Foundation and contributors.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0
whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html

.. _CKAN: http://ckan.org
.. _PostGIS: http://postgis.org
.. _pycsw: http://pycsw.org
.. _GeoJSON: http://geojson.org
.. _ckanext-geoview: https://github.com/ckan/ckanext-geoview
