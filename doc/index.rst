.. ckanext-spatial documentation master file, created by
   sphinx-quickstart on Wed Apr 10 17:17:12 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ckanext-spatial's documentation!
===========================================

==============================================
ckanext-spatial - Geo related plugins for CKAN
==============================================

This extension contains plugins that add geospatial capabilities to CKAN.
The following plugins are currently available:

* Spatial model for CKAN datasets and automatic geo-indexing (`spatial_metadata`)
* Spatial Search - Spatial search integration and API call (`spatial_query`).
* Spatial Search Widget - Map widget integrated on the search form (`spatial_query_widget`).
* Dataset Extent Map - Map widget showing a dataset extent (`dataset_extent_map`).
* WMS Preview - a Web Map Service (WMS) previewer (`wms_preview`).
* CSW Server - a basic CSW server - to server metadata from the CKAN instance (`cswserver`)
* GEMINI Harvesters - for importing INSPIRE-style metadata into CKAN (`gemini_csw_harvester`, `gemini_doc_harvester`, `gemini_waf_harvester`)
* Harvest Metadata API - a way for a user to view the harvested metadata XML, either as a raw file or styled to view in a web browser. (`spatial_harvest_metadata_api`)

These libraries:
* CSW Client - a basic client for accessing a CSW server
* Validators - uses XSD / Schematron to validate geographic metadata XML. Used by the GEMINI Harvesters
* Validators for ISO19139/INSPIRE/GEMINI2 metadata. Used by the Validator.

And these command-line tools:
* cswinfo - a command-line tool to help making requests of any CSW server

As of October 2012, ckanext-csw and ckanext-inspire were merged into this extension.

Contents:

.. toctree::
   :maxdepth: 2
    
   spatial-search
   dataset-map


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

