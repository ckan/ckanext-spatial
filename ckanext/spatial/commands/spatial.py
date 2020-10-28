import click
import sys

import logging

from ckan.lib.helpers import json
from ckanext.spatial.lib import save_package_extent
log = logging.getLogger(__name__)


def get_commands():
    return [spatial]


@click.group()
def spatial():
    """Performs spatially related operations.
    """
    pass


@spatial.command()
@click.argument(u"srid", required=False)
def initdb(srid):
    from ckanext.spatial.model import setup as db_setup
    
    db_setup(srid)

    print('DB tables created')


@spatial.command()
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
            errors.append(u'Package %s - Error decoding JSON object: %s' % (package.id,str(e)))
        except TypeError as e:
            errors.append(u'Package %s - Error decoding JSON object: %s' % (package.id,str(e)))

        save_package_extent(package.id,geometry)
    
    Session.commit()
    
    if errors:
        msg = 'Errors were found:\n%s' % '\n'.join(errors)
        print(msg)

    msg = "Done. Extents generated for %i out of %i packages" % (count,len(packages))

    print(msg)
