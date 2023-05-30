from __future__ import print_function

import six
from six.moves.urllib.parse import urljoin
from six.moves import html_parser
import logging
import hashlib

import dateutil.parser
import pyparsing as parse
import requests
from sqlalchemy.orm import aliased
from sqlalchemy.exc import DataError

from ckan import model
from ckan.lib.helpers import json
from ckan.logic import ValidationError, NotFound, get_action

from ckan.plugins.core import SingletonPlugin, implements
from ckantoolkit import config

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra
import ckanext.harvest.queue as queue

from ckanext.spatial.harvesters.waf import WAFHarvester
from ckanext.harvest.queue import get_connection_redis

from lxml import etree

import boto3
from copy import deepcopy
import unicodedata

log = logging.getLogger(__name__)


class DatastreamSitemapHarvester(WAFHarvester, SingletonPlugin):
    '''
    A Harvester for WAF (Web Accessible Folders) containing spatial metadata documents.
    e.g. Apache serving a directory of ISO 19139 files.
    '''

    implements(IHarvester)

    redis_translation_store = 'awsTranslations'
    translation_method_text = "text translated using the Amazon translate service / texte traduit à l'aide du service Amazon translate"

    def info(self):
        return {
            'name': 'datastream_sitemap',
            'title': 'Sitemap Harvester for datastream ISO19115-2',
            'description': 'site map listing datasets urls with avilable iso19115-2 xml'
        }
    
    def translate_string(self, redis_conn, string_to_translate, source_lang='en', target_lang='fr'):
        store_name = '%s_%s_to_%s' % (self.redis_translation_store,source_lang,target_lang)
        # check for string in redis
        redis_trans = redis_conn.hget(store_name,string_to_translate)
        if redis_trans: 
            # replace non-breaking white space
            redis_trans = redis_trans.replace(u'\u00A0',' ')
            log.debug('"%s" found in cache', string_to_translate)
            return redis_trans

        # if not exists, call aws translate
        try:      
            translate = boto3.client(service_name='translate', use_ssl=True)
            aws_trans_obj = translate.translate_text(Text=string_to_translate, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)
            aws_trans = aws_trans_obj.get('TranslatedText')
            # replace non-breaking white space
            aws_trans = aws_trans.replace(u'\u00A0',' ')
            
            # save translation to redis
            if aws_trans:
                log.debug('"%s" saved to cache', string_to_translate)
                redis_conn.hset(store_name, mapping={string_to_translate:aws_trans})
                return aws_trans
        except Exception as e:
              log.error('Could not translate text %s : %e', string_to_translate, e)

        return None

    def get_package_dict(self, iso_values, harvest_object):

        log.debug(" *** in waf_Datastream get_package_dict")
        package_dict = super(DatastreamSitemapHarvester, self).get_package_dict(iso_values, harvest_object)

        # All DataStream datasets have a DOI so we use that to populate the citation
        iso_values["citation"] = '{"fr": "%s", "en": "%s"}' % (iso_values['unique-resource-identifier'], iso_values['unique-resource-identifier'])
        package_dict['unique-resource-identifier-full'] = []
        package_dict['unique-resource-identifier-full'].append({'code': iso_values['unique-resource-identifier']})

        # TODO: determin if we can set EOV to something useful
        if not package_dict.get("eov"):
            package_dict["eov"] = ["other"]

        # call check redis for translation, call Amazon translate if needed and cache results in redis
        redis_conn = get_connection_redis()
       
        # suppress tags in iso_values as we are using keywords
        if iso_values.get('tags'):
            iso_values['tags'] = []

        # Keywords auto translated
        # in some cases there are no keywords at all
        if iso_values.get('keywords'):
            for item in iso_values['keywords']:
                keyword = json.loads(item.get('keyword','{}'))  
                en_string = None  
                fr_string = None    
                if isinstance(keyword, dict):
                    en_string = keyword.get('en')
                    fr_string = keyword.get('fr')
                else:
                    en_string = keyword

                if en_string and not fr_string:
                    en_string = en_string.replace('"','')
                    en_string = unicodedata.normalize("NFKD", en_string)
                    fr_string = self.translate_string(redis_conn, en_string, 'en', 'fr')
                    item['keyword'] = '{"en": "%s", "fr": "%s"}' % (en_string,fr_string)
                    package_dict['keywords_translation_method'] = json.dumps({'en':'', 'fr':'Keyword ' + self.translation_method_text})
                elif fr_string and not en_string:
                    fr_string = fr_string.replace('"','')
                    fr_string = unicodedata.normalize("NFKD", fr_string)
                    en_string = self.translate_string(redis_conn, fr_string, 'fr', 'en')
                    item['keyword'] = '{"en": "%s", "fr": "%s"}' % (en_string,fr_string)
                    package_dict['keywords_translation_method'] = json.dumps({'fr':'', 'en':'Keyword ' + self.translation_method_text})
        else:
            iso_values['keywords'] = [{'keyword': '{"en": "other", "fr": "autre"}', 'type': ''}]

        # Title auto translated
        title = json.loads(package_dict["title"])
        if title.get('en') and not title.get('fr'):
            title['fr'] = self.translate_string(redis_conn, title['en'] , 'en', 'fr')
            package_dict["title"] = json.dumps(title)
            package_dict['title_translation_method'] = json.dumps({'en':'', 'fr':'Title ' + self.translation_method_text})
        elif title.get('fr') and not title.get('en'):
            title['en'] = self.translate_string(redis_conn, title['fr'] , 'fr', 'en')
            package_dict["title"] = json.dumps(title)
            package_dict['title_translation_method'] = json.dumps({'fr':'', 'en':'Title ' + self.translation_method_text})

        # Description auto translated
        notes = json.loads(package_dict["notes"])
        if notes.get('en') and not notes.get('fr'):
            notes['fr'] = self.translate_string(redis_conn, notes['en'] , 'en', 'fr')
            package_dict["notes"] = json.dumps(notes)
            package_dict['notes_translation_method'] = json.dumps({'en':'', 'fr':'Description ' + self.translation_method_text})
        elif notes.get('fr') and not notes.get('en'):
            notes['en'] = self.translate_string(redis_conn, notes['fr'] , 'fr', 'en')
            package_dict["notes"] = json.dumps(notes)
            package_dict['notes_translation_method'] = json.dumps({'fr':'', 'en':'Description ' + self.translation_method_text})

        # Datastream does not provide a download link in there metadata so we are
        # adding their dataset metadata page as a resource instead.
        package_dict['resources'] = [
            {
                'url': iso_values['unique-resource-identifier'],
                'name': "Access DataStream",
                'description': '',
                'resource_locator_protocol': '',
                'resource_locator_function': r'',
            }]


        # End of processing, return the modified package
        return package_dict

    def gather_stage(self,harvest_job,collection_package_id=None):
        log = logging.getLogger(__name__ + '.WAF.gather')
        log.debug('WafHarvester gather_stage for job: %r', harvest_job)

        self.harvest_job = harvest_job

        # Get source URL
        source_url = harvest_job.source.url

        self._set_source_config(harvest_job.source.config)

        # # Get contents
        # try:
        #     response = requests.get(source_url, timeout=60)
        #     response.raise_for_status()
        # except requests.exceptions.RequestException as e:
        #     self._save_gather_error('Unable to get content for URL: %s: %r' % \
        #                                 (source_url, e),harvest_job)
        #     return None
        #
        # content = response.content


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

        # Get contents of sitemap.xml
        # https://datastream.org/dataset/sitemap.xml
        try:
            sitemap_response = requests.get(source_url, timeout=60)
            sitemap_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self._save_gather_error('Unable to get content for URL: %s: %r' % \
                                        (source_url, e),harvest_job)
            return None

        sitemape_content = sitemap_response.text

        # convert xml content to lxml etree
        sitemap_tree = etree.fromstring(str.encode(sitemape_content))

        # using dataset urls, generate url to xml metadata files. aka add .iso19115.xml to end
        url_to_modified_harvest = {} ## mapping of url to last_modified in harvest
        try:
            for url_node in sitemap_tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
                loc_node = url_node.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                last_modified_node = url_node.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
                url = loc_node.text + '.iso19115.xml'
                modified_date = last_modified_node.text
                url_to_modified_harvest[url] = modified_date
        except Exception as e:
            msg = 'Error extracting URLs from %s, error was %r' % (source_url, e)
            self._save_gather_error(msg, harvest_job)
            return None

        ######  Compare source and db ######

        harvest_locations = set(url_to_modified_harvest.keys())
        old_locations = set(url_to_modified_db.keys())

        new = harvest_locations - old_locations
        delete = old_locations - harvest_locations
        possible_changes = old_locations & harvest_locations
        change = []

        for item in possible_changes:
            if (not url_to_modified_harvest[item] or not url_to_modified_db[item]  # if there is no date assume change
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
            if config.get('ckan.harvest.status_mail.all', False):
                self._save_gather_error('No records to change',
                                         harvest_job)
            else:
                log.debug('No records to change')
            return []
