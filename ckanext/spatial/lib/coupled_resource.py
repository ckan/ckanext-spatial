import re

guid_matcher = None

def extract_guid(csw_url):
    '''Given a CSW GetRecordByID URL, identify the record\'s ID (GUID).
    Returns the GUID or None if it can\'t find it.'''
    # Example CSW url: http://ogcdev.bgs.ac.uk/geonetwork/srv/en/csw?SERVICE=CSW&amp;REQUEST=GetRecordById&amp;ID=9df8df52-d788-37a8-e044-0003ba9b0d98&amp;elementSetName=full&amp;OutputSchema=http://www.isotc211.org/2005/gmd
    if not guid_matcher:
        global guid_matcher
        guid_matcher = re.compile('id=\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', flags=re.IGNORECASE)
    guid_match = guid_matcher.search(csw_url)
    if guid_match:
        return guid_match.groups()[0]

def extract_gemini_harvest_source_reference(coupled_href):
    '''Given the href in the Coupled Resource (srv:operatesOn xlink:href)
    this function returns the 'harvest_source_reference' identifier for
    the coupled dataset record.

    This follows the Gemini Encoding Guidance 2.1, which differs from
    the INSPIRE guidance:
    
    The value of the XLink attribute, as shown in the INSPIRE technical
    guidance, is the value of the metadata item Unique Resource
    Identifier. However, the guidance for GEMINI metadata is different.
    The value of the  attribute shall be a URL that
    allows access to an unambiguous metadata instance, which may be:
    * an OGC CS-W GetRecordById request
    * an address of a metadata instance in a WAF
    '''
    if not coupled_href.startswith('http'):
        return
    guid = extract_guid(coupled_href)
    return guid or coupled_href

        
