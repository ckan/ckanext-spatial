======================
Installation and Setup
======================

Check the Troubleshooting_ section if you get errors at any stage.

.. warning:: If you are looking for the geospatial preview plugins to render (eg GeoJSON
          or WMS services), these are now located in ckanext-geoview_. They have a much simpler
          installation, so you can skip all the following steps if you just want the previews.

All commands assume an existing CKAN database named ``ckan_default``.


Install the extension
---------------------

.. note:: The package names and paths shown are the defaults on Ubuntu installs.
          Adjust the package names and the paths if you are using a different platform.

#. Install some packages needed by the extension dependencies::

     sudo apt-get install python-dev libxml2-dev libxslt1-dev libgeos-c1

#. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

#. Install the ckanext-spatial Python package into your virtual environment::

     pip install -e "git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial"

#. Install the rest of Python modules required by the extension::

     pip install -r /usr/lib/ckan/default/src/ckanext-spatial/requirements.txt

#. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

To use the :doc:`harvesters`, you will need to install and configure the
harvester extension: `ckanext-harvest`_. Follow the install instructions on
its documentation for details on how to set it up.


Configuration
-------------


Add the following plugins to the ``ckan.plugins`` directive in the
CKAN ini file::

    ckan.plugins = spatial_metadata spatial_query


Troubleshooting
---------------

Here are some common problems you may find when installing or using the
extension:

When upgrading the extension to a newer version
+++++++++++++++++++++++++++++++++++++++++++++++

ckan.plugins.core.PluginNotFoundException: geojson_view
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 149, in load
    service = _get_service(plugin)
  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 256, in _get_service
    raise PluginNotFoundException(plugin_name)
    ckan.plugins.core.PluginNotFoundException: geojson_view

Your CKAN instance is using the ``geojson_view`` (or ``geojson_preview``) plugin. This plugin has been
moved from ckanext-spatial to ckanext-geoview_. Please install ckanext-geoview following the instructions on the
README.

TemplateNotFound: Template dataviewer/geojson.html cannot be found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    File '/home/pyenvs/spatial/src/ckan/ckan/lib/base.py', line 129 in render_template
      template_path, template_type = render_.template_info(template_name)
    File '/home/pyenvs/spatial/src/ckan/ckan/lib/render.py', line 51 in template_info
      raise TemplateNotFound('Template %s cannot be found' % template_name)
    TemplateNotFound: Template dataviewer/geojson.html cannot be found

See the issue above for details. Install ckanext-geoview_ and additionally run the following on the
ckanext-spatial directory with your virtualenv activated::

     python setup.py develop


ImportError: No module named nongeos_plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  File "/home/pyenvs/spatial/src/ckan/ckan/plugins/core.py", line 255, in _get_service
    return plugin.load()(name=plugin_name)
  File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pkg_resources.py", line 2147, in load
    ['__name__'])
  ImportError: No module named nongeos_plugin

See the issue above for details. Install ckanext-geoview_ and additionally run the following on the
ckanext-spatial directory with your virtualenv activated::

     python setup.py develop


Plugin class 'GeoJSONPreview' does not implement an interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

 File "/home/pyenvs/spatial/src/ckanext-spatial/ckanext/spatial/nongeos_plugin.py", line 175, in <module>
   class GeoJSONPreview(GeoJSONView):
 File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pyutilib/component/core/core.py", line 732, in __new__
   return PluginMeta.__new__(cls, name, bases, d)
 File "/home/pyenvs/spatial/local/lib/python2.7/site-packages/pyutilib/component/core/core.py", line 659, in __new__
   raise PluginError("Plugin class %r does not implement an interface, and it has already been defined in environment '%r'." % (str(name), PluginGlobals.env().name))
   pyutilib.component.core.core.PluginError: Plugin class 'GeoJSONPreview' does not implement an interface, and it has already been defined in environment ''pca''

You have correctly installed ckanext-geoview_ but the ckanext-spatial source code is outdated, with references
to the view plugins previously part of this extension. Pull the latest version of the code and re-register the
extension. With the virtualenv CKAN is installed on activated, run::

     git pull
     python setup.py develop

When running the spatial harvesters
+++++++++++++++++++++++++++++++++++

::

    File "xmlschema.pxi", line 102, in lxml.etree.XMLSchema.__init__ (src/lxml/lxml.etree.c:154475)
    lxml.etree.XMLSchemaParseError: local list type: A type, derived by list or union, must have the simple ur-type definition as base type, not '{http://www.opengis.net/gml}doubleList'., line 1

The XSD validation used by the spatial harvesters requires libxml2 version 2.9.

With CKAN you would probably have installed an older version from your
distribution. (e.g. with ``sudo apt-get install libxml2-dev``). You need to
find the SO files for the old version::

    $ find /usr -name "libxml2.so"

For example, it may show it here: ``/usr/lib/x86_64-linux-gnu/libxml2.so``.
The directory of the SO file is used as a parameter to the ``configure`` next
on.

Download the libxml2 source::

    $ cd ~
    $ wget ftp://xmlsoft.org/libxml2/libxml2-2.9.0.tar.gz

Unzip it::

    $ tar zxvf libxml2-2.9.0.tar.gz
    $ cd libxml2-2.9.0/

Configure with the SO directory you found before::

    $ ./configure --libdir=/usr/lib/x86_64-linux-gnu

Now make it and install it::

    $ make
    $ sudo make install

Now check the install by running xmllint::

    $ xmllint --version
    xmllint: using libxml version 20900
     compiled with: Threads Tree Output Push Reader Patterns Writer SAXv1 FTP HTTP DTDValid HTML Legacy C14N Catalog XPath XPointer XInclude Iconv ISO8859X Unicode Regexps Automata Expr Schemas Schematron Modules Debug Zlib

.. _ckanext-harvest: https://github.com/okfn/ckanext-harvest
.. _ckanext-geoview: https://github.com/ckan/ckanext-geoview
