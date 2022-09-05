# -*- coding: utf-8 -*-

import pytest

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


@pytest.mark.usefixtures("clean_db", "clean_index", "harvest_setup")
@pytest.mark.ckan_config("ckanext.spatial.search_backend", "solr")
class TestBBoxSearch(SpatialTestBase):
    def test_spatial_query(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_outside_bbox(self):

        factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-10,-20,10,20"}
        )

        assert result["count"] == 0

    def test_spatial_query_wrong_bbox(self):
        with pytest.raises(SearchError):
            helpers.call_action(
                "package_search",
                extras={"ext_bbox": "-10,-20,10,a"},
            )

    def test_spatial_real_multipolygon_inside_extent_no_intersect(self):
        """
        Testing this scenario, will return a result as the whole extent of
        the two polygons was indexed:

                   xxxxxxxx
                xxx       xx             xxxx
                x Polygon 1 x             x   xxxx
                x        xxx            xx      xx
                x       xx              x        xx
                 xxxxxxxx              xx         xxx
                     ┌────────┐     xxxx             x
                     │ Search │    xx                xx
                     │  BBox  │   xx                  x
                     │        │   x     Polygon 2    xx
                     └────────┘  xx                  x
                                xx                xxxx
                                x            xxxxx
                                x        xxxx
                                xxxx  xxxx
                                   xxx

        """
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/hawaii.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-156.570,19.959,-155.960,20.444"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_polygon_split_across_antimeridian(self):
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/chukot.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "175,61,179,64"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_polygon_split_across_antimeridian_outside_bbox(self):
        """
        This test passes because as the geometry passes the antemeridian, the
        extent generated to be index is (-180, miny, 180, maxy). Sites needing to
        deal with this scenario should use the `solr-spatial-field` backend.
        See ``TestSpatialFieldSearch.test_spatial_polygon_split_across_antimeridian_outside_bbox``
        """
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/chukot.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "0,61,15,64"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_nz(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_nz_wrap(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-203,-54,-167,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio_wrap(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "258,37,281,51"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]


@pytest.mark.usefixtures("clean_db", "clean_index", "harvest_setup")
@pytest.mark.ckan_config("ckanext.spatial.search_backend", "solr-spatial-field")
class TestSpatialFieldSearch(SpatialTestBase):
    def test_spatial_query_point(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_polygon(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["polygon"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_real_polygon(self):
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/altafulla.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_real_multipolygon(self):
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/hawaii.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_real_multipolygon_inside_extent_no_intersect(self):
        """
        Testing this scenario, should not return results:

                   xxxxxxxx
                xxx       xx               xxxx
                x Polygon 1 x             x   xxxx
                x        xxx            xx      xx
                x       xx              x        xx
                 xxxxxxxx              xx         xxx
                     ┌────────┐     xxxx             x
                     │ Search │    xx                xx
                     │  BBox  │   xx                  x
                     │        │   x     Polygon 2    xx
                     └────────┘  xx                  x
                                xx                xxxx
                                x            xxxxx
                                x        xxxx
                                xxxx  xxxx
                                   xxx

        """
        factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/hawaii.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-156.570,19.959,-155.960,20.444"}
        )

        assert result["count"] == 0

    def test_spatial_polygon_holes(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["polygon_holes"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_multipolygon(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["multipolygon"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )
        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_outside_bbox(self):

        factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-10,-20,10,20"}
        )

        assert result["count"] == 0

    def test_spatial_query_wrong_bbox(self):
        with pytest.raises(SearchError):
            helpers.call_action(
                "package_search",
                extras={"ext_bbox": "-10,-20,10,a"},
            )

    def test_spatial_query_nz(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_nz_wrap(self):
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-203,-54,-167,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_ohio_wrap(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "258,37,281,51"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_dateline_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["dateline2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_polygon_split_across_antimeridian(self):
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/chukot.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "175,61,179,64"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_polygon_split_across_antimeridian_outside_bbox(self):
        factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": self.read_file("data/chukot.geojson")
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "0,61,15,64"}
        )

        assert result["count"] == 0
