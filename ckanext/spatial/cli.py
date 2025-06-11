# encoding: utf-8
import click



def get_commands():
    return [
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
    from ckanext.spatial.util import report
    return report(pkg)


@spatial_validation.command('report-csv')
@click.argument('filepath')
def report_csv(filepath):
    """
    Performs validation on all the harvested metadata in the db and
    writes a report in CSV format to the given filepath.
    """
    from ckanext.spatial.util import report_csv
    return report_csv(filepath)


@spatial_validation.command('file')
@click.argument('filepath')
def validate_file(filepath):
    """Performs validation on the given metadata file."""
    from ckanext.spatial.util import validate_file
    return validate_file(filepath)
