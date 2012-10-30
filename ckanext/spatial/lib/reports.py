import logging

from lxml import etree

from ckanext.spatial.harvesters import SpatialHarvester
from ckanext.spatial.lib.report import ReportTable
from ckan import model
from ckanext.harvest.model import HarvestObject

def validation_report(package_id=None):
    '''
    Looks at every harvested metadata record and compares the
    validation errors that it had on last import and what it would be with
    the current validators. Useful when going to update the validators.

    Returns a ReportTable.
    '''
    log = logging.getLogger(__name__ + '.validation_report')

    validators = SpatialHarvester()._get_validator()
    log.debug('Validators: %r', validators.profiles)

    query = model.Session.query(HarvestObject).\
            filter_by(current=True).\
            order_by(HarvestObject.fetch_finished.desc())

    if package_id:
        query = query.filter(HarvestObject.package_id==package_id)

    report = ReportTable([
        'Harvest Object id',
        'GEMINI2 id',
        'Date fetched',
        'Dataset name',
        'Publisher',
        'Source URL',
        'Old validation errors',
        'New validation errors'])

    old_validation_failure_count = 0
    new_validation_failure_count = 0

    for harvest_object in query:
        validation_errors = []
        for err in harvest_object.errors:
            if 'not a valid Gemini' in err.message or \
                   'Validating against' in err.message:
                validation_errors.append(err.message)
        if validation_errors:
            old_validation_failure_count += 1

        groups = harvest_object.package.get_groups()
        publisher = groups[0].title if groups else '(none)'

        xml = etree.fromstring(harvest_object.content.encode("utf-8"))
        valid, errors = validators.is_valid(xml)
        if not valid:
            new_validation_failure_count += 1
                         
        report.add_row_dict({
                             'Harvest Object id': harvest_object.id,
                             'GEMINI2 id': harvest_object.guid,
                             'Date fetched': harvest_object.fetch_finished,
                             'Dataset name': harvest_object.package.name,
                             'Publisher': publisher,
                             'Source URL': harvest_object.source.url,
                             'Old validation errors': '; '.join(validation_errors),
                             'New validation errors': '; '.join(errors),
                             })

    log.debug('%i results', query.count())
    log.debug('%i failed old validation', old_validation_failure_count)
    log.debug('%i failed new validation', new_validation_failure_count)
    return report
