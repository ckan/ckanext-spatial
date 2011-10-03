import sys
import re
from pprint import pprint
import logging

from ckan.lib.cli import CkanCommand
from ckan.lib.helpers import json
from ckanext.spatial.lib import save_package_extent
log = logging.getLogger(__name__)

class Spatial(CkanCommand):
    '''Performs spatially related operations.

    Usage:
        spatial initdb [srid]
            Creates the necessary tables. You must have PostGIS installed
            and configured in the database.
            You can provide the SRID of the geometry column. Default is 4326.

        spatial extents
            Creates or updates the extent geometry column for datasets with
            an extent defined in the 'spatial' extra.
      
    The commands should be run from the ckanext-spatial directory and expect
    a development.ini file to be present. Most of the time you will
    specify the config explicitly though::

        paster extents update --config=../ckan/development.ini

    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2 
    min_args = 0

    def command(self):
        self._load_config()
        print ''

        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'initdb':
            self.initdb()    
        elif cmd == 'extents':
            self.update_extents()
        else:
            print 'Command %s not recognized' % cmd

    def initdb(self):
        if len(self.args) >= 2:
            srid = unicode(self.args[1])
        else:
            srid = None

        from ckanext.spatial.model import setup as db_setup
        
        db_setup(srid)

        print 'DB tables created'

    def update_extents(self):
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
            except ValueError,e:
                errors.append(u'Package %s - Error decoding JSON object: %s' % (package.id,str(e)))
            except TypeError,e:
                errors.append(u'Package %s - Error decoding JSON object: %s' % (package.id,str(e)))

            save_package_extent(package.id,geometry)
        

        Session.commit()
        
        if errors:
            msg = 'Errors were found:\n%s' % '\n'.join(errors)
            print msg

        msg = "Done. Extents generated for %i out of %i packages" % (count,len(packages))

        print msg

