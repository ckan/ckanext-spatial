==================
Spatial Harvesters
==================

Overview and Configuration
--------------------------

The spatial extension provides some harvesters for importing ISO19139-based
metadata into CKAN, as well as providing a base class for writing new ones.
The harvesters use the interface provided by ckanext-harvest_, so you will need
to install and set it up first.

Once ckanext-harvest is installed, you can add the following plugins to your
ini file to enable the different harvesters (If you are upgrading from a
previous version to CKAN 2.0 see legacy_harvesters_):

* ``csw_harvester`` - CSW server
* ``waf_harvester`` - WAF (Web Accessible Folder): An online accessible index
  page with links to metadata documents
* ``doc_harvester`` - A single online accessible metadata document.

Have a look at the `ckanext-harvest documentation`_ if you want to have an
overview of how the CKAN harvesters work, but basically there are three
separate stages:

* gather_stage - Aggregates all the remote identifiers for a particular source
  (eg identifiers for a CSW server, files for a WAF).
* fetch_stage  - Fetches all the remote documents and stores them on the
  database.
* import_stage - Performs all the processing for transforming the remote
  content into a CKAN dataset: validates the document, parses it, converts it
  to a CKAN dataset dict and saves it in the database.

The extension provides different XSD and schematron based validators. You can
specify which validators to use for the remote documents with the following
configuration option::

    ckan.spatial.validator.profiles = iso19193eden

By default, the import stage will stop if the validation of the harvested
document fails. This can be modified setting the
``ckanext.spatial.harvest.continue_on_validation_errors`` to True. The setting
can also be applied at the source level setting to True the
``continue_on_validation_errors`` key on the source configuration object.

By default the harvesting actions (eg creating or updating datasets) will be
performed by the internal site admin user.  This is the recommended setting,
but if necessary, it can be overridden with the
``ckanext.spatial.harvest.user_name`` config option, eg to support the old
hardcoded 'harvest' user::

    ckanext.spatial.harvest.user_name = harvest

Customizing the harvesters
--------------------------

The default harvesters provided in this extension can be overriden from
extensions to customize to your needs. You can either extend ``CswHarvester``,
``WAFfHarverster`` or the main ``SpatialHarvester`` class. There are some
extension points that can be safely overriden from your extension. Probably the
most useful is ``get_package_dict``, which allows to tweak the dataset fields
before creating or updating them. ``transform_to_iso`` allows to hook into
transformation mechanisms to transform other formats into ISO1939, the only one
directly supported byt he spatial harvesters. Finally, the whole
``import_stage`` can be overriden if the default logic does not suit your
needs.

Check the source code of ``ckanext/spatial/harvesters/base.py`` for more
details on these functions.

The `ckanext-geodatagov`_ extension contains live examples on how to extend
the default spatial harvesters and create new ones for other spatial services
like ArcGIS REST APIs.


Harvest Metadata API
--------------------

This plugin allows to access the actual harvested document via API requests.
It is enabled with the following plugin::

    ckan.plugins = spatial_harvest_metadata_api

(It was previously known as ``inspire_api``)

To view the harvest objects (containing the harvested metadata) in the web
interface, these controller locations are added:

* raw XML document: /harvest/object/{id}
* HTML representation: /harvest/object/{id}/html

.. note:: The old URLs are now deprecated and redirect to the previously
          mentioned:

          * /api/2/rest/harvestobject/<id>/xml
          * /api/2/rest/harvestobject/<id>/html


For those harvest objects that have an original document (which was transformed
to ISO), this can be accessed via:

* raw XML document: /harvest/object/{id}/original
* HTML representation: /harvest/object/{id}/html/original

The HTML representation is created via an XSLT transformation. The extension
provides an XSLT file that should work on ISO 19139 based documents, but if you
want to use your own on your extension, you can override it using the following
configuration options::

    ckanext.spatial.harvest.xslt_html_content = ckanext.myext:templates/xslt/custom.xslt
    ckanext.spatial.harvest.xslt_html_content_original = ckanext.myext:templates/xslt/custom2.xslt

If your project does not transform different metadata types you can ignore the
second option.

.. _legacy_harvesters:

Legacy harvesters
-----------------

Prior to CKAN 2.0, the spatial harvesters available on this extension were
based on the GEMINI2 format, an ISO19139 profile used by the UK Location
Programme, and the logic for creating or updating datasets and the resulting
fields were somehow adapted to the needs for this particular project. The
harvesters were still generic enough and should work fine with other ISO19139
based sources, but extra care has been put to make the new harvesters more
generic and robust, so these ones should only be used on existing instances:

* ``gemini_csw_harvester``
* ``gemini_waf_harvester``
* ``gemini_doc_harvester``

If you are using these harvesters please consider upgrading to the new
versions described on the previous section.


.. todo:: Validation library details


.. _ckanext-harvest: https://github.com/okfn/ckanext-harvest
.. _ckanext-harvest documentation: https://github.com/okfn/ckanext-harvest#the-harvesting-interface
.. _ckanext-geodatagov: https://github.com/okfn/ckanext-geodatagov/blob/master/ckanext/geodatagov/harvesters/
