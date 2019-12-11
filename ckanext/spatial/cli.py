# encoding: utf-8
import click
import logging
from ckan.cli import click_config_option
from ckan.cli.cli import CkanCommand

import ckanext.spatial.util as util


log = logging.getLogger(__name__)


@click.group(short_help=u"Validation commands")
@click.help_option(u"-h", u"--help")
@click_config_option
@click.pass_context
def validation(ctx, config, *args, **kwargs):
    ctx.obj = CkanCommand(config)


@validation.command()
@click.argument('pkg', required=False)
def report(pkg):
    return util.report(pkg)


@validation.command('report-csv')
@click.argument('filepath')
def report_csv(filepath):
    return util.report_csv(filepath)


@validation.command('file')
@click.argument('filepath')
def validate_file(filepath):
    return util.validate_file(filepath)


@click.group(short_help=u"Performs spatially related operations.")
@click.help_option(u"-h", u"--help")
@click_config_option
@click.pass_context
def spatial(ctx, config, *args, **kwargs):
    ctx.obj = CkanCommand(config)


@spatial.command()
@click.argument('srid', required=False)
def initdb(srid):
    return util.initdb(srid)


@spatial.command('extents')
def update_extents():
    return util.update_extents()
