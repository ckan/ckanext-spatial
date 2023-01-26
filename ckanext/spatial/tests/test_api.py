import pytest

from ckan.model import Session

from ckanext.spatial.tests.base import SpatialTestBase


@pytest.mark.usefixtures(
    "with_plugins",
    "clean_db",
    "clean_index",
    "harvest_setup",
)
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
            raise pytest.skip("The harvester extension is needed for these tests")

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
        assert r.headers["Content-Type"] == "application/xml; charset=utf-8"
        assert r.body == '<?xml version="1.0" encoding="UTF-8"?>\n<xml>Content 1</xml>'

        # Access human-readable view of content
        url = "/harvest/object/{0}/html".format(object_id_1)
        r = app.get(url, status=200)
        assert(
            r.headers["Content-Type"] == "text/html; charset=utf-8"
        )

        # Access original content in object extra (if present)
        url = "/harvest/object/{0}/original".format(object_id_1)
        r = app.get(url, status=404)

        url = "/harvest/object/{0}/original".format(object_id_2)
        r = app.get(url, status=200)
        assert r.headers["Content-Type"] == "application/xml; charset=utf-8"
        assert (
            r.body
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            + "<xml>Original Content 2</xml>"
        )
