import sys
import logging
import datetime
import io

import requests
from lxml import etree

from pycsw import metadata, repository, util
import pycsw.config

logging.basicConfig(format='%(message)s', level=logging.INFO)

log = logging.getLogger(__name__)

def setup_db(pycsw_config):
    """Setup database tables and indexes"""
    from sqlalchemy import Column, create_engine, Integer, MetaData, \
        Table, Text

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table', 'records')

    log.debug('Creating engine')
    engine = create_engine(database)

    mdata = MetaData(engine)

    log.info('Creating table %s', table_name)
    records = Table(
        table_name, mdata,
        # core; nothing happens without these
        Column('identifier', Text, primary_key=True),
        Column('typename', Text,
               default='csw:Record', nullable=False, index=True),
        Column('schema', Text,
               default='http://www.opengis.net/cat/csw/2.0.2', nullable=False,
               index=True),
        Column('mdsource', Text, default='local', nullable=False,
               index=True),
        Column('insert_date', Text, nullable=False, index=True),
        Column('xml', Text, nullable=False),
        Column('anytext', Text, nullable=False),
        Column('language', Text, index=True),

        # identification
        Column('type', Text, index=True),
        Column('title', Text, index=True),
        Column('title_alternate', Text, index=True),
        Column('abstract', Text),
        Column('keywords', Text),
        Column('keywordstype', Text, index=True),
        Column('parentidentifier', Text, index=True),
        Column('relation', Text, index=True),
        Column('time_begin', Text, index=True),
        Column('time_end', Text, index=True),
        Column('topicategory', Text, index=True),
        Column('resourcelanguage', Text, index=True),

        # attribution
        Column('creator', Text, index=True),
        Column('publisher', Text, index=True),
        Column('contributor', Text, index=True),
        Column('organization', Text, index=True),

        # security
        Column('securityconstraints', Text),
        Column('accessconstraints', Text),
        Column('otherconstraints', Text),

        # date
        Column('date', Text, index=True),
        Column('date_revision', Text, index=True),
        Column('date_creation', Text, index=True),
        Column('date_publication', Text, index=True),
        Column('date_modified', Text, index=True),

        Column('format', Text, index=True),
        Column('source', Text, index=True),

        # geospatial
        Column('crs', Text, index=True),
        Column('geodescode', Text, index=True),
        Column('denominator', Integer, index=True),
        Column('distancevalue', Integer, index=True),
        Column('distanceuom', Text, index=True),
        Column('wkt_geometry', Text),

        # service
        Column('servicetype', Text, index=True),
        Column('servicetypeversion', Text, index=True),
        Column('operation', Text, index=True),
        Column('couplingtype', Text, index=True),
        Column('operateson', Text, index=True),
        Column('operatesonidentifier', Text, index=True),
        Column('operatesoname', Text, index=True),

        # additional
        Column('degree', Text, index=True),
        Column('classification', Text, index=True),
        Column('conditionapplyingtoaccessanduse', Text, index=True),
        Column('lineage', Text, index=True),
        Column('responsiblepartyrole', Text, index=True),
        Column('specificationtitle', Text, index=True),
        Column('specificationdate', Text, index=True),
        Column('specificationdatetype', Text, index=True),

        # distribution
        # links: format "name,description,protocol,url[^,,,[^,,,]]"
        Column('links', Text, index=True),

        Column('ckan_id', Text, index=True),
        Column('ckan_modified', Text),
    )
    records.create()


def load(pycsw_config, ckan_url):

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table', 'records')

    context = pycsw.config.StaticContext()
    repo = repository.Repository(database, context, table=table_name)
    ckan_url = ckan_url.lstrip('/') + '/'

    log.info('Started gathering CKAN datasets identifiers: {0}'.format(str(datetime.datetime.now())))

    query = 'api/search/dataset?qjson={"fl":"id,metadata_modified,extras_harvest_object_id,extras_metadata_source", "q":"harvest_object_id:*", "limit":1000, "start":%s}'

    start = 0

    gathered_records = {}

    while True:
        url = ckan_url + query % start

        response = requests.get(url)
        listing = response.json()
        results = listing.get('results')
        if not results:
            break
        for result in results:
            gathered_records[result['id']] = {
                'metadata_modified': result['metadata_modified'],
                'harvest_object_id': result['extras']['harvest_object_id'],
                'source': result['extras'].get('metadata_source')
            }

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
    response = requests.get(url)

    if ckan_info['source'] == 'arcgis':
        return

    try:
        xml = etree.parse(io.BytesIO(response.content))
    except Exception, err:
        log.error('Could not pass xml doc from %s, Error: %s' % (ckan_id, err))
        return

    try:
        record = metadata.parse_record(context, xml, repo)[0]
    except Exception, err:
        log.error('Could not extract metadata from %s, Error: %s' % (ckan_id, err))
        return

    if not record.identifier:
        record.identifier = ckan_id
    record.ckan_id = ckan_id
    record.ckan_modified = ckan_info['metadata_modified']

    return record


usage='''
Manages the CKAN-pycsw integration

    python ckan-pycsw.py setup [-p]
        Setups the necessary pycsw table on the db.

    python ckan-pycsw.py load [-p] -u
        Loads CKAN datasets as records into the pycsw db.

All commands require the pycsw configuration file. By default it will try
to find a file called 'default.cfg' in the same directory, but you'll
probably need to provide the actual location via the -p option:

    paster ckan-pycsw setup -p /etc/pycsw/default.cfg

The load command requires a CKAN URL from where the datasets will be pulled:

    paster ckan-pycsw setup -p /etc/pycsw/default.cfg -u http://localhost

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
         help='Path to pycsw config file')

    parser.add_argument('-u', '--ckan_url',
         action='store',
         help='CKAN URL')

    if len(sys.argv) <= 1:
        parser.print_usage()
        sys.exit(1)

    arg = parser.parse_args()
    pycsw_config = _load_config(arg.pycsw_config)

    if arg.command == 'setup':
        setup_db(pycsw_config)
    elif arg.command == 'load':
        if not arg.ckan_url:
            raise AssertionError('You need to provide a CKAN URL with -u or --ckan_url')
        load(pycsw_config, arg.ckan_url)
    elif arg.command == 'clear':
        clear(pycsw_config)
    else:
        print 'Unknown command {0}'.format(arg.command)
        sys.exit(1)
