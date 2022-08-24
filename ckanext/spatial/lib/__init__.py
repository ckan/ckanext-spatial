import logging
import six
import ckantoolkit as tk

config = tk.config

log = logging.getLogger(__name__)


def get_srid(crs):
    """Returns the SRID for the provided CRS definition
    The CRS can be defined in the following formats
    - urn:ogc:def:crs:EPSG::4326
    - EPSG:4326
    - 4326
    """

    if ":" in crs:
        crs = crs.split(":")
        srid = crs[len(crs) - 1]
    else:
        srid = crs

    return int(srid)


def validate_bbox(bbox_values):
    """
    Ensures a bbox is expressed in a standard dict.

    bbox_values may be:
           a string: "-4.96,55.70,-3.78,56.43"
           or a list [-4.96, 55.70, -3.78, 56.43]
           or a list of strings ["-4.96", "55.70", "-3.78", "56.43"]
    and returns a dict:
           {'minx': -4.96,
            'miny': 55.70,
            'maxx': -3.78,
            'maxy': 56.43}

    Any problems and it returns None.
    """

    if isinstance(bbox_values, six.string_types):
        bbox_values = bbox_values.split(",")

    if len(bbox_values) != 4:
        return None

    try:
        bbox = {}
        bbox["minx"] = float(bbox_values[0])
        bbox["miny"] = float(bbox_values[1])
        bbox["maxx"] = float(bbox_values[2])
        bbox["maxy"] = float(bbox_values[3])
    except ValueError:
        return None

    return bbox
