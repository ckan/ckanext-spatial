from datetime import datetime, date
import lxml

from nose.tools import assert_equal, assert_in

from ckan import plugins
from ckan.lib.base import config
from ckan import model
from ckan.model import Session,Package
from ckan.logic.schema import default_update_package_schema
from ckan.logic import get_action
from ckanext.harvest.model import (setup as harvest_model_setup,
                                   HarvestSource, HarvestJob, HarvestObject)
from ckanext.spatial.validation import Validators, SchematronValidator
from ckanext.spatial.harvesters import (GeminiCswHarvester, GeminiDocHarvester,
                                        GeminiWafHarvester, SpatialHarvester)
from ckanext.spatial.model.package_extent import setup as spatial_db_setup
from ckanext.spatial.tests.base import SpatialTestBase

from xml_file_server import serve

class HarvestFixtureBase(SpatialTestBase):

    serving = False

    @classmethod
    def setup_class(cls):
        SpatialTestBase.setup_class()

        # Start simple HTTP server that serves XML test files
        if not cls.serving:
            serve()
            cls.serving = True
            # gets shutdown when nose finishes all tests,
            # so don't restart ever

    def setup(self):
        # Add sysadmin user
        harvest_user = model.User(name=u'harvest', password=u'test')
        model.add_user_to_role(harvest_user, model.Role.ADMIN, model.System())
        Session.add(harvest_user)
        Session.commit()

        package_schema = default_update_package_schema()
        self.context ={'model':model,
                       'session':Session,
                       'user':u'harvest',
                       'schema':package_schema,
                       'api_version': '2'}

        if config.get('ckan.harvest.auth.profile') == u'publisher':
            # Create a publisher user
            rev = model.repo.new_revision()
            self.publisher_user = model.User(name=u'test-publisher-user',password=u'test')
            self.publisher = model.Group(name=u'test-publisher',title=u'Test Publihser',type=u'publisher')
            Session.add(self.publisher_user)
            Session.add(self.publisher)

            Session.commit()

            member = model.Member(table_name = 'user',
                             table_id = self.publisher_user.id,
                             group=self.publisher,
                             capacity='admin')
            Session.add(member)

            Session.commit()

    def teardown(self):
       model.repo.rebuild_db()

    def _create_job(self,source_id):
        # Create a job
        context ={'model':model,
                 'session':Session,
                 'user':u'harvest'}

        job_dict=get_action('harvest_job_create')(context,{'source_id':source_id})
        job = HarvestJob.get(job_dict['id'])
        assert job

        return job

    def _create_source_and_job(self,source_fixture):
        context ={'model':model,
                 'session':Session,
                 'user':u'harvest'}

        if config.get('ckan.harvest.auth.profile') == u'publisher' \
           and not 'publisher_id' in source_fixture:
           source_fixture['publisher_id'] = self.publisher.id

        source_dict=get_action('harvest_source_create')(context,source_fixture)
        source = HarvestSource.get(source_dict['id'])
        assert source

        job = self._create_job(source.id)

        return source, job

    def _run_job_for_single_document(self,job,force_import=False,expect_gather_errors=False,expect_obj_errors=False):

        harvester = GeminiDocHarvester()

        harvester.force_import = force_import


        object_ids = harvester.gather_stage(job)
        assert object_ids, len(object_ids) == 1
        if expect_gather_errors:
            assert len(job.gather_errors) > 0
        else:
            assert len(job.gather_errors) == 0

        assert harvester.fetch_stage(object_ids) == True

        obj = HarvestObject.get(object_ids[0])
        assert obj, obj.content

        harvester.import_stage(obj)
        Session.refresh(obj)
        if expect_obj_errors:
            assert len(obj.errors) > 0
        else:
            assert len(obj.errors) == 0

        job.status = u'Finished'
        job.save()

        return obj

