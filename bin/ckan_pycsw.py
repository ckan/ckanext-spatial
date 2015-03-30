import sys
import logging
import datetime
import io
##Needed for the debugging code bellow
#import codecs

import requests
from lxml import etree
from jinja2 import Environment, FileSystemLoader

from pycsw import metadata, repository, util
import pycsw.config
import pycsw.admin

logging.basicConfig(format='%(message)s', level=logging.INFO)

log = logging.getLogger(__name__)

def to_date(unixtime):
    """Convert unix time to YYYY-MM-DD"""
    try:
        return datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d')
    except ValueError:
        return '-1'

def keyword_list(value):
    """Ensure keywords are treated as lists"""
    if isinstance(value, list):  # list already
        return value
    else:  # csv string
        return value.split(',')

def setup_db(pycsw_config):
    """Setup database tables and indexes"""

    from sqlalchemy import Boolean, Column, Text

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table', 'records')

    ckan_columns = [
        Column('ckan_id', Text, index=True),
        Column('ckan_modified', Text),
        Column('ckan_collection', Boolean),
    ]

    pycsw.admin.setup_db(database,
        table_name, '',
        create_plpythonu_functions=False,
        extra_columns=ckan_columns)


def set_keywords(pycsw_config_file, pycsw_config, ckan_url, limit=20):
    """set pycsw service metadata keywords from top limit CKAN tags"""

    ckan_url = ckan_url or pycsw_config.get('defaults', 'ckan_url')
    ckan_url = ckan_url.rstrip('/') + '/'

    log.info('Fetching tags from %s', ckan_url)
    url = ckan_url + 'api/tag_counts'
    response = requests.get(url)
    tags = response.json()

    log.info('Deriving top %d tags', limit)
    # uniquify and sort by top limit
    tags_unique = [list(x) for x in set(tuple(x) for x in tags)]
    tags_sorted = sorted(tags_unique, key=lambda x: x[1], reverse=1)[0:limit]
    keywords = ','.join('%s' % tn[0] for tn in tags_sorted)

    log.info('Setting tags in pycsw configuration file %s', pycsw_config_file)
    pycsw_config.set('metadata:main', 'identification_keywords', keywords)
    with open(pycsw_config_file, 'wb') as configfile:
        pycsw_config.write(configfile)


