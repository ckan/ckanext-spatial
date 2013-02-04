from nose.tools import assert_equal

from ckanext.spatial.lib.coupled_resource import extract_guid, extract_gemini_harvest_source_reference

GOOD_CSW_RECORD = 'http://ogcdev.bgs.ac.uk/geonetwork/srv/en/csw?SERVICE=CSW&amp;REQUEST=GetRecordById&amp;ID=9df8df52-d788-37a8-e044-0003ba9b0d98&amp;elementSetName=full&amp;OutputSchema=http://www.isotc211.org/2005/gmd'
GOOD_CSW_RECORD_ID = '9df8df52-d788-37a8-e044-0003ba9b0d98'
BAD_CSW_RECORD = 'http://www.geostore.com/OGC/OGCInterface?INTERFACE=ENVIRONMENT&UID=def&PASSWORD=abc&LC=ffe0000000&'
WAF_ITEM = 'http://www.ordnancesurvey.co.uk/oswebsite/xml/products/Topo.xml'
BAD_COUPLE = 'CEH:EIDC:#1279200030617' # would be ok for INSPIRE, but not Gemini

def test_extract_guid__ok():
    assert_equal(extract_guid(GOOD_CSW_RECORD), GOOD_CSW_RECORD_ID)
    assert_equal(extract_guid(GOOD_CSW_RECORD.lower()), GOOD_CSW_RECORD_ID)

def test_extract_guid__bad():
    assert_equal(extract_guid(BAD_CSW_RECORD), None)
    assert_equal(extract_guid(''), None)
    assert_equal(extract_guid(' '), None)

def test_extract_gemini_harvest_source_reference():
    assert_equal(extract_gemini_harvest_source_reference(WAF_ITEM),
                 WAF_ITEM)
    assert_equal(extract_gemini_harvest_source_reference(GOOD_CSW_RECORD),
                 GOOD_CSW_RECORD_ID)
    assert_equal(extract_guid(BAD_COUPLE),
                 None)
