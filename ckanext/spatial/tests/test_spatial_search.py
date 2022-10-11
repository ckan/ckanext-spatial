# -*- coding: utf-8 -*-
import json
import pytest

from ckan.lib.search import SearchError

import ckan.tests.helpers as helpers
import ckan.tests.factories as factories

from ckanext.spatial.tests.base import SpatialTestBase

extents = {
    "nz": """
        {"type":"Polygon",
        "coordinates":[[[174,-38],[176,-38],[176,-40],[174,-40],[174,-38]]]}""",
    "ohio": """
        {"type": "Polygon",
        "coordinates": [[[-84,38],[-84,40],[-80,42],[-80,38],[-84,38]]]}""",
    "antimeridian_bbox": """
        {"type":"Polygon",
        "coordinates":[[[169,70],[169,60],[192,60],[192,70],[169,70]]]}""",
    "antimeridian_bbox_2": """
        {"type":"Polygon",
        "coordinates":[[[170,60],[-170,60],[-170,70],[170,70],[170,60]]]}""",
    "antimeridian_polygon": """
        { "type": "MultiPolygon",
            "coordinates": [ [ [
            [ 181.2, 61.7 ], [ 178.1, 61.4 ],
            [ 176.9, 59.2 ], [ 178.4, 55.2 ],
            [ 188.6, 54.9 ], [ 188.8, 60.2 ],
            [ 181.2, 61.7 ] ] ] ]
        }
    """
}


@pytest.mark.usefixtures("clean_db", "clean_index", "harvest_setup", "with_plugins")
@pytest.mark.ckan_config("ckanext.spatial.search_backend", "solr-bbox")
class TestBBoxSearch(SpatialTestBase):
    def test_spatial_query(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_point(self):
        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": self.geojson_examples["point"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 0

    def test_spatial_query_outside_bbox(self):
        factories.Dataset(
            extras=[{"key": "spatial", "value": extents["ohio"]}]
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

    def test_spatial_query_antimeridian_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox_2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox_2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_geometry_collection(self):
        """ Test a geometry collection """

        # Build a GeometryCollection with all ohio and nz extents
        geometry_collection = {
            'type': 'GeometryCollection',
            'geometries': [
                json.loads(geom) for zone, geom in extents.items() if zone in ['nz', 'ohio']]
        }

        dataset = factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": json.dumps(geometry_collection)
                }
            ]
        )

        # Test that we get the same dataset using two different extents

        # New Zealand
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

        # Ohio
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_sorting_of_bbox_results(self):
        """
        Bounding box based searches support ordering the results spatially. The default
        method used is overlap ratio, ie datasets with geometries that overlap more with
        the input bounding box are returned first. In this case for instance, we would
        expect the results to be ordered as B, D, A, C

          2 ┌────────────┬────────────┐
            │            │            │
            │         xxxxxxxxxxxxx   │
            │   A     x  │        x B │
            │         x  │        x   │
            │         x  │        x   │
          1 ├─────────x──┼────────x───┤
            │         x  │        x   │
            │         xxxxxxxxxxxxx   │
            │            │            │
            │   C        │          D │
            │            │            │
            └────────────┴────────────┘
        0,0              1            2
        """

        dataset_extents = [
            ("Dataset A", (0, 1, 1, 2)),
            ("Dataset B", (1, 1, 2, 2)),
            ("Dataset C", (0, 0, 1, 1)),
            ("Dataset D", (1, 0, 2, 1)),
        ]

        for item in dataset_extents:
            geom = """
                {{"type":"Polygon",
                "coordinates":[[[{xmin},{ymax}],[{xmin},{ymin}],[{xmax},{ymin}],[{xmax},{ymax}],[{xmin},{ymax}]]]}}
            """.format(
                xmin=item[1][0], ymin=item[1][1], xmax=item[1][2], ymax=item[1][3])
            factories.Dataset(
                title=item[0],
                extras=[{"key": "spatial", "value": geom}]
            )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "0.75,0.75,1.75,1.75"}
        )

        assert result["count"] == 4

        assert (
            [d["title"] for d in result["results"]] == [
                "Dataset B", "Dataset D", "Dataset A", "Dataset C"]
        )

    def test_spatial_search_combined_with_other_q(self):
        dataset_extents = [
            ("Dataset A", (0, 1, 1, 2), "rabbit"),
            ("Dataset B", (1, 1, 2, 2), "rabbit"),
            ("Dataset C", (0, 0, 1, 1), "mole"),
            ("Dataset D", (1, 0, 2, 1), "badger"),
        ]

        for item in dataset_extents:
            geom = """
                {{"type":"Polygon",
                "coordinates":[[[{xmin},{ymax}],[{xmin},{ymin}],[{xmax},{ymin}],[{xmax},{ymax}],[{xmin},{ymax}]]]}}
            """.format(
                xmin=item[1][0], ymin=item[1][1], xmax=item[1][2], ymax=item[1][3])
            factories.Dataset(
                title=item[0],
                notes=item[2],
                extras=[{"key": "spatial", "value": geom}]

            )

        result = helpers.call_action(
            "package_search", q="rabbit", extras={"ext_bbox": "0.75,0.75,1.75,1.75"}
        )

        assert result["count"] == 2




