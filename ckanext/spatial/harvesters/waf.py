import logging
import hashlib
from urlparse import urljoin
import dateutil.parser
import pyparsing as parse
import requests
from sqlalchemy.orm import aliased
from sqlalchemy.exc import DataError

from ckan import model

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra
import ckanext.harvest.queue as queue

from ckanext.spatial.harvesters.base import SpatialHarvester, guess_standard

log = logging.getLogger(__name__)


class WAFHarvester(SpatialHarvester, SingletonPlugin):
    '''
    A Harvester for WAF (Web Accessible Folders) containing spatial metadata documents.
    e.g. Apache serving a directory of ISO 19139 files.
    '''

    implements(IHarvester)

    def info(self):
        return {
            'name': 'waf',
            'title': 'Web Accessible Folder (WAF)',
            'description': 'A Web Accessible Folder (WAF) displaying a list of spatial metadata documents'
            }


    def get_original_url(self, harvest_object_id):
        url = model.Session.query(HOExtra.value).\
                                    filter(HOExtra.key=='waf_location').\
                                    filter(HOExtra.harvest_object_id==harvest_object_id).\
                                    first()

        return url[0] if url else None


    def gather_stage(self,harvest_job,collection_package_id=None):
        log = logging.getLogger(__name__ + '.WAF.gather')
        log.debug('WafHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job

        # Get source URL
        source_url = harvest_job.source.url

        self._set_source_config(harvest_job.source.config)

        # Get contents
        try:
            response = requests.get(source_url, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException, e:
            self._save_gather_error('Unable to get content for URL: %s: %r' % \
                                        (source_url, e),harvest_job)
            return None

        content = response.content
        scraper = _get_scraper(response.headers.get('server'))

        ######  Get current harvest object out of db ######

        url_to_modified_db = {} ## mapping of url to last_modified in db
        url_to_ids = {} ## mapping of url to guid in db


        HOExtraAlias1 = aliased(HOExtra)
        HOExtraAlias2 = aliased(HOExtra)
        query = model.Session.query(HarvestObject.guid, HarvestObject.package_id, HOExtraAlias1.value, HOExtraAlias2.value).\
                                    join(HOExtraAlias1, HarvestObject.extras).\
                                    join(HOExtraAlias2, HarvestObject.extras).\
                                    filter(HOExtraAlias1.key=='waf_modified_date').\
                                    filter(HOExtraAlias2.key=='waf_location').\
                                    filter(HarvestObject.current==True).\
                                    filter(HarvestObject.harvest_source_id==harvest_job.source.id)


        for guid, package_id, modified_date, url in query:
            url_to_modified_db[url] = modified_date
            url_to_ids[url] = (guid, package_id)

        ######  Get current list of records from source ######

        url_to_modified_harvest = {} ## mapping of url to last_modified in harvest
        try:
            for url, modified_date in _extract_waf(content,source_url,scraper):
                url_to_modified_harvest[url] = modified_date
        except Exception,e:
            msg = 'Error extracting URLs from %s, error was %s' % (source_url, e)
            self._save_gather_error(msg,harvest_job)
            return None

        ######  Compare source and db ######

        harvest_locations = set(url_to_modified_harvest.keys())
        old_locations = set(url_to_modified_db.keys())

        new = harvest_locations - old_locations
        delete = old_locations - harvest_locations
        possible_changes = old_locations & harvest_locations
        change = []

        for item in possible_changes:
            if (not url_to_modified_harvest[item] or not url_to_modified_db[item] #if there is no date assume change
                or url_to_modified_harvest[item] > url_to_modified_db[item]):
                change.append(item)

        def create_extras(url, date, status):
            extras = [HOExtra(key='waf_modified_date', value=date),
                      HOExtra(key='waf_location', value=url),
                      HOExtra(key='status', value=status)]
            if collection_package_id:
                extras.append(
                    HOExtra(key='collection_package_id',
                            value=collection_package_id)
                )
            return extras


        ids = []
        for location in new:
            guid=hashlib.md5(location.encode('utf8','ignore')).hexdigest()
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras(location,
                                                     url_to_modified_harvest[location],
                                                     'new'),
                                guid=guid
                               )
            obj.save()
            ids.append(obj.id)

        for location in change:
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras(location,
                                                     url_to_modified_harvest[location],
                                                     'change'),
                                guid=url_to_ids[location][0],
                                package_id=url_to_ids[location][1],
                               )
            obj.save()
            ids.append(obj.id)

        for location in delete:
            obj = HarvestObject(job=harvest_job,
                                extras=create_extras('','', 'delete'),
                                guid=url_to_ids[location][0],
                                package_id=url_to_ids[location][1],
                               )
            model.Session.query(HarvestObject).\
                  filter_by(guid=url_to_ids[location][0]).\
                  update({'current': False}, False)

            obj.save()
            ids.append(obj.id)

        if len(ids) > 0:
            log.debug('{0} objects sent to the next stage: {1} new, {2} change, {3} delete'.format(
                len(ids), len(new), len(change), len(delete)))
            return ids
        else:
            self._save_gather_error('No records to change',
                                     harvest_job)
            return []

    def fetch_stage(self, harvest_object):

        # Check harvest object status
        status = self._get_object_extra(harvest_object,'status')

        if status == 'delete':
            # No need to fetch anything, just pass to the import stage
            return True

        # We need to fetch the remote document

        # Get location
        url = self._get_object_extra(harvest_object, 'waf_location')
        if not url:
            self._save_object_error(
                    'No location defined for object {0}'.format(harvest_object.id),
                    harvest_object)
            return False

        # Get contents
        try:
            content = self._get_content_as_unicode(url)
        except Exception, e:
            msg = 'Could not harvest WAF link {0}: {1}'.format(url, e)
            self._save_object_error(msg, harvest_object)
            return False

        # Check if it is an ISO document
        document_format = guess_standard(content)
        if document_format == 'iso':
            harvest_object.content = content
            harvest_object.save()
        else:
            extra = HOExtra(
                    object=harvest_object,
                    key='original_document',
                    value=content)
            extra.save()

            extra = HOExtra(
                    object=harvest_object,
                    key='original_format',
                    value=document_format)
            extra.save()

        return True


