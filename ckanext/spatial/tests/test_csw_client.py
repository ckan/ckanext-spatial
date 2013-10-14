import time
import urllib
from urllib2 import urlopen
import os

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo
from owslib.iso import MD_Metadata
from pylons import config
from nose.plugins.skip import SkipTest

#from ckan.tests import CkanServerCase
from ckan.model import engine_is_sqlite

service = "http://ogcdev.bgs.ac.uk/geonetwork/srv/en/csw"
service = "http://ec2-46-51-149-132.eu-west-1.compute.amazonaws.com:8080/geonetwork/srv/csw"
service = "http://localhost:5000/csw"
#service = "http://localhost:8080/geonetwork/srv/csw"

GMD = "http://www.isotc211.org/2005/gmd"

### make sure GetRecords is called first so that we can use identifiers
### we know exist later on in GetRecordById
identifiers = []

# copied from ckan/tests/__init__ to save importing it and therefore
# setting up Pylons.
class CkanServerCase:
    @staticmethod
    def _system(cmd):
        import commands
        (status, output) = commands.getstatusoutput(cmd)
        if status:
            raise Exception, "Couldn't execute cmd: %s: %s" % (cmd, output)

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
            import urllib2
            import time
            try:
                response = urllib2.urlopen(url)
            except urllib2.URLError:
                time.sleep(0.01)
            else:
                break

    @staticmethod
    def _stop_ckan_server(process): 
        pid = process.pid
        pid = int(pid)
        if os.system("kill -9 %d" % pid):
            raise Exception, "Can't kill foreign CKAN instance (pid: %d)." % pid

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

class TestCswClient(CkanProcess):

    ## Invalid requests ##
    
    def test_invalid(self):
        params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
        f = urlopen(service, params)
        response = f.read()
        f.close()
        assert "MissingParameterValue" in response, response
        assert 'locator="request"' in response, response

    def test_empty(self):
        fp = urlopen(service)
        response = fp.read()
        fp.close()
        assert "MissingParameterValue" in response, response
        assert 'locator="request"' in response, response

    def test_invalid_request(self):
        fp = urlopen(service + "?request=foo")
        response = fp.read()
        fp.close()
        assert "OperationNotSupported" in response, response
        assert 'locator="foo"' in response, response

    def test_invalid_service(self):
        fp = urlopen(service + "?request=GetCapabilities&service=hello")
        response = fp.read()
        fp.close()
        assert "InvalidParameterValue" in response, response
        assert 'locator="service"' in response, response

    ## Test Capabilities ##
        
    def test_good(self):
        fp = urlopen(service + "?request=GetCapabilities&service=CSW")
        caps = fp.read()
        fp.close()
        assert "GetCapabilities" in caps
        assert "GetRecords" in caps
        assert "GetRecordById" in caps
        
    def test_good_post(self):
        csw = CatalogueServiceWeb(service)
        assert csw.identification.title, csw.identification.title
        ops = dict((x.name, x.methods) for x in csw.operations)
        assert "GetCapabilities" in ops
        assert "GetRecords" in ops
        assert "GetRecordById" in ops

    ## Get 01 Records ##


    def test_GetRecords(self):
        # NB: This test fails because no records have been setup...
        raise SkipTest() # therefore skip
        csw = CatalogueServiceWeb(service)
        csw.getrecords2(outputschema=GMD, startposition=1, maxrecords=5)
        nrecords = len(csw.records)
        #print csw.response[:1024]
        assert nrecords == 5, nrecords
        for ident in csw.records:
            identifiers.append(ident)
            assert isinstance(csw.records[ident], MD_Metadata), (ident, csw.records[ident])

    def test_GetRecords_dataset(self):
        csw = CatalogueServiceWeb(service)
        constraints = [PropertyIsEqualTo("dc:type", "dataset")]
        csw.getrecords2(constraints=constraints, outputschema=GMD, startposition=1, maxrecords=5)
        nrecords = len(csw.records)
        # TODO

    def test_GetRecords_brief(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords2(outputschema=GMD, startposition=1, maxrecords=5, esn="brief")
        nrecords = len(csw.records)
        # TODO

    def test_GetRecords_summary(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords2(outputschema=GMD, startposition=1, maxrecords=5, esn="summary")
        nrecords = len(csw.records)
        # TODO

    ## Get 02 RecordById ##

    def test_GetRecordById(self):
        csw = CatalogueServiceWeb(service)
        tofetch = identifiers[:2]
        csw.getrecordbyid(tofetch, outputschema=GMD)
        nrecords = len(csw.records)
        assert nrecords == len(tofetch), nrecords
        for ident in csw.records:
            identifiers.append(ident)
            assert isinstance(csw.records[ident], MD_Metadata), (ident, csw.records[ident])

        csw.getrecordbyid(["nonexistent"], outputschema=GMD)
        nrecords = len(csw.records)
        assert nrecords == 0, nrecords