def load(pycsw_config, ckan_url):

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table', 'records')

    context = pycsw.config.StaticContext()
    repo = repository.Repository(database, context, table=table_name)

    log.info('Started gathering CKAN datasets identifiers: {0}'.format(str(datetime.datetime.now())))

    ckan_url = ckan_url or pycsw_config.get('defaults', 'ckan_url')
    ckan_url = ckan_url.rstrip('/') + '/'
    query = 'api/search/dataset?qjson={"fl":"id,metadata_modified,extras_harvest_object_id,extras_source_datajson_identifier,extras_metadata_source,extras_collection_package_id", "q":"harvest_object_id:[\\"\\" TO *]", "limit":1000, "start":%s}'

    start = 0

    gathered_records = {}

    while True:
        url = ckan_url + query % start

        response = requests.get(url)
        listing = response.json()
        if not isinstance(listing, dict):
            raise RuntimeError, 'Wrong API response: %s' % listing
        results = listing.get('results')
        if not results:
            break
        for result in results:
            gathered_records[result['id']] = {
                'metadata_modified': result['metadata_modified'],
                'harvest_object_id': result['extras']['harvest_object_id'],
                'source': result['extras'].get('metadata_source')
            }
            is_collection = True
            if 'collection_package_id' in result['extras']:
                is_collection = False
                gathered_records[result['id']]['collection_package_id'] = \
                    result['extras']['collection_package_id']

            gathered_records[result['id']]['ckan_collection'] = is_collection
            if 'source_datajson_identifier' in result['extras']:
                gathered_records[result['id']]['source'] = 'datajson'

        start = start + 1000
        log.debug('Gathered %s' % start)

    log.info('Gather finished ({0} datasets): {1}'.format(
        len(gathered_records.keys()),
        str(datetime.datetime.now())))

    existing_records = {}

    query = repo.session.query(repo.dataset.ckan_id, repo.dataset.ckan_modified)
    for row in query:
        existing_records[row[0]] = row[1]
    repo.session.close()

    new = set(gathered_records) - set(existing_records)
    deleted = set(existing_records) - set(gathered_records)
    changed = set()

    for key in set(gathered_records) & set(existing_records):
        if gathered_records[key]['metadata_modified'] > existing_records[key]:
            changed.add(key)

    for ckan_id in deleted:
        try:
            repo.session.begin()
            repo.session.query(repo.dataset.ckan_id).filter_by(
            ckan_id=ckan_id).delete()
            log.info('Deleted %s' % ckan_id)
            repo.session.commit()
        except Exception, err:
            repo.session.rollback()
            raise

    for ckan_id in new:
        ckan_info = gathered_records[ckan_id]
        record = get_record(context, repo, ckan_url, ckan_id, ckan_info)
        if not record:
            log.info('Skipped record %s' % ckan_id)
            continue
        try:
            repo.insert(record, 'local', util.get_today_and_now())
            log.info('Inserted %s' % ckan_id)
        except Exception, err:
            log.error('ERROR: not inserted %s Error:%s' % (ckan_id, err))

    for ckan_id in changed:
        ckan_info = gathered_records[ckan_id]
        record = get_record(context, repo, ckan_url, ckan_id, ckan_info)
        if not record:
            log.info('Skipped record %s' % ckan_id)
            continue
        update_dict = dict([(getattr(repo.dataset, key),
        getattr(record, key)) \
        for key in record.__dict__.keys() if key != '_sa_instance_state'])
        try:
            repo.session.begin()
            repo.session.query(repo.dataset).filter_by(
            ckan_id=ckan_id).update(update_dict)
            repo.session.commit()
            log.info('Changed %s' % ckan_id)
        except Exception, err:
            repo.session.rollback()
            raise RuntimeError, 'ERROR: %s' % str(err)


def clear(pycsw_config):

    from sqlalchemy import create_engine, MetaData, Table

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table', 'records')

    log.debug('Creating engine')
    engine = create_engine(database)
    records = Table(table_name, MetaData(engine))
    records.delete().execute()
    log.info('Table cleared')


