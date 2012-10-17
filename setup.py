from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(
	name='ckanext-spatial',
	version=version,
	description="Geo-related plugins for CKAN",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Open Knowledge Foundation',
	author_email='info@okfn.org',
	url='http://okfn.org',
	license='AGPL',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.spatial'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [console_scripts]
    cswinfo = ckanext.spatial.commands.cswinfo:cswinfo

    [ckan.plugins]
    spatial_metadata=ckanext.spatial.plugin:SpatialMetadata
    spatial_query=ckanext.spatial.plugin:SpatialQuery
    spatial_query_widget=ckanext.spatial.plugin:SpatialQueryWidget
    dataset_extent_map=ckanext.spatial.plugin:DatasetExtentMap
    wms_preview=ckanext.spatial.nongeos_plugin:WMSPreview
    cswserver=ckanext.spatial.plugin:CatalogueServiceWeb

    [paste.paster_command]
    spatial=ckanext.spatial.commands.spatial:Spatial
	""",
)
