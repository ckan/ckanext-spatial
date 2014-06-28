===========
CSW support
===========

The extension provides the support for the CSW_ standard, a specification from
the Open Geospatial Consortium for exposing geospatial catalogues over the web.

This support consists of:

* Ability to import records from CSW servers with the CSW harvester. See
  :doc:`harvesters` for more details.

* Integration with pycsw_ to provide a fully compliant CSW interface for
  harvested records. This integration is described in the following sections.


ckan-pycsw
----------

The spatial extension offers the ``ckan-pycsw`` command, which allows to expose
the spatial datasets harvested from other sources in a CSW interface. This is
powered by pycsw_, which fully implements the OGC CSW specification.

How it works
++++++++++++


The current implementation is based on CKAN and pycsw being loosely integrated
via the CKAN API. pycsw will be generally installed in the same server as CKAN
(although it can also be run on a separate one), and the synchronization
command will be run regularly to keep the records on the pycsw repository up to
date. This is done using the CKAN API to get all the datasets identifiers (more
precisely the ones from datasets that have been harvested) and then deciding
which ones need to be created, updated or deleted on the pycsw repository. For
those that need to be created or updated, the original harvested spatial
document (ie ISO 19139) is requested from CKAN, and it is then imported using
pycsw internal functions::

   Harvested
   datasets
      +
      |
      v
  +--------+                 +---------+
  |        |    CKAN API     |         |
  |  CKAN  | +------------>  |  pycsw  | +------> CSW
  |        |                 |         |
  +--------+                 +---------+


Remember, only datasets that were harvested with the :doc:`harvesters`
can currently be exposed via pycsw.

All necessary tasks are done with the ``ckan-pycsw`` command. To get more
details of its usage, run the following::

    cd /usr/lib/ckan/default/src/ckanext-spatial
    paster ckan-pycsw --help


Setup
+++++

1. Install pycsw. There are several options for this, depending on your
   server setup, check the `pycsw documentation`_.

   .. note:: CKAN integration requires at least pycsw version 1.8.0. Make sure
             to install at least this version.

   The following instructions assume that you have installed CKAN via a
   `package install`_ and should be run as root, but the steps are the same if
   you are setting it up in another location::

    cd /usr/lib/ckan/default/src
    source ../bin/activate

    # From now on the virtualenv should be activated

    git clone https://github.com/geopython/pycsw.git
    cd pycsw
    # Remember to use at least pycsw 1.8.0
    git checkout 1.8.0
    pip install -e .
    python setup.py build
    python setup.py install

