import os
from mock import call, patch, Mock

from nose.tools import assert_raises

from ckanext.spatial.harvesters.gemini import GeminiWafHarvester, GeminiHarvester


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


@patch('ckan.model.Session.query')
def test_gen_new_name(mock_ckan_session_query):
    class MockSessionQuery:
        def __init__(self, name):
            self.name = name
            self.first_query = True

        def filter(self, *arg):
            mock_return = Mock()
            if self.first_query:
                self.first_query = False

                if self.name:
                    mock_pkg_query = Mock()
                    mock_pkg_query.name = self.name
                else:
                    mock_pkg_query = None
                mock_return.order_by.return_value.first.return_value = mock_pkg_query
                return mock_return
            else:
                mock_return = Mock()
                mock_return.first.return_value = None
                return mock_return

    harvester = GeminiHarvester()

    mock_ckan_session_query.return_value = MockSessionQuery(None)
    assert harvester.gen_new_name('Some test') == 'some-test'

    mock_ckan_session_query.return_value = MockSessionQuery('some-test')
    assert harvester.gen_new_name('Some test') == 'some-test1'

    mock_ckan_session_query.return_value = MockSessionQuery('some-test100')
    assert harvester.gen_new_name('Some test') == 'some-test101'
