# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys

import six

from pkg_resources import resource_stream
import logging
from ckan.lib.helpers import json
from lxml import etree
from pprint import pprint

from ckan import model
from ckan.model.package_extra import PackageExtra

try:
    from ckanext.spatial.lib import save_package_extent
    from ckanext.spatial.lib.reports import validation_report
    from ckanext.spatial.harvesters import SpatialHarvester
    from ckanext.spatial.model import ISODocument
except ImportError:
    # ckanext-harvest not loaded
    pass

from ckantoolkit import config


log = logging.getLogger(__name__)


def report(pkg=None):

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


def get_xslt(original=False):
    if original:
        config_option = \
            'ckanext.spatial.harvest.xslt_html_content_original'
    else:
        config_option = 'ckanext.spatial.harvest.xslt_html_content'

    xslt_package = None
    xslt_path = None
    xslt = config.get(config_option, None)
    if xslt:
        if ':' in xslt:
            xslt = xslt.split(':')
            xslt_package = xslt[0]
            xslt_path = xslt[1]
        else:
            log.error(
                'XSLT should be defined in the form <package>:<path>'
                ', eg ckanext.myext:templates/my.xslt')

    return xslt_package, xslt_path


def get_harvest_object_original_content(id):
    from ckanext.harvest.model import HarvestObject, HarvestObjectExtra

    extra = model.Session.query(
        HarvestObjectExtra
    ).join(HarvestObject).filter(HarvestObject.id == id).filter(
        HarvestObjectExtra.key == 'original_document'
    ).first()

    if extra:
        return extra.value
    else:
        return None


def get_harvest_object_content(id):
    from ckanext.harvest.model import HarvestObject
    obj = model.Session.query(HarvestObject).filter(HarvestObject.id == id).first()
    if obj:
        return obj.content
    else:
        return None


def transform_to_html(content, xslt_package=None, xslt_path=None):

    xslt_package = xslt_package or __name__
    xslt_path = xslt_path or \
        'templates/ckanext/spatial/gemini2-html-stylesheet.xsl'

    # optimise -- read transform only once and compile rather
    # than at each request
    with resource_stream(xslt_package, xslt_path) as style:
        style_xml = etree.parse(style)
        transformer = etree.XSLT(style_xml)

    xml = etree.parse(six.StringIO(content and six.text_type(content)))
    html = transformer(xml)

    result = etree.tostring(html, pretty_print=True)

    return result


def _get_package_extras(pkg_id):
    """Returns a list of package extras by its ID

    Args:
        pkg_id (str): an ID of package

    Returns:
        List[PackageExtra]: a list of package extras
    """
    return model.meta.Session.query(PackageExtra) \
        .filter_by(package_id=pkg_id) \
        .all()
