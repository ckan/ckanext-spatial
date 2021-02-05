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


@click.group(u"spatial-validation", short_help=u"Validation commands")
def spatial_validation():
    pass


@spatial_validation.command()
@click.argument('pkg', required=False)
def report(pkg):
    return util.report(pkg)


@spatial_validation.command('report-csv')
@click.argument('filepath')
def report_csv(filepath):
    return util.report_csv(filepath)


@spatial_validation.command('file')
@click.argument('filepath')
def validate_file(filepath):
    return util.validate_file(filepath)


@click.group(short_help=u"Performs spatially related operations.")
def spatial():
    pass


@spatial.command()
@click.argument('srid', required=False)
def initdb(srid):
    return util.initdb(srid)


@spatial.command('extents')
def update_extents():
    return util.update_extents()
