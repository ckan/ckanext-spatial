from setuptools import setup, find_packages
from ckanext.spatial import __version__

version = __version__

setup(
    name="ckanext-spatial",
    version=version,
    description="Geo-related plugins for CKAN",
    long_description="""
This extension contains plugins that add geospatial capabilities to CKAN_,
including:

* Geospatial dataset search powered by Solr, providing a bounding box via
  a UI map widget or the API.
* Harvesters to import geospatial metadata into CKAN from other sources
  in ISO 19139 format and others.
* Commands to support the CSW standard using pycsw_.

**Note**: The view plugins for rendering spatial formats like GeoJSON_ have
been moved to ckanext-geoview_.

Full documentation, including installation instructions, can be found at:

https://docs.ckan.org/projects/ckanext-spatial/en/latest/
""",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="",
    author="Open Knowledge Foundation",
    author_email="info@okfn.org",
    url="http://okfn.org",
    license="AGPL",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    namespace_packages=["ckanext"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    [ckan.plugins]
    spatial_metadata=ckanext.spatial.plugin:SpatialMetadata
    spatial_query=ckanext.spatial.plugin:SpatialQuery
    spatial_harvest_metadata_api=ckanext.spatial.plugin:HarvestMetadataApi

    csw_harvester=ckanext.spatial.harvesters:CSWHarvester
    waf_harvester=ckanext.spatial.harvesters:WAFHarvester
    doc_harvester=ckanext.spatial.harvesters:DocHarvester

    # Legacy harvesters
    gemini_csw_harvester=ckanext.spatial.harvesters.gemini:GeminiCswHarvester
    gemini_doc_harvester=ckanext.spatial.harvesters.gemini:GeminiDocHarvester
    gemini_waf_harvester=ckanext.spatial.harvesters.gemini:GeminiWafHarvester

    [paste.paster_command]
    spatial=ckanext.spatial.commands.spatial:Spatial
    ckan-pycsw=ckanext.spatial.commands.csw:Pycsw
    validation=ckanext.spatial.commands.validation:Validation

    [ckan.test_plugins]
    test_spatial_plugin = ckanext.spatial.tests.test_plugin.plugin:TestSpatialPlugin
""",
)
