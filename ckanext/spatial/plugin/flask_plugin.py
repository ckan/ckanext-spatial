# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.spatial.views as blueprints
from ckanext.spatial.cli import get_commands


class SpatialQueryMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.api]

    # IClick

    def get_commands(self):
        return get_commands()


class HarvestMetadataApiMixin(p.SingletonPlugin):
    p.implements(p.IBlueprint)

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.harvest_metadata]
