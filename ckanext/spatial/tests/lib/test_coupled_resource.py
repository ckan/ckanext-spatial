from nose.tools import assert_equal
from pylons import config
from pprint import pprint

from ckan.logic import get_action
from ckan.lib.create_test_data import CreateTestData
from ckan import model
from ckan.lib.base import json
from ckanext.harvest.model import HarvestSource, HarvestJob, HarvestObject, HarvestCoupledResource

from ckanext.spatial.lib.coupled_resource import extract_guid, extract_gemini_harvest_source_reference, update_coupled_resources


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

ref_prefix = 'http://waf/'

class TestUpdateCoupledResources:
    def setup(self):
        # Create fixtures
        CreateTestData.create_arbitrary([
            {'name': 'serviceA',
             'extras': {'coupled-resource': json.dumps(
                 [{'href': [ref_prefix+'Bref']},
                  {'href': [ref_prefix+'Href']},
                  {'href': [ref_prefix+'Eref']}]),
                        'resource-type': 'service'}},
            {'name': 'serviceF',
             'extras': {'coupled-resource': json.dumps(
                 [{'href': [ref_prefix+'Dref']}]),
                        'resource-type': 'service'}},
            {'name': 'serviceG',
             'extras': {'coupled-resource': json.dumps(
                 [{'href': [ref_prefix+'Gref']}]),
                        'resource-type': 'service'}},
            {'name': 'datasetB',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'datasetC',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'datasetD',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'datasetE',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'datasetG',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'datasetH',
             'extras': {'resource-type': 'dataset'}},
            {'name': 'serviceD',
             'extras': {'coupled-resource': json.dumps(
                 [{'href': [ref_prefix+'Dref']}]),
                        'resource-type': 'service'}},
             ])
        self._create_user()
        self._create_publisher()
        self.source, self.job = self._create_source_and_job()
        self._create_harvest_object('datasetB', ref='Bref')
        self._create_harvest_object('datasetC', ref='Cref')
        self._create_harvest_object('datasetD', ref='Dref')
        self._create_harvest_object('datasetE', ref='Eref')

        # Create a partially-filled coupling table
        self._create_coupled_resource('serviceA', 'Bref', 'datasetB')
        self._create_coupled_resource('serviceA', 'Cref', 'datasetC')
        self._create_coupled_resource(None,       'Dref', 'datasetD')
        self._create_coupled_resource('serviceA', 'Eref', None)
        self._create_coupled_resource('serviceF', 'Dref', 'datasetD')

        model.Session.commit()
        model.Session.remove()

        self.couples_before = self._get_coupled_resources()
        pprint(self.couples_before)
        assert_equal(len(self.couples_before), 5)

    def teardown(self):
        model.repo.rebuild_db()

    def test_01_reharvest_existing_dataset(self):
        package = model.Package.by_name(u'datasetB')
        update_coupled_resources(package, ref_prefix+'Bref')
        assert_equal(self._get_coupled_resources(), self.couples_before)
        
    def test_02_reharvest_existing_service(self):
        package = model.Package.by_name(u'serviceF')
        update_coupled_resources(package, None)
        assert_equal(self._get_coupled_resources(), self.couples_before)

    def test_03_harvest_dataset_to_match_existing_service(self):
        package = model.Package.by_name(u'datasetE')
        update_coupled_resources(package, ref_prefix+'Eref')
        assert_equal(self._get_coupled_resources(),
                     change_line(self.couples_before,
                                 (u'serviceA', u'Eref', None),
                                 (u'serviceA', u'Eref', u'datasetE')))

    def test_04_harvest_service_to_match_existing_dataset(self):
        package = model.Package.by_name(u'serviceD')
        update_coupled_resources(package, None)
        assert_equal(self._get_coupled_resources(),
                     change_line(self.couples_before,
                                 (None, u'Dref', u'datasetD'),
                                 (u'serviceD', u'Dref', u'datasetD')))

    def test_05_harvest_dataset_not_matching_a_service(self):
        package = model.Package.by_name(u'datasetG')
        update_coupled_resources(package, ref_prefix+'Gref')
        assert_equal(self._get_coupled_resources(),
                     add_line(self.couples_before,
                              (None, u'Gref', u'datasetG')))

    def test_06_harvest_service_not_matching_a_dataset(self):
        package = model.Package.by_name(u'serviceG')
        update_coupled_resources(package, None)
        assert_equal(self._get_coupled_resources(),
                     add_line(self.couples_before,
                              (u'serviceG', u'Gref', None)))

    def test_07_reharvest_existing_dataset_but_with_changed_ref(self):
        # This may occur only in a WAF. If a dataset is reharvested from
        # a different WAF URL then the old WAF URL (and therefore ref)
        # for that dataset becomes invalid.
        # (A CSW may change a dataset's GUID, but it becomes a different
        # datasets entirely if that happens)
        package = model.Package.by_name(u'datasetB')
        update_coupled_resources(package, ref_prefix+'Jref')
        expected_couples = change_line(self.couples_before,
                                       ('serviceA', u'Bref', 'datasetB'),
                                       ('serviceA', u'Bref', None))
        expected_couples = add_line(expected_couples,
                                    (None, u'Jref', 'datasetB'))
        assert_equal(self._get_coupled_resources(), expected_couples)

    def test_08_reharvest_existing_service_to_delete_and_add_couples(self):
        package = model.Package.by_name(u'serviceA')
        update_coupled_resources(package, None)
        expected_couples = change_line(self.couples_before,
                                       ('serviceA', u'Cref', 'datasetC'),
                                       (None, 'Cref', 'datasetC'))
        expected_couples = add_line(expected_couples,
                                    (u'serviceA', u'Href', None))
        print 'EXPECTED_COUPLES'; pprint(expected_couples)
        print 'RESULT_COUPLES'; pprint(self._get_coupled_resources())
        assert_equal(self._get_coupled_resources(),
                     expected_couples)
        

    def _get_coupled_resources(self):
        return [(couple.service_record.name if couple.service_record else None,
                 couple.harvest_source_reference.replace(ref_prefix, ''),
                 couple.dataset_record.name if couple.dataset_record else None)\
                for couple in model.Session.query(HarvestCoupledResource)]

    def _create_coupled_resource(self, service_name, ref, dataset_name):
        service = model.Package.by_name(unicode(service_name or ''))
        dataset = model.Package.by_name(unicode(dataset_name or ''))
        if service_name: assert service
        if dataset_name: assert dataset
        model.Session.add(
            HarvestCoupledResource(service_record=service,
                                   harvest_source_reference=ref_prefix+ref,
                                   dataset_record=dataset)
            )

    def _create_harvest_object(self, package_name, ref):
        package = model.Package.by_name(unicode(package_name))
        model.Session.add(
                HarvestObject(guid='not important',
                              current=True, source=self.source, job=self.job,
                              harvest_source_reference=ref_prefix+ref,
                              package=package)
            )
        

    def _create_user(self):
        harvest_user = model.User(name=u'harvest', password=u'test')
        model.add_user_to_role(harvest_user, model.Role.ADMIN, model.System())
        model.Session.add(harvest_user)
        model.Session.commit()

    def _create_publisher(self):
        self.publisher = model.Group(name=u'test-publisher',
                                     title=u'Test Publihser',
                                     type=u'publisher')
        model.Session.add(self.publisher)
        model.Session.commit()
        
    def _create_source_and_job(self):
        context ={'model': model,
                  'session': model.Session,
                  'user': u'harvest'}
        source_fixture = {
            'url': u'http://csw/GetCapabilities',
            'type': u'csw'
        }
        if config.get('ckan.harvest.auth.profile') == u'publisher' \
           and not 'publisher_id' in source_fixture:
           source_fixture['publisher_id'] = self.publisher.id

        source_dict=get_action('harvest_source_create')(context,source_fixture)
        source = HarvestSource.get(source_dict['id'])
        assert source

        job = self._create_job(source.id)

        return source, job
                
    def _create_job(self,source_id):
        # Create a job
        context ={'model':model,
                  'session':model.Session,
                  'user':u'harvest'}

        job_dict=get_action('harvest_job_create')(context,{'source_id':source_id})
        job = HarvestJob.get(job_dict['id'])
        assert job

        return job

def change_line(couples, line_to_change, replacement_line):
    '''Given a list of coupled resource tuples, returns a similar
    list, but with the line that matches line_to_change replaced
    with replacement_line.'''
    line_number = couples.index(line_to_change)
    return couples[:line_number] + [replacement_line] + couples[line_number+1:]

def add_line(couples, line_to_add):
    '''Given a list of coupled resource tuples, returns a similar
    list, but with the line added.'''
    return couples[:] + [line_to_add]

def remove_line(couples, line_to_remove):
    '''Given a list of coupled resource tuples, returns a similar
    list, but with the line added.'''
    line_number = couples.index(line_to_remove)
    return couples[:line_number] + couples[line_number+1:]

