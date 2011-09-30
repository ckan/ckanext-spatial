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
    [ckan.plugins]
	# Add plugins here, eg
	wms_preview=ckanext.spatial.plugin:WMSPreview
 	spatial_query=ckanext.spatial.plugin:SpatialQuery
 	dataset_extent_map=ckanext.spatial.plugin:DatasetExtentMap
    [paste.paster_command]
    spatial=ckanext.spatial.commands.spatial:Spatial
	""",
)
