import logging

from ckan import plugins as p
from ckan.lib import helpers as h

from ckantoolkit import config

log = logging.getLogger(__name__)

def spatial_widget_expands():
    '''Return the value of the spatial_widget_expands config setting.

    To disable expanding of the spatial widget when drawing search box, add this line to the
    [app:main] section of your CKAN config file::

      ckan.spatial.spatial_widget_expands = False

    Returns ``True`` by default, if the setting is not in the config file.

    :rtype: bool

    '''
    value = config.get('ckan.spatial.spatial_widget_expands', True)
    value = p.toolkit.asbool(value)
    return value

def spatial_default_extent():
    '''Return the value of the ckanext.spatial.default_extent config setting.

    :rtype: text

    '''
    value = config.get('ckanext.spatial.default_extent')
    return value

def get_reference_date(date_str):
    '''
        Gets a reference date extra created by the harvesters and formats it
        nicely for the UI.

        Examples:
            [{"type": "creation", "value": "1977"}, {"type": "revision", "value": "1981-05-15"}]
            [{"type": "publication", "value": "1977"}]
            [{"type": "publication", "value": "NaN-NaN-NaN"}]

        Results
            1977 (creation), May 15, 1981 (revision)
            1977 (publication)
            NaN-NaN-NaN (publication)
    '''
    try:
        out = []
        for date in h.json.loads(date_str):
            value = h.render_datetime(date['value']) or date['value']
            out.append('{0} ({1})'.format(value, date['type']))
        return ', '.join(out)
    except (ValueError, TypeError):
        return date_str


def get_responsible_party(value):
    '''
        Gets a responsible party extra created by the harvesters and formats it
        nicely for the UI.

        Examples:
            [{"name": "Complex Systems Research Center", "roles": ["pointOfContact"]}]
            [{"name": "British Geological Survey", "roles": ["custodian", "pointOfContact"]}, {"name": "Natural England", "roles": ["publisher"]}]

        Results
            Complex Systems Research Center (pointOfContact)
            British Geological Survey (custodian, pointOfContact); Natural England (publisher)
    '''
    formatted = {
        'resourceProvider': p.toolkit._('Resource Provider'),
        'pointOfContact': p.toolkit._('Point of Contact'),
        'principalInvestigator': p.toolkit._('Principal Investigator'),
    }

    try:
        out = []
        parties = h.json.loads(value)
        for party in parties:
            roles = [formatted[role] if role in list(formatted.keys()) else p.toolkit._(role.capitalize()) for role in party['roles']]
            out.append('{0} ({1})'.format(party['name'], ', '.join(roles)))
        return '; '.join(out)
    except (ValueError, TypeError):
        return value


def get_common_map_config():
    '''
        Returns a dict with all configuration options related to the common
        base map (ie those starting with 'ckanext.spatial.common_map.')
    '''
    namespace = 'ckanext.spatial.common_map.'
    return dict([(k.replace(namespace, ''), v) for k, v in config.items() if k.startswith(namespace)])

def spatial_get_map_initial_max_zoom(pkg):
    max_zoom = h.get_pkg_dict_extra(pkg, 'spatial_initial_max_zoom') or \
        pkg.get('spatial_initial_max_zoom') or \
        config.get('ckanext.spatial.initial_max_zoom', 9)
    return max_zoom
