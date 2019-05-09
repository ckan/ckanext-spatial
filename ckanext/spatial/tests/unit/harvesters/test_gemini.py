import os
from mock import call, patch, Mock

from nose.tools import assert_raises

from ckanext.spatial.harvesters.gemini import GeminiWafHarvester


@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester._save_gather_error')
def test_gemini_waf_extract_urls_report_link_errors(mock_save_gather_error):
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
        '..',
        '..',
        'data',
        'sample-waf.html')
    ) as f:
        gemini = GeminiWafHarvester()
        gemini.harvest_job = Mock()
        urls = gemini._extract_urls(f.read(), 'http://test.co.uk/xml')

        assert urls == [
            'http://test.co.uk/xml/AddressBase.xml',
            'http://test.co.uk/xml/SourcePoint.xml',
            'http://test.co.uk/xml/RealImagery.xml'
        ] 
        assert mock_save_gather_error.call_args_list == [
            call('Ignoring link in WAF because it has "/": /xml/BoundaryLine.xml', gemini.harvest_job),
            call('Ignoring link in WAF because it has "/": /xml/SmallScale.xml', gemini.harvest_job)
        ]
