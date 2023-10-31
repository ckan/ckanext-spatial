import logging
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


def normalize_bbox(bbox_values):
    """
    Ensures a bbox is expressed in a standard dict

    bbox_values may be:
           a string: "-4.96,55.70,-3.78,56.43"
           or a list [-4.96, 55.70, -3.78, 56.43]
           or a list of strings ["-4.96", "55.70", "-3.78", "56.43"]

    ordered as MinX, MinY, MaxX, MaxY.

    Returns a dict with the keys:

       {
            "minx": -4.96,
            "miny": 55.70,
            "maxx": -3.78,
            "maxy": 56.43
        }

    If there are any problems parsing the input it returns None.
    """

    if isinstance(bbox_values, str):
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


def fit_bbox(bbox_dict):
    """
    Ensures that all coordinates in a bounding box
    fall within -180, -90, 180, 90 degrees

    Accepts a dict with the following keys:

       {
            "minx": -4.96,
            "miny": 55.70,
            "maxx": -3.78,
            "maxy": 56.43
        }

    """

    def _adjust_longitude(value):
        if value < -180 or value > 180:
            value = value % 360
            if value < -180:
                value = 360 + value
            elif value > 180:
                value = -360 + value
        return value

    def _adjust_latitude(value):
        if value < -90 or value > 90:
            value = value % 180
            if value < -90:
                value = 180 + value
            elif value > 90:
                value = -180 + value
        return value

    return {
        "minx": _adjust_longitude(bbox_dict["minx"]),
        "maxx": _adjust_longitude(bbox_dict["maxx"]),
        "miny": _adjust_latitude(bbox_dict["miny"]),
        "maxy": _adjust_latitude(bbox_dict["maxy"]),
    }


def fit_linear_ring(lr):

    bbox = {
        "minx": lr[0][0],
        "maxx": lr[2][0],
        "miny": lr[0][1],
        "maxy": lr[2][1],
    }

    bbox = fit_bbox(bbox)

    return [
        (bbox["minx"], bbox["maxy"]),
        (bbox["minx"], bbox["miny"]),
        (bbox["maxx"], bbox["miny"]),
        (bbox["maxx"], bbox["maxy"]),
        (bbox["minx"], bbox["maxy"]),
    ]
