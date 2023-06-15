from ckanext.spatial.lib import normalize_bbox, fit_bbox


bbox_dict = {"minx": -4.96, "miny": 55.70, "maxx": -3.78, "maxy": 56.43}


def test_string():
    res = normalize_bbox("-4.96,55.70,-3.78,56.43")
    assert res == bbox_dict


def test_list():
    res = normalize_bbox([-4.96, 55.70, -3.78, 56.43])
    assert res == bbox_dict


def test_list_of_strings():
    res = normalize_bbox(["-4.96", "55.70", "-3.78", "56.43"])
    assert res == bbox_dict


def test_bad():
    res = normalize_bbox([-4.96, 55.70, -3.78])
    assert res is None


def test_bad_2():
    res = normalize_bbox("random")
    assert res is None


def test_fit_within_bounds():

    assert fit_bbox(bbox_dict) == bbox_dict


def test_fit_out_of_bounds():

    bbox_dict = {"minx": -185, "miny": -95, "maxx": 195, "maxy": 95}
    assert fit_bbox(bbox_dict) == {
        "minx": 175,
        "miny": 85,
        "maxx": -165,
        "maxy": -85,
    }