def get_record(context, repo, ckan_url, ckan_id, ckan_info):

    query = ckan_url + 'harvest/object/%s'
    url = query % ckan_info['harvest_object_id']
    log.info('Fetching %s' % url)
    response = requests.get(url)

    if not response.ok:
        log.error('Could not get Harvest object for id %s (%d: %s)',
                  ckan_id, response.status_code, response.reason)
        return

    if ckan_info['source'] in ['arcgis', 'datajson']:  # convert json to iso
        result = response.json()
        tmpldir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               '..',
                               'ckanext/spatial/templates/ckanext/spatial')
        env = Environment(loader=FileSystemLoader(tmpldir))
 
        if ckan_info['source'] == 'arcgis':
            log.info('ArcGIS detected. Converting ArcGIS JSON to ISO XML: %s' % ckan_id)
            env.filters['to_date'] = to_date
            tmpl = 'arcgisjson2iso.xml'
        else:
            log.info('Open Data JSON detected. Converting to ISO XML: %s' % ckan_id)
            env.filters['keyword_list'] = keyword_list
            tmpl = 'datajson2iso.xml'

        template = env.get_template(tmpl)
        content = template.render(json=result)
        
        ##Some debugging code to test by writing xml to a hardcoded folder
        #outfile = codecs.open("/root/json_xml/%s.xml" % ckan_id, "w", "utf-8")
        #outfile.write(content)
        #outfile.close()
        #return

    else:  # harvested ISO XML
        content = response.content

    # from here we have an ISO document no matter what
    try:
        try:
            log.debug('parsing XML as is')
            xml = etree.parse(io.BytesIO(content))
        except:
            log.debug('parsing XML with .encode("utf8")')
            xml = etree.parse(io.BytesIO(content.encode("utf8")))
    except Exception, err:
        log.error('Could not pass xml doc from %s, Error: %s' % (ckan_id, err))
        return

    try:
        log.debug('Parsing ISO XML')
        record = metadata.parse_record(context, xml, repo)[0]
        if not record.identifier:  # force id into ISO XML
            log.info('gmd:fileIdentifier is empty. Inserting id %s' % ckan_id)

            record.identifier = ckan_id

            gmd_ns = 'http://www.isotc211.org/2005/gmd'
            gco_ns = 'http://www.isotc211.org/2005/gco'

            xname = xml.find('{%s}fileIdentifier' % gmd_ns)
            if xname is None:  # doesn't exist, insert it
                log.debug('Inserting new gmd:fileIdentifier')
                fileid = etree.Element('{%s}fileIdentifier' % gmd_ns)
                etree.SubElement(fileid, '{%s}CharacterString' % gco_ns).text = ckan_id
                xml.insert(0, fileid)
            else:  # gmd:fileIdentifier exists, check for gco:CharacterString
                log.debug('Updating')
                value = xname.find('{%s}CharacterString' % gco_ns)
                if value is None:
                    log.debug('missing gco:CharacterString')
                    etree.SubElement(xname, '{%s}CharacterString' % gco_ns).text = ckan_id
                else:
                    log.debug('empty gco:CharacterString')
                    value.text = ckan_id
            record.xml = etree.tostring(xml)

    except Exception, err:
        log.error('Could not extract metadata from %s, Error: %s' % (ckan_id, err))
        return

    record.ckan_id = ckan_id
    record.ckan_modified = ckan_info['metadata_modified']
    record.ckan_collection = ckan_info['ckan_collection']
    if 'collection_package_id' in ckan_info:
        record.parentidentifier = ckan_info['collection_package_id']

    return record


usage='''
Manages the CKAN-pycsw integration

    python ckan-pycsw.py setup [-p]
        Setups the necessary pycsw table on the db.

    python ckan-pycsw.py set_keywords [-p] -u
        Sets pycsw server metadata keywords from CKAN site tag list.

    python ckan-pycsw.py load [-p] -u
        Loads CKAN datasets as records into the pycsw db.

    python ckan-pycsw.py clear [-p]
        Removes all records from the pycsw table.

All commands require the pycsw configuration file. By default it will try
to find a file called 'default.cfg' in the same directory, but you'll
probably need to provide the actual location via the -p option:

    paster ckan-pycsw setup -p /etc/ckan/default/pycsw.cfg

The load command requires a CKAN URL from where the datasets will be pulled:

    paster ckan-pycsw load -p /etc/ckan/default/pycsw.cfg -u http://localhost

'''

def _load_config(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise AssertionError('pycsw config file {0} does not exist.'.format(abs_path))

    config = SafeConfigParser()
    config.read(abs_path)

    return config



import os
import argparse
from ConfigParser import SafeConfigParser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='\n'.split(usage)[0],
        usage=usage)
    parser.add_argument('command',
         help='Command to perform')

    parser.add_argument('-p', '--pycsw_config',
         action='store', default='default.cfg',
         help='pycsw config file to use.')

    parser.add_argument('-u', '--ckan_url',
         action='store',
         help='CKAN instance to import the datasets from.')

    if len(sys.argv) <= 1:
        parser.print_usage()
        sys.exit(1)

    arg = parser.parse_args()
    pycsw_config = _load_config(arg.pycsw_config)

    if arg.command == 'setup':
        setup_db(pycsw_config)
    elif arg.command in ['load', 'set_keywords']:
        if not arg.ckan_url:
            raise AssertionError('You need to provide a CKAN URL with -u or --ckan_url')
        ckan_url = arg.ckan_url.rstrip('/') + '/'
        if arg.command == 'load':
            load(pycsw_config, ckan_url)
        else:
            set_keywords(arg.pycsw_config, pycsw_config, ckan_url)
    elif arg.command == 'clear':
        clear(pycsw_config)
    else:
        print 'Unknown command {0}'.format(arg.command)
        sys.exit(1)