class TestHarvest(HarvestFixtureBase):

    @classmethod
    def setup_class(cls):
        SpatialHarvester._validator = Validators(profiles=['gemini2'])
        HarvestFixtureBase.setup_class()

    def test_harvest_basic(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1-waf/index.html',
            'type': u'gemini-waf'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiWafHarvester()

        # We need to send an actual job, not the dict
        object_ids = harvester.gather_stage(job)

        assert len(object_ids) == 2

        # Fetch stage always returns True for Waf harvesters
        assert harvester.fetch_stage(object_ids) == True

        objects = []
        for object_id in object_ids:
            obj = HarvestObject.get(object_id)
            assert obj
            objects.append(obj)
            harvester.import_stage(obj)

        pkgs = Session.query(Package).all()

        assert len(pkgs) == 2

        pkg_ids = [pkg.id for pkg in pkgs]

        for obj in objects:
            assert obj.current == True
            assert obj.package_id in pkg_ids

    def test_harvest_fields_service(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/service1.xml',
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        object_ids = harvester.gather_stage(job)
        assert object_ids, len(object_ids) == 1

        # No gather errors
        assert len(job.gather_errors) == 0

        # Fetch stage always returns True for Single Doc harvesters
        assert harvester.fetch_stage(object_ids) == True

        obj = HarvestObject.get(object_ids[0])
        assert obj, obj.content
        assert obj.guid == u'test-service-1'

        harvester.import_stage(obj)

        # No object errors
        assert len(obj.errors) == 0

        package_dict = get_action('package_show_rest')(self.context,{'id':obj.package_id})

        assert package_dict

        expected = {
            'name': u'one-scotland-address-gazetteer-web-map-service-wms',
            'title': u'One Scotland Address Gazetteer Web Map Service (WMS)',
            'tags': [u'Addresses', u'Scottish National Gazetteer'],
            'notes': u'This service displays its contents at larger scale than 1:10000. [edited]',
        }

        for key,value in expected.iteritems():
            if not package_dict[key] == value:
                raise AssertionError('Unexpected value for %s: %s (was expecting %s)' % \
                    (key, package_dict[key], value))

        if config.get('ckan.harvest.auth.profile') == u'publisher':
            assert package_dict['groups'] == [self.publisher.id]

        expected_extras = {
            # Basic
            'harvest_object_id': obj.id,
            'guid': obj.guid,
            'UKLP': u'True',
            'resource-type': u'service',
            'access_constraints': u'["No restriction on public access"]',
            'responsible-party': u'The Improvement Service (owner)',
            'provider':u'The Improvement Service',
            'contact-email': u'OSGCM@improvementservice.org.uk',
            # Spatial
            'bbox-east-long': u'0.5242365625',
            'bbox-north-lat': u'61.0243',
            'bbox-south-lat': u'54.4764484375',
            'bbox-west-long': u'-9.099786875',
            'spatial': u'{"type":"Polygon","coordinates":[[[0.5242365625, 54.4764484375],[0.5242365625, 61.0243], [-9.099786875, 61.0243], [-9.099786875, 54.4764484375], [0.5242365625, 54.4764484375]]]}',
            # Other
            'coupled-resource': u'[{"href": ["http://scotgovsdi.edina.ac.uk/srv/en/csw?service=CSW&request=GetRecordById&version=2.0.2&outputSchema=http://www.isotc211.org/2005/gmd&elementSetName=full&id=250ea276-48e2-4189-8a89-fcc4ca92d652"], "uuid": ["250ea276-48e2-4189-8a89-fcc4ca92d652"], "title": []}]',
            'dataset-reference-date': u'[{"type": "publication", "value": "2011-09-08"}]',
            'frequency-of-update': u'daily',
            'licence': u'["Use of the One Scotland Gazetteer data used by this this service is available to any organisation that is a member of the One Scotland Mapping Agreement. It is not currently commercially available", "http://www.test.gov.uk/licenseurl"]',
            'licence_url': u'http://www.test.gov.uk/licenseurl',
            'metadata-date': u'2011-09-08T16:07:32',
            'metadata-language': u'eng',
            'spatial-data-service-type': u'other',
            'spatial-reference-system': u'OSGB 1936 / British National Grid (EPSG:27700)',
            'temporal_coverage-from': u'["1904-06-16"]',
            'temporal_coverage-to': u'["2004-06-16"]',
        }

        for key,value in expected_extras.iteritems():
            if not key in package_dict['extras']:
                raise AssertionError('Extra %s not present in package' % key)

            if not package_dict['extras'][key] == value:
                raise AssertionError('Unexpected value for extra %s: %s (was expecting %s)' % \
                    (key, package_dict['extras'][key], value))

        expected_resource = {
            'ckan_recommended_wms_preview': 'True',
            'description': 'Link to the GetCapabilities request for this service',
            'format': 'WMS',
            'name': 'Web Map Service (WMS)',
            'resource_locator_function': 'download',
            'resource_locator_protocol': 'OGC:WMS-1.3.0-http-get-capabilities',
            'resource_type': None,
            'size': None,
            'url': u'http://sedsh13.sedsh.gov.uk/ArcGIS/services/OSG/OSG/MapServer/WMSServer?request=GetCapabilities&service=WMS',
            'verified': 'True',
        }

        resource = package_dict['resources'][0]
        for key,value in expected_resource.iteritems():
            if not resource[key] == value:
                raise AssertionError('Unexpected value in resource for %s: %s (was expecting %s)' % \
                    (key, resource[key], value))
        assert datetime.strptime(resource['verified_date'],'%Y-%m-%dT%H:%M:%S.%f').date() == date.today()

    def test_harvest_fields_dataset(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/dataset1.xml',
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        object_ids = harvester.gather_stage(job)
        assert object_ids, len(object_ids) == 1

        # No gather errors
        assert len(job.gather_errors) == 0

        # Fetch stage always returns True for Single Doc harvesters
        assert harvester.fetch_stage(object_ids) == True

        obj = HarvestObject.get(object_ids[0])
        assert obj, obj.content
        assert obj.guid == u'test-dataset-1'

        harvester.import_stage(obj)

        # No object errors
        assert len(obj.errors) == 0

        package_dict = get_action('package_show_rest')(self.context,{'id':obj.package_id})

        assert package_dict

        expected = {
            'name': u'country-parks-scotland',
            'title': u'Country Parks (Scotland)',
            'tags': [u'Nature conservation'],
            'notes': u'Parks are set up by Local Authorities to provide open-air recreation facilities close to towns and cities. [edited]'
        }

        for key,value in expected.iteritems():
            if not package_dict[key] == value:
                raise AssertionError('Unexpected value for %s: %s (was expecting %s)' % \
                    (key, package_dict[key], value))

        if config.get('ckan.harvest.auth.profile') == u'publisher':
            assert package_dict['groups'] == [self.publisher.id]

        expected_extras = {
            # Basic
            'harvest_object_id': obj.id,
            'guid': obj.guid,
            'resource-type': u'dataset',
            'responsible-party': u'Scottish Natural Heritage (custodian, distributor)',
            'access_constraints': u'["Copyright Scottish Natural Heritage"]',
            'contact-email': u'data_supply@snh.gov.uk',
            'provider':'',
            # Spatial
            'bbox-east-long': u'0.205857204',
            'bbox-north-lat': u'61.06066944',
            'bbox-south-lat': u'54.529947158',
            'bbox-west-long': u'-8.97114288',
            'spatial': u'{"type":"Polygon","coordinates":[[[0.205857204, 54.529947158],[0.205857204, 61.06066944], [-8.97114288, 61.06066944], [-8.97114288, 54.529947158], [0.205857204, 54.529947158]]]}',
            # Other
            'coupled-resource': u'[]',
            'dataset-reference-date': u'[{"type": "creation", "value": "2004-02"}, {"type": "revision", "value": "2006-07-03"}]',
            'frequency-of-update': u'irregular',
            'licence': u'["Reference and PSMA Only", "http://www.test.gov.uk/licenseurl"]',
            'licence_url': u'http://www.test.gov.uk/licenseurl',
            'metadata-date': u'2011-09-23T10:06:08',
            'metadata-language': u'eng',
            'spatial-reference-system': u'urn:ogc:def:crs:EPSG::27700',
            'temporal_coverage-from': u'["1998"]',
            'temporal_coverage-to': u'["2010"]',
        }

        for key,value in expected_extras.iteritems():
            if not key in package_dict['extras']:
                raise AssertionError('Extra %s not present in package' % key)

            if not package_dict['extras'][key] == value:
                raise AssertionError('Unexpected value for extra %s: %s (was expecting %s)' % \
                    (key, package_dict['extras'][key], value))

        expected_resource = {
            'description': 'Test Resource Description',
            'format': u'',
            'name': 'Test Resource Name',
            'resource_locator_function': 'download',
            'resource_locator_protocol': 'test-protocol',
            'resource_type': None,
            'size': None,
            'url': u'https://gateway.snh.gov.uk/pls/apex_ddtdb2/f?p=101',
        }

        resource = package_dict['resources'][0]
        for key,value in expected_resource.iteritems():
            if not resource[key] == value:
                raise AssertionError('Unexpected value in resource for %s: %s (was expecting %s)' % \
                    (key, resource[key], value))

    def test_harvest_error_bad_xml(self):
        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/error_bad_xml.xml',
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        try:
            object_ids = harvester.gather_stage(job)
        except lxml.etree.XMLSyntaxError:
            # this only occurs in debug_exception_mode
            pass
        else:
            assert object_ids is None

        # Check gather errors
        assert len(job.gather_errors) == 1
        assert job.gather_errors[0].harvest_job_id == job.id
        assert 'Error parsing the document' in job.gather_errors[0].message

    def test_harvest_error_404(self):
        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/not_there.xml',
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        object_ids = harvester.gather_stage(job)
        assert object_ids is None

        # Check gather errors
        assert len(job.gather_errors) == 1
        assert job.gather_errors[0].harvest_job_id == job.id
        assert 'Unable to get content for URL' in job.gather_errors[0].message

    def test_harvest_error_validation(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/error_validation.xml',
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        object_ids = harvester.gather_stage(job)

        # Right now the import process goes ahead even with validation errors
        assert object_ids, len(object_ids) == 1

        # No gather errors
        assert len(job.gather_errors) == 1
        assert job.gather_errors[0].harvest_job_id == job.id

        message = job.gather_errors[0].message

        assert_in('Validation error', message)
        assert_in('Validating against "GEMINI 2.1 Schematron 1.2" profile failed', message)
        assert_in('One email address shall be provided', message)
        assert_in('Service type shall be one of \'discovery\', \'view\', \'download\', \'transformation\', \'invoke\' or \'other\' following INSPIRE generic names', message)
        assert_in('Limitations on public access code list value shall be \'otherRestrictions\'', message)
        assert_in('One organisation name shall be provided', message)

        # Fetch stage always returns True for Single Doc harvesters
        assert harvester.fetch_stage(object_ids) == True

        obj = HarvestObject.get(object_ids[0])
        assert obj, obj.content
        assert obj.guid == u'test-error-validation-1'

        harvester.import_stage(obj)

        # Check errors
        assert len(obj.errors) == 1


    def test_harvest_update_records(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/dataset1.xml',
            'type': u'gemini-single'
        }

        source, first_job = self._create_source_and_job(source_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert first_package_dict
        assert first_obj.current == True
        assert first_obj.package

        # Create and run a second job, the package should not be updated
        second_job = self._create_job(source.id)

        second_obj = self._run_job_for_single_document(second_job)

        Session.remove()
        Session.add(first_obj)
        Session.add(second_obj)

        Session.refresh(first_obj)
        Session.refresh(second_obj)

        second_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was not updated
        assert second_package_dict, first_package_dict['id'] == second_package_dict['id']
        assert first_package_dict['metadata_modified'] == second_package_dict['metadata_modified']
        assert not second_obj.package, not second_obj.package_id
        assert second_obj.current == False, first_obj.current == True

        # Create and run a third job, forcing the importing to simulate an update in the package
        third_job = self._create_job(source.id)
        third_obj = self._run_job_for_single_document(third_job,force_import=True)

        # For some reason first_obj does not get updated after the import_stage,
        # and we have to force a refresh to get the actual DB values.
        Session.remove()
        Session.add(first_obj)
        Session.add(second_obj)
        Session.add(third_obj)

        Session.refresh(first_obj)
        Session.refresh(second_obj)
        Session.refresh(third_obj)

        third_package_dict = get_action('package_show_rest')(self.context,{'id':third_obj.package_id})

        # Package was updated
        assert third_package_dict, first_package_dict['id'] == third_package_dict['id']
        assert third_package_dict['metadata_modified'] > second_package_dict['metadata_modified']
        assert third_obj.package, third_obj.package_id == first_package_dict['id']
        assert third_obj.current == True
        assert second_obj.current == False
        assert first_obj.current == False

    def test_harvest_deleted_record(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/service1.xml',
            'type': u'gemini-single'
        }

        source, first_job = self._create_source_and_job(source_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert first_package_dict
        assert first_package_dict['state'] == u'active'
        assert first_obj.current == True

        # Delete package
        first_package_dict['state'] = u'deleted'
        self.context.update({'id':first_package_dict['id']})
        updated_package_dict = get_action('package_update_rest')(self.context,first_package_dict)

        # Create and run a second job, the date has not changed, so the package should not be updated
        # and remain deleted
        first_job.status = u'Finished'
        first_job.save()
        second_job = self._create_job(source.id)

        second_obj = self._run_job_for_single_document(second_job)

        second_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was not updated
        assert second_package_dict, updated_package_dict['id'] == second_package_dict['id']
        assert not second_obj.package, not second_obj.package_id
        assert second_obj.current == False, first_obj.current == True


        # Harvest an updated document, with a more recent modified date, package should be
        # updated and reactivated
        source.url = u'http://127.0.0.1:8999/gemini2.1/service1_newer.xml'
        source.save()

        third_job = self._create_job(source.id)

        third_obj = self._run_job_for_single_document(third_job)

        third_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        Session.remove()
        Session.add(first_obj)
        Session.add(second_obj)
        Session.add(third_obj)

        Session.refresh(first_obj)
        Session.refresh(second_obj)
        Session.refresh(third_obj)

        # Package was updated
        assert third_package_dict, third_package_dict['id'] == second_package_dict['id']
        assert third_obj.package, third_obj.package
        assert third_obj.current == True, second_obj.current == False
        assert first_obj.current == False

        assert 'NEWER' in third_package_dict['title']
        assert third_package_dict['state'] == u'active'



    def test_harvest_different_sources_same_document(self):

        # Create source1
        source1_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/source1/same_dataset.xml',
            'type': u'gemini-single'
        }

        source1, first_job = self._create_source_and_job(source1_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert first_package_dict
        assert first_package_dict['state'] == u'active'
        assert first_obj.current == True

        # Harvest the same document, unchanged, from another source, the package
        # is not updated.
        # (As of https://github.com/okfn/ckanext-inspire/commit/9fb67
        # we are no longer throwing an exception when this happens)
        source2_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/source2/same_dataset.xml',
            'type': u'gemini-single'
        }

        source2, second_job = self._create_source_and_job(source2_fixture)

        second_obj = self._run_job_for_single_document(second_job)

        second_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was not updated
        assert second_package_dict, first_package_dict['id'] == second_package_dict['id']
        assert first_package_dict['metadata_modified'] == second_package_dict['metadata_modified']
        assert not second_obj.package, not second_obj.package_id
        assert second_obj.current == False, first_obj.current == True


        # Inactivate source1 and reharvest from source2, package should be updated
        third_job = self._create_job(source2.id)
        third_obj = self._run_job_for_single_document(third_job,force_import=True)

        Session.remove()
        Session.add(first_obj)
        Session.add(second_obj)
        Session.add(third_obj)

        Session.refresh(first_obj)
        Session.refresh(second_obj)
        Session.refresh(third_obj)

        third_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was updated
        assert third_package_dict, first_package_dict['id'] == third_package_dict['id']
        assert third_package_dict['metadata_modified'] > second_package_dict['metadata_modified']
        assert third_obj.package, third_obj.package_id == first_package_dict['id']
        assert third_obj.current == True
        assert second_obj.current == False
        assert first_obj.current == False


    def test_harvest_different_sources_same_document_but_deleted_inbetween(self):

        # Create source1
        source1_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/source1/same_dataset.xml',
            'type': u'gemini-single'
        }

        source1, first_job = self._create_source_and_job(source1_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert first_package_dict
        assert first_package_dict['state'] == u'active'
        assert first_obj.current == True

        # Delete/withdraw the package
        first_package_dict = get_action('package_delete')(self.context,{'id':first_obj.package_id})
        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Harvest the same document, unchanged, from another source
        source2_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/source2/same_dataset.xml',
            'type': u'gemini-single'
        }

        source2, second_job = self._create_source_and_job(source2_fixture)

        second_obj = self._run_job_for_single_document(second_job)

        second_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # It would be good if the package was updated, but we see that it isn't
        assert second_package_dict, first_package_dict['id'] == second_package_dict['id']
        assert second_package_dict['metadata_modified'] == first_package_dict['metadata_modified']
        assert not second_obj.package
        assert second_obj.current == False
        assert first_obj.current == True


    def test_harvest_moves_sources(self):

        # Create source1
        source1_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/service1.xml',
            'type': u'gemini-single'
        }

        source1, first_job = self._create_source_and_job(source1_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        first_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert first_package_dict
        assert first_package_dict['state'] == u'active'
        assert first_obj.current == True

        # Harvest the same document GUID but with a newer date, from another source. 
        source2_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/service1_newer.xml',
            'type': u'gemini-single'
        }

        source2, second_job = self._create_source_and_job(source2_fixture)

        second_obj = self._run_job_for_single_document(second_job)

        second_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Now we have two packages
        assert second_package_dict, first_package_dict['id'] == second_package_dict['id']
        assert second_package_dict['metadata_modified'] > first_package_dict['metadata_modified']
        assert second_obj.package
        assert second_obj.current == True
        assert first_obj.current == True
        # so currently, if you move a Gemini between harvest sources you need
        # to update the date to get it to reharvest, and then you should
        # withdraw the package relating to the original harvest source.


    def test_harvest_import_command(self):

        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/dataset1.xml',
            'type': u'gemini-single'
        }

        source, first_job = self._create_source_and_job(source_fixture)

        first_obj = self._run_job_for_single_document(first_job)

        before_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was created
        assert before_package_dict
        assert first_obj.current == True
        assert first_obj.package

        # Create and run two more jobs, the package should not be updated
        second_job = self._create_job(source.id)
        second_obj = self._run_job_for_single_document(second_job)
        third_job = self._create_job(source.id)
        third_obj = self._run_job_for_single_document(third_job)

        # Run the import command manually
        imported_objects = get_action('harvest_objects_import')(self.context,{'source_id':source.id})
        Session.remove()
        Session.add(first_obj)
        Session.add(second_obj)
        Session.add(third_obj)

        Session.refresh(first_obj)
        Session.refresh(second_obj)
        Session.refresh(third_obj)

        after_package_dict = get_action('package_show_rest')(self.context,{'id':first_obj.package_id})

        # Package was updated, and the current object remains the same
        assert after_package_dict, before_package_dict['id'] == after_package_dict['id']
        assert after_package_dict['metadata_modified'] > before_package_dict['metadata_modified']
        assert third_obj.current == False
        assert second_obj.current == False
        assert first_obj.current == True


        source_dict = get_action('harvest_source_show')(self.context,{'id':source.id})
        assert len(source_dict['status']['packages']) == 1


class TestValidation(HarvestFixtureBase):

    @classmethod
    def setup_class(cls):
        SpatialHarvester._validator = Validators(profiles=['iso19139eden', 'constraints', 'gemini2'])
        HarvestFixtureBase.setup_class()

    def get_validation_errors(self, validation_test_filename):
        # Create source
        source_fixture = {
            'url': u'http://127.0.0.1:8999/gemini2.1/validation/%s' % validation_test_filename,
            'type': u'gemini-single'
        }

        source, job = self._create_source_and_job(source_fixture)

        harvester = GeminiDocHarvester()

        # Gather stage for GeminiDocHarvester includes validation
        object_ids = harvester.gather_stage(job)

        # Check the validation errors
        errors = '; '.join([gather_error.message for gather_error in job.gather_errors])
        return errors

    def test_01_dataset_fail_iso19139_schema(self):
        errors = self.get_validation_errors('01_Dataset_Invalid_XSD_No_Such_Element.xml')
        assert len(errors) > 0
        assert_in('ISO19139', errors)
        assert_in('(gmx.xsd)', errors)
        assert_in('Could not get the GUID', errors)

    def test_02_dataset_fail_constraints_schematron(self):
        errors = self.get_validation_errors('02_Dataset_Invalid_19139_Missing_Data_Format.xml')
        assert len(errors) > 0
        assert_in('Constraints', errors)
        assert_in('MD_Distribution / MD_Format: count(distributionFormat + distributorFormat) > 0', errors)

    def test_03_dataset_fail_gemini_schematron(self):
        errors = self.get_validation_errors('03_Dataset_Invalid_GEMINI_Missing_Keyword.xml')
        assert len(errors) > 0
        assert_in('GEMINI', errors)
        assert_in('Descriptive keywords are mandatory', errors)

    def test_04_dataset_valid(self):
        errors = self.get_validation_errors('04_Dataset_Valid.xml')
        assert len(errors) == 0

    def test_05_series_fail_iso19139_schema(self):
        errors = self.get_validation_errors('05_Series_Invalid_XSD_No_Such_Element.xml')
        assert len(errors) > 0
        assert_in('ISO19139', errors)
        assert_in('(gmx.xsd)', errors)
        assert_in('Could not get the GUID', errors)

    def test_06_series_fail_constraints_schematron(self):
        errors = self.get_validation_errors('06_Series_Invalid_19139_Missing_Data_Format.xml')
        assert len(errors) > 0
        assert_in('Constraints', errors)
        assert_in('MD_Distribution / MD_Format: count(distributionFormat + distributorFormat) > 0', errors)

    def test_07_series_fail_gemini_schematron(self):
        errors = self.get_validation_errors('07_Series_Invalid_GEMINI_Missing_Keyword.xml')
        assert len(errors) > 0
        assert_in('GEMINI', errors)
        assert_in('Descriptive keywords are mandatory', errors)

    def test_08_series_valid(self):
        errors = self.get_validation_errors('08_Series_Valid.xml')
        assert len(errors) == 0

    def test_09_service_fail_iso19139_schema(self):
        errors = self.get_validation_errors('09_Service_Invalid_No_Such_Element.xml')
        assert len(errors) > 0
        assert_in('ISO19139', errors)
        assert_in('(gmx.xsd & srv.xsd)', errors)
        assert_in('Could not get the GUID', errors)

    def test_10_service_fail_constraints_schematron(self):
        errors = self.get_validation_errors('10_Service_Invalid_19139_Level_Description.xml')
        assert len(errors) > 0
        assert_in('Constraints', errors)
        assert_in("DQ_Scope: 'levelDescription' is mandatory if 'level' notEqual 'dataset' or 'series'.", errors)

    def test_11_service_fail_gemini_schematron(self):
        errors = self.get_validation_errors('11_Service_Invalid_GEMINI_Service_Type.xml')
        assert len(errors) > 0
        assert_in('GEMINI', errors)
        assert_in("Service type shall be one of 'discovery', 'view', 'download', 'transformation', 'invoke' or 'other' following INSPIRE generic names.", errors)

    def test_12_service_valid(self):
        errors = self.get_validation_errors('12_Service_Valid.xml')
        assert len(errors) == 0, errors

    def test_13_dataset_fail_iso19139_schema_2(self):
        # This test Dataset has srv tags and only Service metadata should.
        errors = self.get_validation_errors('13_Dataset_Invalid_Element_srv.xml')
        assert len(errors) > 0
        assert_in('ISO19139', errors)
        assert_in('(gmx.xsd)', errors)
        assert_in('(u"Element \'{http://www.isotc211.org/2005/srv}SV_ServiceIdentification\': This element is not expected.', errors)
