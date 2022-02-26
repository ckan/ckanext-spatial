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

CIOOS-SIOOC Changes
===================
* Change anchor pattern matching in WAF harvester to capture html anchor tags
  produced by ERDDAP on its WAF page [44b84fb](https://github.com/cioos-siooc/ckanext-spatial/commit/44b84fbd6bb40005bd75510d05f6818d9ff8de62)
* If using the default spatial indexing (solr) only bounding box's are excepted
  as dataset extents. We made a small change to the before_indexing function to
  convert points to a 2m by 2m bounding box so that datasets with point extents
  would work with the default indexing. [fcf411b](https://github.com/cioos-siooc/ckanext-spatial/commit/fcf411be168e585da983486d111decc6e85be8ed)
* adjusted icon path for map to work with ckan sites that are not hosted at the
  root url. Also added alterntive_url to spatial widget which allows placing the
  map on pages other then the default dataset page.
  [3c66e24](https://github.com/cioos-siooc/ckanext-spatial/commit/3c66e24e59fc6138c089538307c9ff3ec57c99b3),
  [7abd586](https://github.com/cioos-siooc/ckanext-spatial/commit/7abd58658bc3595c8a0e584f0f3e9be95fb766ea)
* Add config option to control if the spatial widget (map) expands when doing a
  spatial search. Can be set by adding
  ```
  ckan.spatial.spatial_widget_expands = true | false
  ```
   to production.ini
  [cc588c1](https://github.com/cioos-siooc/ckanext-spatial/commit/cc588c1f8d92a0fbee088398ee02f719eabf0bc2)
* Added custom csw harvester for geonetwork to handle pulling groups from
  geonetwork and populating in ckan. To make use of this feature you must
  specify a group mapping dictionary in the config for the harvester. Group mapping follows the same format as used by the ckan harvester.
  [484e39e](https://github.com/cioos-siooc/ckanext-spatial/commit/484e39ec841f37dbe0a5f67c23b3bc68bec82caa),
  [08e4832](https://github.com/cioos-siooc/ckanext-spatial/commit/08e483227ef8ed15fbedab47fc4da45f02254d35),
  [5695d1d](https://github.com/cioos-siooc/ckanext-spatial/commit/5695d1d900ef34e4a4143719dbdfbc24133d180e)
* Add group mapping to WAF harvester.
[0f25a0b](https://github.com/cioos-siooc/ckanext-spatial/commit/0f25a0bdb591b413f89d4e716118fd8269aede1b),
[20236c8](https://github.com/cioos-siooc/ckanext-spatial/commit/20236c85bff69a2ab03a7e9b6aea28478fee840e)
* Add remote_orgs support to spatial base. Harvesting of remote organizations
  works similarly to the ckan harvester base but matches on organization name.
  Name is pulled from metadata in responsible party or metadata contact fields.
  Also added is an organization_mapping field that works similarly to
  group_mapping. Temote organization names that match the dictionary key are
  mapped to local org names. The local names are used as organization titles and
  regex replaced to conform to ckan org names internally. To use add
  ```
  "remote_orgs": "create"
  "organization_mapping":{"REMOTE ORG NAME": "Local Org Name"}
  ```
  to the harvester config. [5d0fbd0](https://github.com/cioos-siooc/ckanext-spatial/commit/5d0fbd0e33f7ee72d5576ba97781465971c5c839)

* update ckan_pycsw so it works with current stable version of pycsw and add
  option to pull spatial record from the package_converter extension. To use
  add the following to the pycsw config file.
  ```
  [server]
  harvest_type = package_converter
  ```
  [08cc41b](https://github.com/cioos-siooc/ckanext-spatial/commit/08cc41b414c513c2f5ff53dfa556cd8829ad4f31),
  [b404f2e](https://github.com/cioos-siooc/ckanext-spatial/commit/b404f2e822109126609529d7c5d9aad32f69295a),
  [8ac08f9](https://github.com/cioos-siooc/ckanext-spatial/commit/8ac08f95ce79f3b51fc01a5d51a902d32415aaca)


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
