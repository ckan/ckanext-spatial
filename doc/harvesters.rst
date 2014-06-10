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

The extension provides different XSD and schematron based validators, and you
can also write your own (see `Writing custom validators`_). You can
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

When a document has not been updated remotely, the previous harvest object is
replaced by the current one rather than keeping it, to avoid cluttering the
``harvest_object`` table. This means that the ``harvest_object_id`` reference
on the linked dataset needs to be updated, by reindexing it. This will happen
by default, but if you want to turn it off (eg if you are doing separate
reindexing) it can be turn off with the following option::

    ckanext.spatial.harvest.reindex_unchanged = False


Customizing the harvesters
--------------------------

The default harvesters provided in this extension can be extended from
extensions implementing the ``ISpatialHarvester`` interface.

Probably the most useful extension point is ``get_package_dict``, which
allows to tweak the dataset fields before creating or updating it::

    import ckan.plugins as p
    from ckanext.spatial.interfaces import ISpatialHarvester

    class MyPlugin(p.SingletonPlugin):

        p.implements(ISpatialHarvester, inherit=True)

        def get_package_dict(self, context, data_dict):

            # Check the reference below to see all that's included on data_dict

            package_dict = data_dict['package_dict']
            iso_values = data_dict['iso_values']

            package_dict['extras'].append(
                {'key': 'topic-category', 'value': iso_values.get('topic-category')}
            )

            package_dict['extras'].append(
                {'key': 'my-custom-extra', 'value': 'my-custom-value'}
            )

            return package_dict

``get_validators`` allows to register custom validation classes that can be
applied to the harvested documents. Check the `Writing custom validators`_
section to know more about how to write your custom validators::

    import ckan.plugins as p
    from ckanext.spatial.interfaces import ISpatialHarvester
    from ckanext.spatial.validation.validation import BaseValidator

    class MyPlugin(p.SingletonPlugin):

        p.implements(ISpatialHarvester, inherit=True)

        def get_validators(self):
            return [MyValidator]


    class MyValidator(BaseValidator):

        name = 'my-validator'

        title= 'My very own validator'

        @classmethod
        def is_valid(cls, xml):

            return True, []


``transform_to_iso`` allows to hook into transformation mechanisms to
transform other formats into ISO1939, the only one directly supported by
the spatial harvesters.

Here is the full reference for the provided extension points:

.. autoclass:: ckanext.spatial.interfaces.ISpatialHarvester
   :members:

If you need to further customize the default behaviour of the harvesters, you
can either extend ``CswHarvester``, ``WAFfHarverster`` or the main
``SpatialHarvester`` class., for instance to override the whole
``import_stage`` if the default logic does not suit your
needs.

The `ckanext-geodatagov`_ extension contains live examples on how to extend
the default spatial harvesters and create new ones for other spatial services
like ArcGIS REST APIs.

Writing custom validators
-------------------------


Validator classes extend the ``BaseValidator`` class:

.. autoclass:: ckanext.spatial.validation.validation.BaseValidator
   :members:

Helper classes are provided for XSD and schematron based validation, and
completely custom logic can be also implemented. Here are some examples of
the most common types:

* XSD based validators::

    class ISO19139NGDCSchema(XsdValidator):
        '''
        XSD based validation for ISO 19139 documents.

        Uses XSD schema from the NOAA National Geophysical Data Center:

        http://ngdc.noaa.gov/metadata/published/xsd/

        '''
        name = 'iso19139ngdc'
        title = 'ISO19139 XSD Schema (NGDC)'

        @classmethod
        def is_valid(cls, xml):
            xsd_path = 'xml/iso19139ngdc'

            xsd_filepath = os.path.join(os.path.dirname(__file__),
                                            xsd_path, 'schema.xsd')
            return cls._is_valid(xml, xsd_filepath, 'NGDC Schema (schema.xsd)')



* Schematron validators::

    class Gemini2Schematron(SchematronValidator):
        name = 'gemini2'
        title = 'GEMINI 2.1 Schematron 1.2'

        @classmethod
        def get_schematrons(cls):
            with resource_stream("ckanext.spatial",
                                 "validation/xml/gemini2/gemini2-schematron-20110906-v1.2.sch") as schema:
                return [cls.schematron(schema)]


* Custom validators::

    class MinimalFGDCValidator(BaseValidator):

        name = 'fgdc_minimal'
        title = 'FGDC Minimal Validation'

        _elements = [
            ('Identification Citation Title', '/metadata/idinfo/citation/citeinfo/title'),
            ('Identification Citation Originator', '/metadata/idinfo/citation/citeinfo/origin'),
            ('Identification Citation Publication Date', '/metadata/idinfo/citation/citeinfo/pubdate'),
            ('Identification Description Abstract', '/metadata/idinfo/descript/abstract'),
            ('Identification Spatial Domain West Bounding Coordinate', '/metadata/idinfo/spdom/bounding/westbc'),
            ('Identification Spatial Domain East Bounding Coordinate', '/metadata/idinfo/spdom/bounding/eastbc'),
            ('Identification Spatial Domain North Bounding Coordinate', '/metadata/idinfo/spdom/bounding/northbc'),
            ('Identification Spatial Domain South Bounding Coordinate', '/metadata/idinfo/spdom/bounding/southbc'),
            ('Metadata Reference Information Contact Address Type', '/metadata/metainfo/metc/cntinfo/cntaddr/addrtype'),
            ('Metadata Reference Information Contact Address State', '/metadata/metainfo/metc/cntinfo/cntaddr/state'),
            ]

        @classmethod
        def is_valid(cls, xml):

            errors = []

            for title, xpath in cls._elements:
                element = xml.xpath(xpath)
                if len(element) == 0 or not element[0].text:
                    errors.append(('Element not found: {0}'.format(title), None))
            if len(errors):
                return False, errors

            return True, []


The `validation.py`_ file included in the ckanext-spatial extension contains
more examples of the different types.

Remember that after registering your own validators you must specify them on
the following configuration option::

    ckan.spatial.validator.profiles = iso19193eden,my-validator


.. _validation.py: https://github.com/ckan/ckanext-spatial/blob/master/ckanext/spatial/validation/validation.py

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
