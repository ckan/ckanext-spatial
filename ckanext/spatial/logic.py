import logging
import urllib
import json
import ckan.model as model
from ckantoolkit import side_effect_free, get_action
from ckanext.spatial.lib import get_srid, validate_bbox, bbox_query, polygon_query, validate_polygon

log = logging.getLogger(__name__)


def load_json(j):
    try:
        new_val = json.loads(j)
    except Exception:
        new_val = j
    return new_val

@side_effect_free
def spatial_query_geo(context, data_dict):

    srid = get_srid(str(data_dict.get('crs'))) if 'crs' in \
        data_dict else None

    bbox = poly = []
    if 'bbox' in data_dict:
        bbox = validate_bbox(data_dict['bbox'])
    elif 'poly' in data_dict:
        poly_str = urllib.parse.unquote_plus(data_dict['poly'])
        if poly_str.startswith('BOX'):
            bbox = validate_bbox(poly_str[4:-1])
        else:
            poly = validate_polygon(poly_str)
    else:
        return []

    if not (bbox or poly):
        return []

    extents = bbox_query(bbox, srid) if bbox \
        else polygon_query(poly, srid)

    ids = [extent.package_id for extent in extents]
    output = dict(count=len(ids), results=ids)

    return output


@side_effect_free
def spatial_query_geo_package_search(context, data_dict):

    search_params = dict(data_dict)
    search_params.pop('bbox', None)
    search_params.pop('poly', None)
    
    if 'bbox' in data_dict or 'poly' in data_dict:
        ids = spatial_query_geo(context, data_dict)
        results = ids.get('results', [])
        if results:
            search_params['fq'] += '+id:(' + ' OR '.join(results) + ')'

    pkg = get_action('package_search')(data_dict=search_params)
    return pkg