@pytest.mark.usefixtures("clean_db", "clean_index", "harvest_setup", "with_plugins")
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

    def test_spatial_query_antimeridian_1(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_2(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "162,54,237,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_3(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox_2"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-197,56,-128,70"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_spatial_query_antimeridian_4(self):

        dataset = factories.Dataset(
            extras=[{"key": "spatial", "value": extents["antimeridian_bbox_2"]}]
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

    def test_spatial_polygon_across_antimeridian_not_indexed(self):
        factories.Dataset(
            extras=[
                {
                    "key": "spatial",
                    "value": extents["antimeridian_polygon"]
                }
            ]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "177.9,55,178.0,59"},
        )

        assert result["count"] == 0

    def test_custom_spatial_query(self, monkeypatch, ckan_config):
        """
            ┌────────────────┐ xxxxxx
            │           xxxxx│xx     xxx
            │         xxx    │       xxx
            │        xx      │      xx
            │     xxxx       │    xxx
            │     x         x│xxxxx
            │      xxx   xxxx│
            │         xxxx   │
            │                │
            └────────────────┘
        """
        dataset = factories.Dataset(extras=[{"key": "spatial", "value": extents["nz"]}])

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "175,-39.5,176.5,-39"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

        monkeypatch.setitem(
            ckan_config,
            "ckanext.spatial.solr_query",
            "{{!field f={spatial_field}}}Contains(ENVELOPE({minx}, {maxx}, {maxy}, {miny}))")

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "175,-39.5,176.5,-39"}
        )

        assert result["count"] == 0

    def test_spatial_search_combined_with_other_q(self):
        dataset_extents = [
            ("Dataset A", (0, 1, 1, 2), "rabbit"),
            ("Dataset B", (1, 1, 2, 2), "rabbit"),
            ("Dataset C", (0, 0, 1, 1), "mole"),
            ("Dataset D", (1, 0, 2, 1), "badger"),
        ]

        for item in dataset_extents:
            geom = """
                {{"type":"Polygon",
                "coordinates":[[[{xmin},{ymax}],[{xmin},{ymin}],[{xmax},{ymin}],[{xmax},{ymax}],[{xmin},{ymax}]]]}}
            """.format(
                xmin=item[1][0], ymin=item[1][1], xmax=item[1][2], ymax=item[1][3])
            factories.Dataset(
                title=item[0],
                notes=item[2],
                extras=[{"key": "spatial", "value": geom}]

            )

        result = helpers.call_action(
            "package_search", q="rabbit", extras={"ext_bbox": "0.75,0.75,1.75,1.75"}
        )

        assert result["count"] == 2


@pytest.mark.usefixtures("clean_db", "clean_index", "harvest_setup", "with_plugins")
@pytest.mark.ckan_config(
    "ckan.plugins", "test_spatial_plugin spatial_metadata spatial_query")
@pytest.mark.ckan_config("ckanext.spatial.search_backend", "solr-spatial-field")
class TestCustomIndexing(SpatialTestBase):
    """
    These tests ensure both that
    1. You can use your own custom logic to index geometries
    2. The spatial fields are multivalued, ie you can index more than one geometry against
       the same dataset
    """
    def test_single_geom(self):
        dataset = factories.Dataset(
            extras=[{"key": "my_geoms", "value": self.geojson_examples["polygon"]}]
        )

        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-180,-90,180,90"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

    def test_multiple_geoms(self):
        dataset = factories.Dataset(
            extras=[
                {
                    "key": "my_geoms",
                    "value": "[{}, {}]".format(
                        extents["nz"], extents["ohio"])
                }
            ]
        )

        # Test that we get the same dataset using two different extents

        # New Zealand
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "56,-54,189,-28"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]

        # Ohio
        result = helpers.call_action(
            "package_search", extras={"ext_bbox": "-110,37,-78,53"}
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == dataset["id"]
