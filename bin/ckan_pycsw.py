import sys
import logging
import datetime
import io
import os
import argparse

from configparser import SafeConfigParser

import requests
from lxml import etree

from pycsw.core import metadata, repository, util
import pycsw.core.config
import pycsw.core.admin

import ckan.plugins.toolkit as tk

logging.basicConfig(format='%(message)s', level=logging.INFO)

log = logging.getLogger(__name__)


def setup_db(pycsw_config):
    """Setup database tables and indexes"""

    if sys.version_info < (3, 0):
        log.info("Python 2 detected: Please upgrade to CKAN 2.9 and python 3")
        return

    from sqlalchemy import Column, Text

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table')

    ckan_columns = [
        Column('ckan_id', Text, index=True),
        Column('ckan_modified', Text),
    ]

    pycsw.core.admin.setup_db(database,
        table_name, '',
        create_plpythonu_functions=False,
        extra_columns=ckan_columns)


def set_keywords(pycsw_config_file, pycsw_config, ckan_url, limit=20):
    """set pycsw service metadata keywords from top limit CKAN tags"""

    if sys.version_info < (3, 0):
        log.info("Python 2 detected:  Please upgrade to CKAN 2.9 and python 3")
        return

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


def _get_gathered_records(ckan_url):
    gathered_records = {}
    limit = 1000
    error_count = start = 0

    log.info('Started gathering CKAN datasets identifiers: {0}'.format(str(datetime.datetime.now())))

    query = 'api/search/dataset?fl=id,metadata_modified,extras_harvest_object_id,' \
            'extras_metadata_source&q=harvest_object_id:[\\\\"\\\\"%20TO%20*]&start={start}&rows={limit}'

    while True:
        try:
            url = ckan_url + query.format(start=start, limit=limit)

            response = requests.get(url)
            listing = response.json()
            if not isinstance(listing, dict):
                raise (RuntimeError, 'Wrong API response: %s' % listing)

            r = listing.get('result')
            results = r.get('results')
            if not results:
                break
            for result in results:
                gathered_records[result['id']] = {
                    'metadata_modified': result['metadata_modified'],
                    'harvest_object_id': result['harvest_object_id'],
                    'source': result.get('metadata_source')
                }
            start = start + limit
            log.debug('Gathered %s' % start)
        except Exception as e:
            log.error("Error gathering: %r", e)
            error_count += 1

    log.info('Gather finished ({0} datasets): {1}'.format(
        len(gathered_records.keys()),
        str(datetime.datetime.now())))

    return gathered_records, error_count


def _get_existing_records(repo):
    existing_records = {}

    query = repo.session.query(repo.dataset.ckan_id, repo.dataset.ckan_modified)
    for row in query:
        existing_records[row[0]] = row[1]
    repo.session.close()

    return existing_records


def _delete_records(deleted, repo, error_count):
    delete_count = 0
    for ckan_id in deleted:
        try:
            repo.session.begin()
            repo.session.query(repo.dataset.ckan_id).filter_by(ckan_id=ckan_id).delete()
            log.info('Deleted %s' % ckan_id)
            repo.session.commit()
            delete_count += 1
        except Exception as err:
            repo.session.rollback()
            error_count += 1

    return delete_count, error_count


def _create_records(new, gathered_records, repo, ckan_url, context, error_count):
    new_count = 0
    for ckan_id in new:
        ckan_info = gathered_records[ckan_id]
        try:
            record = get_record(context, repo, ckan_url, ckan_id, ckan_info)
            if not record:
                log.info('Skipped record %s' % ckan_id)
                continue
            repo.insert(record, 'local', util.get_today_and_now())
            log.info('Inserted %s' % ckan_id)
            new_count += 1
        except Exception as err:
            log.error('ERROR: not inserted %s Error:%s' % (ckan_id, err))
            error_count += 1
    return new_count, error_count


def _update_records(changed, gathered_records, repo, context, error_count):
    change_count = 0
    for ckan_id in changed:
        try:
            ckan_info = gathered_records[ckan_id]
            record = get_record(context, repo, ckan_url, ckan_id, ckan_info)
        except Exception as e:
            log.error("Error: %r", e)
            error_count += 1

        if not record:
            continue
        update_dict = dict(
            [(getattr(repo.dataset, key), getattr(record, key)) \
            for key in record.__dict__.keys() if key != '_sa_instance_state']
        )
        try:
            repo.session.begin()
            repo.session.query(repo.dataset).filter_by(ckan_id=ckan_id).update(update_dict)
            repo.session.commit()
            log.info('Changed %s' % ckan_id)
            change_count += 1
        except Exception as err:
            repo.session.rollback()
            log.error(RuntimeError, 'ERROR: %s' % str(err))
            error_count += 1
    return change_count, error_count


def load(pycsw_config, ckan_url):

    if sys.version_info < (3, 0):
        log.info("Python 2 detected: Please upgrade to CKAN 2.9 and python 3")
        return

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table')

    context = pycsw.core.config.StaticContext()
    repo = repository.Repository(database, context, table=table_name)

    new_count = delete_count = change_count = 0

    gathered_records, error_count = _get_gathered_records(ckan_url)

    existing_records = _get_existing_records(repo)

    new = set(gathered_records) - set(existing_records)
    deleted = set(existing_records) - set(gathered_records)
    changed = set()

    for key in set(gathered_records) & set(existing_records):
        if gathered_records[key]['metadata_modified'] > existing_records[key]:
            changed.add(key)

    delete_count, error_count = _delete_records(deleted, repo, error_count)

    new_count, error_count = _create_records(
        new, gathered_records, ckan_url, repo, context, error_count)

    change_count, error_count = _update_records(
        changed, gathered_records, repo, context, error_count)

    log.info("Loading completed: {gather_count} gathered, {new_count} added, "
             "{change_count} changed, {delete_count} deleted, {error_count} errored".format(
                gather_count=len(gathered_records), new_count=new_count,
                change_count=change_count, delete_count=delete_count,
                error_count=error_count))


def clear(pycsw_config):

    if sys.version_info < (3, 0):
        log.info("Python 2 detected:  Please upgrade to CKAN 2.9 and python 3")
        return

    from sqlalchemy import create_engine, MetaData, Table

    database = pycsw_config.get('repository', 'database')
    table_name = pycsw_config.get('repository', 'table')

    log.debug('Creating engine')
    engine = create_engine(database)
    records = Table(table_name, MetaData(engine))
    records.delete().execute()
    log.info('Table cleared')


def get_record(context, repo, ckan_url, ckan_id, ckan_info):

    if sys.version_info < (3, 0):
        log.info("Python 2 detected: Please upgrade to CKAN 2.9 and python 3")
        return

    query = ckan_url + 'harvest/object/%s'
    url = query % ckan_info['harvest_object_id']
    response = requests.get(url)

    if ckan_info['source'] == 'arcgis':
        return

    try:
        xml = etree.parse(io.BytesIO(response.content))
    except Exception as err:
        log.error('Could not pass xml doc from %s, Error: %s' % (ckan_id, err))
        raise

    try:
        record = metadata.parse_record(context, xml, repo)[0]
    except Exception as err:
        log.error('Could not extract metadata from %s, Error: %s' % (ckan_id, err))
        raise

    if not record.identifier:
        record.identifier = ckan_id
    record.ckan_id = ckan_id
    record.ckan_modified = ckan_info['metadata_modified']

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
        print('Unknown command {0}'.format(arg.command))
        sys.exit(1)