apache  = parse.SkipTo(parse.CaselessLiteral("<a href="), include=True).suppress() \
        + parse.quotedString.setParseAction(parse.removeQuotes).setResultsName('url') \
        + parse.SkipTo("</a>", include=True).suppress() \
        + parse.Optional(parse.Literal('</td><td align="right">')).suppress() \
        + parse.Optional(parse.Combine(
            parse.Word(parse.alphanums+'-') +
            parse.Word(parse.alphanums+':')
        ,adjacent=False, joinString=' ').setResultsName('date')
        )

iis =      parse.SkipTo("<br>").suppress() \
         + parse.OneOrMore("<br>").suppress() \
         + parse.Optional(parse.Combine(
           parse.Word(parse.alphanums+'/') +
           parse.Word(parse.alphanums+':') +
           parse.Word(parse.alphas)
         , adjacent=False, joinString=' ').setResultsName('date')
         ) \
         + parse.Word(parse.nums).suppress() \
         + parse.Literal('<A HREF=').suppress() \
         + parse.quotedString.setParseAction(parse.removeQuotes).setResultsName('url')

other = parse.SkipTo(parse.CaselessLiteral("<a href="), include=True).suppress() \
        + parse.quotedString.setParseAction(parse.removeQuotes).setResultsName('url')


scrapers = {'apache': parse.OneOrMore(parse.Group(apache)),
            'other': parse.OneOrMore(parse.Group(other)),
            'iis': parse.OneOrMore(parse.Group(iis))}

def _get_scraper(server):
    if not server or 'apache' in server.lower():
        return 'apache'
    if server == 'Microsoft-IIS/7.5':
        return 'iis'
    else:
        return 'other'

def _extract_waf(content, base_url, scraper, results = None, depth=0):
    if results is None:
        results = []

    base_url = base_url.rstrip('/').split('/')
    if 'index' in base_url[-1]:
        base_url.pop()
    base_url = '/'.join(base_url)
    base_url += '/'

    try:
        parsed = scrapers[scraper].parseString(content)
    except parse.ParseException:
        parsed = scrapers['other'].parseString(content)

    for record in parsed:
        url = record.url
        if not url:
            continue
        if url.startswith('_'):
            continue
        if '?' in url:
            continue
        if '#' in url:
            continue
        if 'mailto:' in url:
            continue
        if '..' not in url and url[0] != '/' and url[-1] == '/':
            new_depth = depth + 1
            if depth > 10:
                log.info('Max WAF depth reached')
                continue
            new_url = urljoin(base_url, url)
            if not new_url.startswith(base_url):
                continue
            log.debug('WAF new_url: %s', new_url)
            try:
                response = requests.get(new_url)
                content = response.content
            except Exception, e:
                print str(e)
                continue
            _extract_waf(content, new_url, scraper, results, new_depth)
            continue
        if not url.endswith('.xml'):
            continue
        date = record.date
        if date:
            try:
                date = str(dateutil.parser.parse(date))
            except Exception, e:
                raise
                date = None
        results.append((urljoin(base_url, record.url), date))

    return results

