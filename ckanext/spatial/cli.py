# encoding: utf-8
import click
import logging

import ckanext.spatial.util as util


log = logging.getLogger(__name__)

def get_commands():
    return [
        spatial,
        spatial_validation
    ]


@click.group(u"spatial-validation", short_help=u"Spatial formats validation commands")
def spatial_validation():
    pass


@spatial_validation.command()
@click.argument('pkg', required=False)
def report(pkg):
    """
    Performs validation on the harvested metadata, either for all
    packages or the one specified.
    """

    return util.report(pkg)


@spatial_validation.command('report-csv')
@click.argument('filepath')
def report_csv(filepath):
    """
    Performs validation on all the harvested metadata in the db and
    writes a report in CSV format to the given filepath.
    """
    return util.report_csv(filepath)


@spatial_validation.command('file')
@click.argument('filepath')
def validate_file(filepath):
    """Performs validation on the given metadata file."""
    return util.validate_file(filepath)


@click.group(short_help=u"Performs spatially related operations.")
def spatial():
    pass


@spatial.command()
@click.argument('srid', required=False)
def initdb(srid):
    """
    Creates the necessary tables. You must have PostGIS installed
    and configured in the database.
    You can provide the SRID of the geometry column. Default is 4326.
    """
    return util.initdb(srid)


@spatial.command('extents')
def update_extents():
    """
    Creates or updates the extent geometry column for datasets with
    an extent defined in the 'spatial' extra.
    """

    return util.update_extents()
