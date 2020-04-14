# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys

import six

import logging
from ckan.lib.helpers import json
from lxml import etree
from pprint import pprint

from ckanext.spatial.lib import save_package_extent


log = logging.getLogger(__name__)


def report(pkg=None):
    from ckan import model
    from ckanext.harvest.model import HarvestObject
    from ckanext.spatial.lib.reports import validation_report

    if pkg:
        package_ref = six.text_type(pkg)
        pkg = model.Package.get(package_ref)
        if not pkg:
            print('Package ref "%s" not recognised' % package_ref)
            sys.exit(1)

    report = validation_report(package_id=pkg.id)
    for row in report.get_rows_html_formatted():
        print()
        for i, col_name in enumerate(report.column_names):
            print('  %s: %s' % (col_name, row[i]))


def validate_file(metadata_filepath):
    from ckanext.spatial.harvesters import SpatialHarvester
    from ckanext.spatial.model import ISODocument

    if not os.path.exists(metadata_filepath):
        print('Filepath %s not found' % metadata_filepath)
        sys.exit(1)
    with open(metadata_filepath, 'rb') as f:
        metadata_xml = f.read()

    validators = SpatialHarvester()._get_validator()
    print('Validators: %r' % validators.profiles)
    try:
        xml_string = metadata_xml.encode("utf-8")
    except UnicodeDecodeError as e:
        print('ERROR: Unicode Error reading file \'%s\': %s' % \
              (metadata_filepath, e))
        sys.exit(1)
        #import pdb; pdb.set_trace()
    xml = etree.fromstring(xml_string)

    # XML validation
    valid, errors = validators.is_valid(xml)

    # CKAN read of values
    if valid:
        try:
            iso_document = ISODocument(xml_string)
            iso_values = iso_document.read_values()
        except Exception as e:
            valid = False
            errors.append(
                'CKAN exception reading values from ISODocument: %s' % e)

    print('***************')
    print('Summary')
    print('***************')
    print('File: \'%s\'' % metadata_filepath)
    print('Valid: %s' % valid)
    if not valid:
        print('Errors:')
        print(pprint(errors))
    print('***************')


def report_csv(csv_filepath):
    from ckanext.spatial.lib.reports import validation_report
    report = validation_report()
    with open(csv_filepath, 'wb') as f:
        f.write(report.get_csv())


def initdb(srid=None):
    if srid:
        srid = six.text_type(srid)

    from ckanext.spatial.model import setup as db_setup

    db_setup(srid)

    print('DB tables created')


def update_extents():
    from ckan.model import PackageExtra, Package, Session
    conn = Session.connection()
    packages = [extra.package \
                for extra in \
                Session.query(PackageExtra).filter(PackageExtra.key == 'spatial').all()]

    errors = []
    count = 0
    for package in packages:
        try:
            value = package.extras['spatial']
            log.debug('Received: %r' % value)
            geometry = json.loads(value)

            count += 1
        except ValueError as e:
            errors.append(u'Package %s - Error decoding JSON object: %s' %
                          (package.id, six.text_type(e)))
        except TypeError as e:
            errors.append(u'Package %s - Error decoding JSON object: %s' %
                          (package.id, six.text_type(e)))

        save_package_extent(package.id, geometry)

    Session.commit()

    if errors:
        msg = 'Errors were found:\n%s' % '\n'.join(errors)
        print(msg)

    msg = "Done. Extents generated for %i out of %i packages" % (count,
                                                                 len(packages))

    print(msg)
