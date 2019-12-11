import ckan.plugins as p
import ckanext.spatial.views as blueprints

class SpatialQueryMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.api]

class HarvestMetadataApiMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.harvest_metadata]
