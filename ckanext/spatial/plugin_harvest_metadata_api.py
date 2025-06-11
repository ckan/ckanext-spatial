from ckan import plugins as p
import ckanext.spatial.views as blueprints


class HarvestMetadataApi(p.SingletonPlugin):
    """
    Harvest Metadata API
    (previously called "InspireApi")

    A way for a user to view the harvested metadata XML, either as a raw file or
    styled to view in a web browser.
    """

    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.harvest_metadata]
