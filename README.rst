==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================


This extension contains plugins that add geospatial capabilities to CKAN_,
including:

* A spatial field on the default CKAN dataset schema, that uses PostGIS_
  as the backend and allows to perform spatial queries and to display the
  dataset extent on the frontend.
* Harvesters to import geospatial metadata into CKAN from other sources
  in ISO 19139 format and others.
* Commands to support the CSW standard using pycsw_.
* Plugins to preview spatial formats such as GeoJSON_.

Full documentation, including installation instructions, can be found at:
    
http://docs.ckan.org/projects/ckanext-spatial


Community
---------

* Developer mailing list: `ckan-dev@lists.okfn.org <http://lists.okfn.org/mailman/listinfo/ckan-dev>`_
* Developer IRC channel: `#ckan on irc.freenode.net <http://webchat.freenode.net/?channels=ckan>`_
* `Issue tracker <https://github.com/okfn/ckanext-spatial/issues>`_


Contributing
------------

For contributing to ckanext-spatial or its documentation, follow the same
guidelines that apply to CKAN core, described in
`CONTRIBUTING <https://github.com/okfn/ckan/blob/master/CONTRIBUTING.rst>`_.


Copying and License
-------------------

This material is copyright (c) 2006-2011 Open Knowledge Foundation.

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0
whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html

.. _CKAN: http://ckan.org
.. _PostGIS: http://postgis.org
.. _pycsw: http://pycsw.org
.. _GeoJSON: http://geojson.org

