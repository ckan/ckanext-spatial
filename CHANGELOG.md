# Changelog

## [Unreleased](https://github.com/ckan/ckanext-dcat/compare/v2.3.1...HEAD)



## [v2.3.1](https://github.com/ckan/ckanext-spatial/compare/v2.3.0...v2.3.1) - 2025-06-11

* Decouple harvest model to avoid SQLAlchemy metadata errors [#347](https://github.com/ckan/ckanext-spatial/issues/347)
* Remove legacy Pylons code [#346](https://github.com/ckan/ckanext-spatial/pull/346)
* Fix map documentation link [#344](https://github.com/ckan/ckanext-spatial/pull/344)

## [v2.3.0](https://github.com/ckan/ckanext-spatial/compare/v2.2.0...v2.3.0) - 2025-03-06

* Bump Shapely requirement [#343](https://github.com/ckan/ckanext-spatial/pull/343)
* Fix WAF harvester [#342](https://github.com/ckan/ckanext-spatial/pull/342)

## [v2.2.0](https://github.com/ckan/ckanext-spatial/compare/v2.1.1...v2.2.0) - 2024-11-08

* CKAN 2.11 support [#331](https://github.com/ckan/ckanext-spatial/pull/331)
* SQLALchemy v2 support [#338](https://github.com/ckan/ckanext-spatial/pull/338)
* Fix requirements versions issues with Shapely and Numpy [#341](https://github.com/ckan/ckanext-spatial/pull/341)
* Fix catch error on index [#327](https://github.com/ckan/ckanext-spatial/pull/327)
* Traverse IIS folders in WAF harvester [#337](https://github.com/ckan/ckanext-spatial/pull/337)
* Ensure the bbox input is in the correct form [#322](https://github.com/ckan/ckanext-spatial/pull/322)

## [v2.1.1](https://github.com/ckan/ckanext-spatial/compare/v2.1.0...v2.1.1) - 2023-11-10

* Lock pyproj to released 3.6.1 [#321](https://github.com/ckan/ckanext-spatial/pull/321)
* Improve date parser for IIS servers [#320](https://github.com/ckan/ckanext-spatial/pull/320)


## [v2.1.0](https://github.com/ckan/ckanext-spatial/compare/v2.0.0...v2.1.0) - 2023-10-31

* Dropped support for Python 2
* Dropped support for the PostGIS search backend
* Updated the common map JS module to support many different tile providers. The default Stamen Terrain tile will no longer work, and users will need to configure a map tiles provider. Please check the [documentation](https://docs.ckan.org/projects/ckanext-spatial/en/latest/map-widgets/) for full details.
* Upgrade tests to check all envs, including CKAN 2.10 with Python 3.10 [#308](https://github.com/ckan/ckanext-spatial/pull/308)
* TypeError when spatial is missing [#306](https://github.com/ckan/ckanext-spatial/pull/306)
* Fix requirements [#313](https://github.com/ckan/ckanext-spatial/pull/313)
* Fix detecting Microsoft-IIS server [#316](https://github.com/ckan/ckanext-spatial/pull/316)
* Update install.rst [#318](https://github.com/ckan/ckanext-spatial/pull/318)
* Change str validator to unicode_safe [#312](https://github.com/ckan/ckanext-spatial/pull/312)
* Use csw2 from owslib [#311](https://github.com/ckan/ckanext-spatial/pull/311)

## [v2.0.0](https://github.com/ckan/ckanext-spatial/compare/v1.1.0...v2.0.0) - 2023-01-26

> [!NOTE]  
> ckanext-spaital v2.0.0 only supports CKAN >= 2.9. For older versions use the 1.x versions


* Remove PostGIS requirement. Still available if using `ckan.spatial.use_postgis=true`, but will be dropped in the future
* Updated and simplified bbox-based and spatial field based searches, cleaning up and consolidating code, extending test coverage
* Pre-built and customized [Docker images](https://github.com/ckan/ckan-solr) (`*-spatial`) including all necessary changes to enable the spatial search
* New dataset search widget, easier to integrate with custom themes
* Allow to customize the actual Solr spatial query
* Updated [docs](https://docs.ckan.org/projects/ckanext-spatial/en/latest/)! 
* [Document](https://docs.ckan.org/projects/ckanext-spatial/en/latest/spatial-search.html#custom-indexing-logic) and add tests for custom indexing support and multiple geometries per dataset
* Refactor `IPackageController` hooks


## [v1.1.0](https://github.com/ckan/ckanext-spatial/compare/v1.0.0...v1.1.0) - 2022-12-20

* Update for PY3 Encoding (waf harvester) [#252](https://github.com/ckan/ckanext-spatial/pull/252)
* Drop deprecated `package_extras` usage [#273](https://github.com/ckan/ckanext-spatial/pull/273)
* Make `_params_for_solr_search` extend `fq_list` [#236](https://github.com/ckan/ckanext-spatial/pull/236)
* Update shapely usage to avoid deprecation [#276](https://github.com/ckan/ckanext-spatial/pull/276)
* `guess_resource_format` may use protocol and function to better guess t… [#268](https://github.com/ckan/ckanext-spatial/pull/268)
* Make `ckanext.spatial.harvest.validate_wms` working again #265 [#267](https://github.com/ckan/ckanext-spatial/pull/267)
* Lineage support [#266](https://github.com/ckan/ckanext-spatial/pull/266)
* Apply byte->str conversion to recursive call [#278](https://github.com/ckan/ckanext-spatial/pull/278)
* CKAN 2.10 support [#279](https://github.com/ckan/ckanext-spatial/pull/279)
* Remove coupled resources from solr [#285](https://github.com/ckan/ckanext-spatial/pull/285)
* Add nginx WAF server [#283](https://github.com/ckan/ckanext-spatial/pull/283)
* Pin shapely [#303](https://github.com/ckan/ckanext-spatial/pull/303)
* Fix HTML view of ISO XML [#280](https://github.com/ckan/ckanext-spatial/pull/280)
