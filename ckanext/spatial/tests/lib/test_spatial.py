from ckanext.spatial.lib import validate_bbox


class TestValidateBbox(object):
    bbox_dict = {"minx": -4.96, "miny": 55.70, "maxx": -3.78, "maxy": 56.43}

    def test_string(self):
        res = validate_bbox("-4.96,55.70,-3.78,56.43")
        assert res == self.bbox_dict

    def test_list(self):
        res = validate_bbox([-4.96, 55.70, -3.78, 56.43])
        assert res == self.bbox_dict

    def test_bad(self):
        res = validate_bbox([-4.96, 55.70, -3.78])
        assert res is None

    def test_bad_2(self):
        res = validate_bbox("random")
        assert res is None
