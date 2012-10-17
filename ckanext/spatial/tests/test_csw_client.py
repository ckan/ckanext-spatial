### black box testing because it's easier... make sure you have
### paster serve running on port 5000 with the cswservice
### plugin enabled...
import unittest
import urllib
from urllib2 import urlopen
from owslib.csw import CatalogueServiceWeb
from owslib.iso import MD_Metadata


service = "http://ogcdev.bgs.ac.uk/geonetwork/srv/en/csw"
service = "http://ec2-46-51-149-132.eu-west-1.compute.amazonaws.com:8080/geonetwork/srv/csw"
service = "http://localhost:5000/csw"
#service = "http://localhost:8080/geonetwork/srv/csw"

GMD = "http://www.isotc211.org/2005/gmd"

class TestInvalid(unittest.TestCase):
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

class TestGetCapabilities(unittest.TestCase):
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

### make sure GetRecords is called first so that we can use identifiers
### we know exist later on in GetRecordById
identifiers = []

class Get_01_Records(unittest.TestCase):
    def test_GetRecords(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords(outputschema=GMD, startposition=1, maxrecords=5)
        nrecords = len(csw.records)
        #print csw.response[:1024]
        assert nrecords == 5, nrecords
        for ident in csw.records:
            identifiers.append(ident)
            assert isinstance(csw.records[ident], MD_Metadata), (ident, csw.records[ident])

    def test_GetRecords_dataset(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords(qtype="dataset", outputschema=GMD, startposition=1, maxrecords=5)
        nrecords = len(csw.records)

    def test_GetRecords_brief(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords(outputschema=GMD, startposition=1, maxrecords=5, esn="brief")
        nrecords = len(csw.records)

    def test_GetRecords_summary(self):
        csw = CatalogueServiceWeb(service)
        csw.getrecords(outputschema=GMD, startposition=1, maxrecords=5, esn="summary")
        nrecords = len(csw.records)
        
class Get_02_RecordById(unittest.TestCase):
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
        
if __name__ == '__main__':
    unittest.main()
