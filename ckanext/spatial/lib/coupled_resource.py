import re
import logging

from ckan.lib.base import json
from ckanext.harvest.model import HarvestCoupledResource
from ckan import model

log = logging.getLogger(__name__)

guid_matcher = None

class CoupledResourceParseError(Exception):
    pass

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
    return guid or coupled_href.strip()

def extract_harvest_source_reference_from_coupled_resource(coupled_resource_dict):
    '''Given a coupled_resource_dict, returns the harvest_source_reference.

    May raise CoupledResourceParseError.
    '''
    href = coupled_resource_dict['href']
    if len(href) <> 1:
        raise CoupledResourceParseError('Coupled resource href is not a list of 1: %r' % href)
    href = href[0]
    if not href.strip():
        raise CoupledResourceParseError('Coupled resource href is blank.')
    ref = extract_gemini_harvest_source_reference(href)
    if not ref:
        raise CoupledResourceParseError('Coupled resource harvest source reference is blank')
    return ref
        
def _package_name(package_or_none):
    return package_or_none.name if package_or_none else None

def update_coupled_resources(package, harvest_source_reference):
    '''Update the harvest_coupled_resource_table with the details of this
    harvested package\'s couplings.

    :param package: the Package object containing extra fields with couples
                    to update in the table.
    :param harvest_source_reference: the ref of this package being harvested.
                    This is not relevant if it is a service record, but
                    essential if it is a dataset.
    '''
    resource_type = package.extras['resource-type']
    if resource_type == 'service':
        # When a service record is harvested, ensure the couples listed
        # in it match the couples in the HarvestCoupledResource objects,
        # ignoring their dataset values (they might be filled in or not).
        pkg_couples_str = package.extras['coupled-resource']
        pkg_couples = json.loads(pkg_couples_str)
        log.info('Service Record %s has %i coupled resources to update',
                 package.name, len(pkg_couples))

        table_couples_matching_service = HarvestCoupledResource.get_by_service_record(package)
        table_couples_not_matching_pkg = table_couples_matching_service.all() # cross them off as we go

        for pkg_couple in pkg_couples:
            try:
                ref = extract_harvest_source_reference_from_coupled_resource(pkg_couple)
            except CoupledResourceParseError, e:
                log.warn('Error parsing couple: %s Ignoring couple=%s', e, pkg_couple)
                continue
            # Match both service and ref
            matching_table_couples = table_couples_matching_service.filter_by(harvest_source_reference=ref)
            if matching_table_couples.count() > 0:
                # Test: test_02_reharvest_existing_service
                # Note down the matches so we don't delete them later
                for matching_table_couple in matching_table_couples:
                    log.info('Service couple is already there (%s, %s, %s)',
                             package.name, ref,
                             _package_name(matching_table_couple.dataset_record))
                    table_couples_not_matching_pkg.remove(matching_table_couple)
                continue
            # Match just ref with blank service
            matching_table_couples = HarvestCoupledResource.get_by_harvest_source_reference(ref)\
                                     .filter_by(service_record=None)
            if matching_table_couples.count() == 0:
                # Test: test_06_harvest_service_not_matching_a_dataset
                # create the row
                obj = HarvestCoupledResource(service_record=package,
                                             harvest_source_reference=ref)
                model.Session.add(obj)
                log.info('Ref is new for this service - adding (%s, %s, None)',
                         package.name, ref)
                model.Session.commit()
            else:
                # Test: test_04_harvest_service_to_match_existing_dataset
                for matching_table_couple in matching_table_couples:
                    # fill in the service value
                    matching_table_couple.service_record = package
                    log.info('Service filled into couple matching ref (%s, %s, %s)',
                             package.name, ref,
                             _package_name(matching_table_couple.dataset_record))
                model.Session.commit()

        # Delete service value for any table_couples not matching the package
        # Test: test_08_reharvest_existing_service_to_delete_and_add_couples
        for table_couple in table_couples_not_matching_pkg:
            log.info('Service couple not matched - deleted service (%s->None, %s, %s)',
                     _package_name(table_couple.service_record),
                     ref, _package_name(table_couple.dataset_record))
            table_couple.service_record = None
            model.Session.commit()
        return
    elif resource_type in ('dataset', 'series'):
        # When a dataset (or dataset series) record is harvested, for its
        # dataset_record_package_id there should be one ref - any with another
        # ref is removed. And for the dataset_record_package_id and ref combo
        # there should be one or more HarvestCoupledResource objects (with
        # a service or without).

        # Couples where this dataset is under a different ref
        # Test: test_07_reharvest_existing_dataset_but_with_changed_ref
        ref = harvest_source_reference
        assert ref
        for couple in model.Session.query(HarvestCoupledResource) \
            .filter_by(dataset_record=package) \
            .filter(HarvestCoupledResource.harvest_source_reference!=ref):
            log.info('Ref %s has been replaced for this dataset record with '
                     '%s. Removing link to the dataset record (%s, %s, %s->None)',
                     couple.harvest_source_reference, ref,
                     _package_name(couple.service_record),
                     couple.harvest_source_reference,
                     _package_name(couple.dataset_record))
            couple.dataset_record = None
            model.Session.commit()

        # Couples with this ref
        for couple in HarvestCoupledResource.get_by_harvest_source_reference(ref):
            if couple.dataset_record != package:
                # Test: test_03_harvest_dataset_to_match_existing_service
                log.info('Linking ref to this dataset record (%s, %s, %s->%s)',
                         _package_name(couple.service_record),
                         ref,
                         _package_name(couple.dataset_record),
                         package.name)
                couple.dataset_record = package
                model.Session.commit()
            else:
                # Test: test_01_reharvest_existing_dataset
                log.info('Couple for this dataset and ref already exists (%s, %s, %s)',
                         _package_name(couple.service_record),
                         ref,
                         _package_name(couple.dataset_record))

        # No couples for this ref
        couples = HarvestCoupledResource.get_by_harvest_source_reference(ref)
        if couples.count() == 0:
            # Test: test_05_harvest_dataset_not_matching_a_service
            obj = HarvestCoupledResource(dataset_record=package,
                                         harvest_source_reference=ref)
            model.Session.add(obj)
            log.info('Ref is new - adding new dataset couple (None, %s, %s)',
                     ref, package.name)
            model.Session.commit()
            return
