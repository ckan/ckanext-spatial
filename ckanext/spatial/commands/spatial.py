from __future__ import print_function
import sys

import logging
from ckan.lib.cli import CkanCommand

import ckanext.spatial.util as util


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
        print('')

        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'initdb':
            self.initdb()
        elif cmd == 'extents':
            self.update_extents()
        else:
            print('Command %s not recognized' % cmd)

    def initdb(self):
        if len(self.args) >= 2:
            srid = self.args[1]
        else:
            srid = None
        return util.initdb(srid)

    def update_extents(self):
        return util.update_extents()
