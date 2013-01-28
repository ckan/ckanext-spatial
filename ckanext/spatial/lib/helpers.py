# template helpers

from ckan import model
from ckan.lib.base import json
from ckanext.harvest.model import HarvestObject
from ckanext.spatial.lib.coupled_resource import extract_gemini_harvest_source_reference

def get_coupled_packages(pkg_extras):
    res_type = pkg_extras.get('resource-type')
    if res_type in ('dataset', 'series'):
        coupled_packages = []
        # Find the service records which point to this dataset record
        harvest_object_id = pkg_extras.get('harvest_object_id')
        if not harvest_object_id:
            return coupled_packages
        harvest_object = HarvestObject.get(harvest_object_id)
        dataset_ref = harvest_object.harvest_source_reference
        if not dataset_ref:
            return coupled_packages # []
        q = model.Session.query(model.Package) \
                .join(model.PackageExtra) \
                .join(HarvestObject) \
                .filter(HarvestObject.current==True) \
                .filter(model.PackageExtra.key=='coupled-resource') \
                .filter(model.PackageExtra.value.like('%' + dataset_ref + '%'))
        # probably 0, 1 or 2 results if there is a view and download service.
        coupled_packages.extend([(pkg.name, pkg.title) for pkg in q.all()])
        return coupled_packages
    
    elif res_type == 'service':
        # Find the dataset records which are pointed to in this service record
        coupled_resources_str = pkg_extras.get('coupled-resource', '[]')
        coupled_resources = json.loads(coupled_resources_str)
        coupled_packages = []
        for coupled_resource in coupled_resources:
            hrefs = coupled_resource.get('href', '')
            href = hrefs[0].strip()
            harvest_source_reference = extract_gemini_harvest_source_reference(href)
            if not harvest_source_reference:
                continue
            q = model.Session.query(model.Package) \
                .join(HarvestObject) \
                .filter(HarvestObject.current==True) \
                .filter(HarvestObject.harvest_source_reference==harvest_source_reference) \
                .filter(model.Package.state==u'active')
            # probably 0 or 1 results, but there is the possibility
            # WAFs lead to multiple results. Just add them all in that case.
            coupled_packages.extend([(pkg.name, pkg.title) for pkg in q.all()])
        return coupled_packages


