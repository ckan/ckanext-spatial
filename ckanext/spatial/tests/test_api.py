import pytest

from ckan.model import Session
from ckan.lib.search import SearchError

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.spatial.tests.base import SpatialTestBase

extents = {
    "nz": '{"type":"Polygon","coordinates":[[[174,-38],[176,-38],[176,-40],[174,-40],[174,-38]]]}',
    "ohio": '{"type": "Polygon","coordinates": [[[-84,38],[-84,40],[-80,42],[-80,38],[-84,38]]]}',
    "dateline": '{"type":"Polygon","coordinates":[[[169,70],[169,60],[192,60],[192,70],[169,70]]]}',
    "dateline2": '{"type":"Polygon","coordinates":[[[170,60],[-170,60],[-170,70],[170,70],[170,60]]]}',
}


@pytest.mark.usefixtures("clean_db")
class TestAction(SpatialTestBase):
    def test_spatial_query(self):
        dataset = factories.Dataset(
            extras=[
                {"key": "spatial", "value": self.geojson_examples["point"]}
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_outside_bbox(self):

        factories.Dataset(
            extras=[
                {"key": "spatial", "value": self.geojson_examples["point"]}
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-10,-20,10,20"}
        )

        assert(result["count"] == 0)

    def test_spatial_query_wrong_bbox(self):
        with pytest.raises(SearchError):
            helpers.call_action(
                "package_search",
                extras={"ext_bbox": "-10,-20,10,a"},
            )

    def test_spatial_query_nz(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["nz"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_nz_wrap(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["nz"]}]
        )
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-203,-54,-167,-28"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_ohio(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_ohio_wrap(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "258,37,281,51"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_dateline_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_dateline_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_dateline_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])

    def test_spatial_query_dateline_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert(result["count"] == 1)
        assert(result["results"][0]["id"] == dataset["id"])


@pytest.mark.usefixtures("clean_db")
class TestHarvestedMetadataAPI(SpatialTestBase):
    def test_api(self, app):
        try:
            from ckanext.harvest.model import (
                HarvestObject,
                HarvestJob,
                HarvestSource,
                HarvestObjectExtra,
            )
        except ImportError:
            raise pytest.skip(
                "The harvester extension is needed for these tests")

        content1 = "<xml>Content 1</xml>"
        ho1 = HarvestObject(
            guid="test-ho-1",
            job=HarvestJob(source=HarvestSource(url="http://", type="xx")),
            content=content1,
        )

        content2 = "<xml>Content 2</xml>"
        original_content2 = "<xml>Original Content 2</xml>"
        ho2 = HarvestObject(
            guid="test-ho-2",
            job=HarvestJob(source=HarvestSource(url="http://", type="xx")),
            content=content2,
        )

        hoe = HarvestObjectExtra(
            key="original_document", value=original_content2, object=ho2
        )

        Session.add(ho1)
        Session.add(ho2)
        Session.add(hoe)
        Session.commit()

        object_id_1 = ho1.id
        object_id_2 = ho2.id

        # Access object content
        url = "/harvest/object/{0}".format(object_id_1)
        r = app.get(url, status=200)
        assert(
            r.headers["Content-Type"] == "application/xml; charset=utf-8"
        )
        assert(
            r.body ==
            '<?xml version="1.0" encoding="UTF-8"?>\n<xml>Content 1</xml>'
        )

        # Access original content in object extra (if present)
        url = "/harvest/object/{0}/original".format(object_id_1)
        r = app.get(url, status=404)

        url = "/harvest/object/{0}/original".format(object_id_2)
        r = app.get(url, status=200)
        assert(
            r.headers["Content-Type"] == "application/xml; charset=utf-8"
        )
        assert(
            r.body ==
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + "<xml>Original Content 2</xml>"
        )
