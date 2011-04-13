import sys
import re
from pprint import pprint

from ckan.lib.cli import CkanCommand
from ckanext.spatial.lib import save_extent

class Spatial(CkanCommand):
    '''Performs spatially related operations.

    Usage:
        spatial initdb [srid]
            Creates the necessary tables. You must have PostGIS installed
            and configured in the database.
            You can provide the SRID of the geometry column. Default is 4258.

        spatial extents
            Creates or updates the extent geometry column for packages with
            a bounding box defined in extras
      
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
                    Session.query(PackageExtra).filter(PackageExtra.key == 'bbox-east-long').all()]

        error = False
        for package in packages:
            try:
                save_extent(package)
            except:
                errors = True
 
        if error:
            msg = "There was an error saving the package extent. Have you set up the package_extent table in the DB?"
        else:
            msg = "Done. Extents generated for %i packages" % len(packages)

        print msg

