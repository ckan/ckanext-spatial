from __future__ import print_function
import sys

import logging
from ckan.lib.cli import CkanCommand

import ckanext.spatial.util as util


log = logging.getLogger(__name__)

class Validation(CkanCommand):
    '''Validation commands

    Usage:
        validation report [package-name]
            Performs validation on the harvested metadata, either for all
            packages or the one specified.

        validation report-csv <filename>.csv
            Performs validation on all the harvested metadata in the db and
            writes a report in CSV format to the given filepath.

        validation file <filename>.xml
            Performs validation on the given metadata file.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 3
    min_args = 0

    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(self.usage)
            sys.exit(1)

        self._load_config()

        cmd = self.args[0]
        if cmd == 'report':
            self.report()
        elif cmd == 'report-csv':
            self.report_csv()
        elif cmd == 'file':
            self.validate_file()
        else:
            print('Command %s not recognized' % cmd)

    def report(self):

        if len(self.args) >= 2:
            pkg = self.args[1]
        else:
            pkg = None
        return util.report(pkg)

    def validate_file(self):
        if len(self.args) > 2:
            print('Too many parameters %i' % len(self.args))
            sys.exit(1)
        if len(self.args) < 2:
            print('Not enough parameters %i' % len(self.args))
            sys.exit(1)

        return util.validate_file(self.args[1])

    def report_csv(self):
        if len(self.args) != 2:
            print('Wrong number of arguments')
            sys.exit(1)
        return util.report_csv(self.args[1])
