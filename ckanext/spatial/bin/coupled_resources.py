'''
Coupled Resources migration tool
'''

import re
import os
import logging
import sys
import requests

from pylons import config
from nose.tools import assert_equal
from lxml import etree

from ckanext.dgu.bin import common
from ckanext.dgu.bin.running_stats import StatsList

service_stats = StatsList()
couple_stats = StatsList()
additional_couple_stats = StatsList()

class FindError(Exception):
    pass

class CoupledResources(object):
    @classmethod
    def detect(cls):
        '''Finds datasets that are coupled and adds their
        harvest_source_reference to the HarvestObject and package extras.
        '''
        from ckan.lib.base import json
        from ckan import model
        from ckanext.harvest.model import HarvestObject
        from ckanext.spatial.model import GeminiDocument
        from ckanext.spatial.lib.coupled_resource import extract_guid

        # Find service records
        for service_record in model.Session.query(model.Package).\
            filter_by(state='active').\
            join(model.PackageExtra).\
            filter_by(state='active').\
            filter_by(key='resource-type').\
            filter_by(value='service'):

            # Find coupled dataset records
            service_type = service_record.extras['resource-type']
            if not 'coupled-resource' in service_record.extras:
                if service_type in ('view', 'download'):
                    service_stats.add('No coupled-resource extra for %s type (where it is mandatory)', service_record.name, service_type)
                else:
                    service_stats.add('No coupled-resource extra (but not mandatory for this service type)', service_record.name)
                continue                
            coupled_resources_str = service_record.extras['coupled-resource']
            coupled_resources = json.loads(coupled_resources_str)
            log.info('%s has %i coupled resources',
                     service_record.name, len(coupled_resources))
            couples_all_detected = True
            couples_detected = False
            for i, coupled_resource in enumerate(coupled_resources):
                couple_id = '%s.%s' % (service_record.name, i)
                href = coupled_resource['href']

                # For tests only
                #if href != ['http://www.ordnancesurvey.co.uk/oswebsite/xml/products/Topo.xml']:
                #    break
                
                if len(href) <> 1:
                    log.error('Coupled resource href is not a list of 1: %r couple=%s',
                              href, couple_id)
                    couple_stats.add('Couple href is length %i' % len(href), couple_id)
                    couples_all_detected = False
                    continue
                href = href[0]
                if not href.strip():
                    log.error('Coupled resource href is blank. couple=%s',
                              couple_id)
                    couple_stats.add('Couple href is blank', couple_id)
                    couples_all_detected = False
                    continue
                    
                # Look for the equivalent dataset resource

                # If it is CSW, we must extract the guid
                # Example CSW url: http://ogcdev.bgs.ac.uk/geonetwork/srv/en/csw?SERVICE=CSW&amp;REQUEST=GetRecordById&amp;ID=9df8df52-d788-37a8-e044-0003ba9b0d98&amp;elementSetName=full&amp;OutputSchema=http://www.isotc211.org/2005/gmd
                guid = extract_guid(href)
                if guid:
                    if not guid.strip():
                        couple_stats.add('Guid was blank', couple_id)
                        log.error('Guid was blank. href=%s', href, couple_id)
                        
                    try:
                        harvest_object = cls.find_harvest_object_by_guid(guid)
                    except FindError, e:
                        log.error('%s guid=%s couple=%s', e, guid, couple_id)
                        couple_stats.add(str(e), couple_id)
                        couples_all_detected = False
                        continue

                    dataset_record = harvest_object.package #res.resource_group.package
                    couple_stats.add('Couple completed', couple_id)
                    log.info('Couple completed %s <-> %s',
                             service_record.name, dataset_record.name)
                    
                    cls.add_coupling(service_record, dataset_record, harvest_object, guid)
                    couples_detected = True
                    continue

                # Known bad couples are weeded out
                bad_couples = ('GetCapabilities', 'CEH:EIDC',
                               'ceh:eidc',
                               'http://data.nbn.org.uk#',
                               'www.geostore.com/OGC/OGCInterface',
                               'spatialni.gov.uk/arcgis/services/LPS/CadastreNI/MapServer/WMSServer',
                               'Please enter a valid url',
                               )
                bad_couple_detected = False
                for bad_couple in bad_couples:
                    if bad_couple in href:
                        couple_stats.add('Invalid couple (%s)' % bad_couple, couple_id)
                        log.info('Invalid couple (%s): %s couple=%s', bad_couple, href, couple_id)
                        bad_couple_detected = True
                if bad_couple_detected:
                    couples_all_detected = False
                    continue
                
                # Try as a WAF
                # Try the URL to download the gemini again, to find the
                # GUID of the dataset
                log.info('Trying possible WAF href: %s' % href)
                try:
                    res = requests.get(href, timeout=10)
                except Exception, e:
                    couple_stats.add('Connecting to href failed: %s' % \
                                     e, couple_id)
                    log.warning('Connecting to href failed: %s href:"%s"', \
                                     e, href)
                    couples_all_detected = False
                    break                    
                if not res.ok:
                    couple_stats.add('Resolving href failed: %s' % \
                                     res.reason, couple_id)
                    log.warning('Resolving href failed: %s %s href:"%s"', \
                                     res.status_code, res.reason, href)
                    couples_all_detected = False
                    break
                gemini = GeminiDocument(res.content)
                try:
                    guid = gemini.read_value('guid')
                except KeyError, e:
                    couple_stats.add('Could not get GUID from Gemini downloaded' % \
                                     href, couple_id)
                    log.warning('Could not get GUID from Gemini downloaded href:"%s"', \
                                     href)
                    couples_all_detected = False
                    break
                except etree.XMLSyntaxError, e:
                    couple_stats.add('Could not parse "Gemini" downloaded',
                                     couple_id)
                    log.warning('Could not parse "Gemini" downloaded href:"%s"', \
                                     href)
                    couples_all_detected = False
                    break
                try:
                    harvest_object = cls.find_harvest_object_by_guid(guid)
                except FindError, e:
                    log.error('%s href=%s couple=%s', e, href, couple_id)
                    couple_stats.add(str(e), couple_id)
                    couples_all_detected = False
                    continue

                dataset_record = harvest_object.package #res.resource_group.package
                couple_stats.add('Couple completed', couple_id)
                log.info('Couple completed %s <-> %s',
                         service_record.name, dataset_record.name)

                cls.add_coupling(service_record, dataset_record, harvest_object, href)
                couples_detected = True

            if coupled_resources:
                if couples_all_detected:
                    service_stats.add('Service couples all completed', service_record.name)
                elif couples_detected:
                    service_stats.add('Service couples partially completed', service_record.name)
                else:
                    service_stats.add('Service couples not completed', service_record.name)
            else:
                if service_type in ('view', 'download'):
                    service_stats.add('No couples for %s type (where it is mandatory)', service_record.name, service_type)
                else:
                    service_stats.add('No couples (but not mandatory for service type %s)' % service_type, service_record.name)
                continue                

        model.Session.remove()

        # Ensure all dataset records are in the harvest_coupled_resource table
        # for future reference
        for dataset_record in model.Session.query(model.Package).\
            filter_by(state='active').\
            join(model.PackageExtra).\
            filter_by(state='active').\
            filter_by(key='resource-type').\
            filter(model.PackageExtra.value.in_(('dataset', 'series'))):
            cls.ensure_dataset_is_in_couple_table(dataset_record)
        model.Session.remove()
        
        print "\nServices:"
        print service_stats.report()
        print "\nCouples:"
        print couple_stats.report()
        print "\nAdditional datasets added to couple table:"
        print additional_couple_stats.report()
    
    @classmethod
    def find_harvest_object_by_guid(cls, guid):
        from ckan import model
        from ckanext.harvest.model import HarvestObject
        
        q = model.Session.query(HarvestObject).\
            filter_by(guid=guid).\
            filter_by(current=True)
        if q.count() == 0:
            raise FindError('No matches for guid')
        if q.count() <> 1:
            raise FindError('Wrong number of matches (%i) for guid' % \
                            q.count())
        harvest_object = q.one()
        return harvest_object

        
    @classmethod
    def add_coupling(cls, service_record, dataset_record,
                     dataset_harvest_object, harvest_source_reference):
        from ckan import model
        from ckanext.harvest.model import HarvestCoupledResource
        
        if dataset_harvest_object.harvest_source_reference != harvest_source_reference:
            dataset_harvest_object.harvest_source_reference = harvest_source_reference
            model.Session.commit()
        q = model.Session.query(HarvestCoupledResource) \
            .filter_by(service_record_package_id=service_record.id) \
            .filter_by(dataset_record_package_id=dataset_record.id) \
            .filter_by(harvest_source_reference=harvest_source_reference)
        if q.count() == 0:
            obj = HarvestCoupledResource(
                service_record_package_id=service_record.id,
                dataset_record_package_id=dataset_record.id,
                harvest_source_reference=harvest_source_reference)
            model.Session.add(obj)
            model.Session.commit()

    @classmethod
    def ensure_dataset_is_in_couple_table(cls, dataset_record):
        from ckan import model
        from ckanext.harvest.model import HarvestCoupledResource
        
        q = model.Session.query(HarvestCoupledResource) \
            .filter_by(dataset_record_package_id=dataset_record.id)
        if q.count() == 0:
            harvest_objects = [ho for ho in dataset_record.harvest_objects \
                               if ho.current]
            if len(harvest_objects) != 1:
                log.warning('Wrong num of current harvest_objects (%i)',
                            len(harvest_objects))
                additional_couple_stats.add('Wrong num of harvest_objects (%i)' % len(harvest_objects),
                                            dataset_record.name)
                return
            harvest_object = harvest_objects[0]
            harvest_source_reference = harvest_object.harvest_source_reference
            
            obj = HarvestCoupledResource(
                dataset_record_package_id=dataset_record.id,
                harvest_source_reference=harvest_source_reference)
            model.Session.add(obj)
            model.Session.commit()
            additional_couple_stats.add('Added to couple table',
                                        dataset_record.name)
            log.info('Added to couple table: %s', dataset_record.name)
        else:
            additional_couple_stats.add('Already in couple table',
                                        dataset_record.name)
            log.info('Already in couple table: %s', dataset_record.name)
        

    @classmethod
    def setup_logging(cls, config_ini_filepath):
        logging.config.fileConfig(config_ini_filepath)
        global log
        log = logging.getLogger(os.path.basename(__file__))


warnings = []
log = None
def warn(msg, *params):
    global warnings
    warnings.append(msg % params)
    global_log.warn(msg, *params)


def usage():
    print """
Coupled Resources tool
Usage:

  python coupled_resources.py <CKAN config ini filepath> detect
    - finds datasets that are coupled and adds their harvest_source_reference
    """

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Wrong number of arguments %i' % len(sys.argv)
        usage()
        sys.exit(0)
    cmd, config_ini, action = sys.argv
    common.load_config(config_ini)
    CoupledResources.setup_logging(config_ini)
    common.register_translator()
    if action == 'detect':
        CoupledResources.detect()
    else:
        raise NotImplementedError