2. Create a database for pycsw. In theory you can use the same database that
   CKAN is using, but if you want to keep them separated, use the following
   command to create a new one (we'll use the same default user though)::

    sudo -u postgres createdb -O ckan_default pycsw -E utf-8

   It is strongly recommended that you install PostGIS in the pycsw databaset,
   so its spatial functions are used. See the :ref:`install_postgis`
   section for details.

3. Configure pycsw. An example configuration file is included on the source::

    cp default-sample.cfg default.cfg

   To keep things tidy we will create a symlink to this file on the CKAN
   configuration directory::

    ln -s /usr/lib/ckan/default/src/pycsw/default.cfg /etc/ckan/default/pycsw.cfg

   Open the file with your favourite editor. The main settings you should tweak
   are ``server.home`` and ``repository.database``::

    [server]
    home=/usr/lib/ckan/default/src/pycsw
    ...
    [repository]
    database=postgresql://ckan_default:pass@localhost/pycsw

   The rest of the options are described `here <http://docs.pycsw.org/en/latest/configuration.html>`_.

4. Setup the pycsw table. This is done with the ``ckan-pycsw`` paster command
   (Remember to have the virtualenv activated when running it)::

    cd /usr/lib/ckan/default/src/ckanext-spatial
    paster ckan-pycsw setup -p /etc/ckan/default/pycsw.cfg

   At this point you should be ready to run pycsw with the wsgi script that it
   includes::

    cd /usr/lib/ckan/default/src/pycsw
    python csw.wsgi

   This will run pycsw at http://localhost:8000. Visiting the following URL
   should return you the Capabilities file:

   http://localhost:8000/?service=CSW&version=2.0.2&request=GetCapabilities

5. Load the CKAN datasets into pycsw. Again, we will use the ``ckan-pycsw``
   command for this::

    cd /usr/lib/ckan/default/src/ckanext-spatial
    paster ckan-pycsw load -p /etc/ckan/default/pycsw.cfg

   When the loading is finished, check that results are returned when visiting
   this link:

   http://localhost:8000/?request=GetRecords&service=CSW&version=2.0.2&resultType=results&outputSchema=http://www.isotc211.org/2005/gmd&typeNames=csw:Record&elementSetName=summary

   The ``numberOfRecordsMatched`` should match the number of harvested datasets
   in CKAN (minus import errors). If you run the command again new or udpated
   datasets will be synchronized and deleted datasets from CKAN will be removed
   from pycsw as well.

Setting Service Metadata Keywords
+++++++++++++++++++++++++++++++++

The CSW standard allows for administrators to set CSW service metadata. These
values can be set in the pycsw configuration ``metadata:main`` section.  If you
would like the CSW service metadata keywords to be reflective of the CKAN
tags, run the following convenience command::

    paster ckan-pycsw set_keywords -p /etc/ckan/default/pycsw.cfg

Note that you must have privileges to write to the pycsw configuration file.


Running it on production site
+++++++++++++++++++++++++++++

On a production site you probably want to run the load command regularly to
keep CKAN and pycsw in sync, and serve pycsw with Apache + mod_wsgi like CKAN.

* To run the load command regularly you can set up a cron job. Type ``crontab -e``
  and copy the following lines::

    # m h  dom mon dow   command
    0 *  *   *   *     /usr/lib/ckan/default/bin/paster --plugin=ckanext-spatial ckan-pycsw load -p /etc/ckan/default/pycsw.cfg

  This particular example will run the load command every hour. You can of
  course modify this periodicity, for instance reducing it for huge instances.
  This `Wikipedia page <http://en.wikipedia.org/wiki/Cron#CRON_expression>`_
  has a good overview of the crontab syntax.

* To run pycsw under Apache check the pycsw `installation documentation <http://docs.pycsw.org/en/latest/installation.html#running-on-wsgi>`_
  or follow these quick steps (they assume the paths used in previous steps):

  - Edit ``/etc/apache2/sites-available/ckan_default`` and add the following
    line just before the existing ``WSGIScriptAlias`` directive::

        WSGIScriptAlias /csw /usr/lib/ckan/default/src/pycsw/csw.wsgi

  - Edit the ``/usr/lib/ckan/default/src/pycsw/csw.wsgi`` file and add these two
    lines just after the imports on the top of the file::

      activate_this = os.path.join('/usr/lib/ckan/default/bin/activate_this.py')
      execfile(activate_this, {"__file__":activate_this})

    We need these to activate the virtualenv where we installed pycsw into.

  - Restart Apache::

      service apache2 restart

    pycsw should be now accessible at http://localhost/csw


Legacy plugins and libraries
----------------------------


Old CSW Server
++++++++++++++

.. warning:: **Deprecated:** The old csw plugin has been deprecated, please see `ckan-pycsw`_
    for details on how to integrate with pycsw.

To activate it, add the ``csw_server`` plugin to your ini file.

Only harvested datasets are served by this CSW Server. This is because
the harvested document is the one that is served, not something derived
from the CKAN Dataset object. Datasets that are created in CKAN by methods
other than harvesting are not served.

The currently supported methods with this CSW Server are:
 * GetCapabilities
 * GetRecords
 * GetRecordById

For example you can ask the capabilities of the CSW server installed into CKAN
running on 127.0.0.1:5000 like this::

 curl 'http://127.0.0.1:5000/csw?request=GetCapabilities&service=CSW&version=2.0.2'

And get a list of the records like this::

 curl 'http://127.0.0.1:5000/csw?request=GetRecords&service=CSW&resultType=results&elementSetName=full&version=2.0.2'

The standard CSW response is in XML format.

cswinfo
+++++++

The command-line tool ``cswinfo`` allows to make queries on CSW servers and
returns the info in nicely formatted JSON. This may be more convenient to type
than using, for example, curl.

Currently available queries are:
 * getcapabilities
 * getidentifiers
 * getrecords
 * getrecordbyid

For details, type::

 cswinfo csw -h

There are options for querying by only certain types, keywords and typenames
as well as configuring the ElementSetName.

The equivalent example to the one above for asking the cabailities is::

 $ cswinfo csw getcapabilities http://127.0.0.1:5000/csw

OWSLib is the library used to actually perform the queries.

.. _pycsw: http://pycsw.org 
.. _pycsw documentation: http://docs.pycsw.org/en/latest/installation.html
.. _package install: http://docs.ckan.org/en/latest/install-from-package.html
.. _CSW: http://www.opengeospatial.org/standards/cat

