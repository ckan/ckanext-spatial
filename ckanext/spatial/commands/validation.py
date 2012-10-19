import sys
import re
from pprint import pprint
import logging

from lxml import etree

from ckan.lib.cli import CkanCommand

log = logging.getLogger(__name__)

class Validation(CkanCommand):
    '''Validation commands

    Usage:
        validation report [package-name]
            Performs validation on the harvested metadata, either for all
            packages or one specified.

        validation report-csv <filename>.csv
      
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 3
    min_args = 0

    def command(self):
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print self.usage
            sys.exit(1)

        self._load_config()

        cmd = self.args[0]
        if cmd == 'report':
            self.report()
        elif cmd == 'report-csv':
            self.report_csv()
        else:
            print 'Command %s not recognized' % cmd

    def report(self):
        from ckan import model
        from ckanext.harvest.model import HarvestObject
        from ckanext.spatial.lib.reports import validation_report

        if len(self.args) >= 2:
            package_ref = unicode(self.args[1])
            pkg = model.Package.get(package_ref)
            if not pkg:
                print 'Package ref "%s" not recognised' % package_ref
                sys.exit(1)
        else:
            pkg = None

        report = validation_report(package_id=pkg.id)
        for row in report.get_rows_html_formatted():
            print
            for i, col_name in enumerate(report.column_names):
                print '  %s: %s' % (col_name, row[i])

    def report_csv(self):
        from ckanext.spatial.lib.reports import validation_report
        if len(self.args) != 2:
            print 'Wrong number of arguments'
            sys.exit(1)
        csv_filepath = self.args[1]
        report = validation_report()
        with open(csv_filepath, 'wb') as f:
            f.write(report.get_csv())
