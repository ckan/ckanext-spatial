from future import standard_library
standard_library.install_aliases()
from builtins import range
from future.utils import raise_
from builtins import object
import time
from urllib.request import urlopen
import os

from pylons import config
from nose.plugins.skip import SkipTest

from ckan.model import engine_is_sqlite

# copied from ckan/tests/__init__ to save importing it and therefore
# setting up Pylons.
class CkanServerCase(object):
    @staticmethod
    def _system(cmd):
        import subprocess
        (status, output) = subprocess.getstatusoutput(cmd)
        if status:
            raise_(Exception, "Couldn't execute cmd: %s: %s" % (cmd, output))

    @classmethod
    def _paster(cls, cmd, config_path_rel):
        config_path = os.path.join(config['here'], config_path_rel)
        cls._system('paster --plugin ckan %s --config=%s' % (cmd, config_path))

    @staticmethod
    def _start_ckan_server(config_file=None):
        if not config_file:
            config_file = config['__file__']
        config_path = config_file
        import subprocess
        process = subprocess.Popen(['paster', 'serve', config_path])
        return process

    @staticmethod
    def _wait_for_url(url='http://127.0.0.1:5000/', timeout=15):
        for i in range(int(timeout)*100):
            import urllib.request, urllib.error, urllib.parse
            import time
            try:
                response = urllib.request.urlopen(url)
            except urllib.error.URLError:
                time.sleep(0.01)
            else:
                break

    @staticmethod
    def _stop_ckan_server(process): 
        pid = process.pid
        pid = int(pid)
        if os.system("kill -9 %d" % pid):
            raise_(Exception, "Can't kill foreign CKAN instance (pid: %d)." % pid)

class CkanProcess(CkanServerCase):
    @classmethod
    def setup_class(cls):
        if engine_is_sqlite():
            raise SkipTest("Non-memory database needed for this test")

        cls.pid = cls._start_ckan_server()
        ## Don't need to init database, since it is same database as this process uses
        cls._wait_for_url()

    @classmethod
    def teardown_class(cls):
        cls._stop_ckan_server(cls.pid)

