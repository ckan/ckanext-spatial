# template helpers

from ckan import model
from ckan.lib.base import json
from ckanext.harvest.model import HarvestObject, HarvestCoupledResource
from ckanext.spatial.lib.coupled_resource import extract_gemini_harvest_source_reference

def get_coupled_packages(pkg):
    res_type = pkg.extras.get('resource-type')
    if res_type in ('dataset', 'series'):
        coupled_resources = pkg.coupled_service
        coupled_packages = \
                  [(couple.service_record.name, couple.service_record.title) \
                   for couple in coupled_resources \
                   if couple.service_record_package_id]
        return coupled_packages
    
    elif res_type == 'service':
        # Find the dataset records which are pointed to in this service record
        coupled_resources = pkg.coupled_dataset
        coupled_packages = \
                  [(couple.dataset_record.name, couple.dataset_record.title) \
                   for couple in coupled_resources \
                   if couple.dataset_record_package_id]
        return coupled_packages

