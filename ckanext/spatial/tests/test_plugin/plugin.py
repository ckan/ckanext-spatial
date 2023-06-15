import json
import shapely
from ckan import plugins as p


class TestSpatialPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)

    p.implements(p.IPackageController, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, "templates")

    def before_index(self, pkg_dict):
        return self.before_dataset_index(pkg_dict)

    def before_dataset_index(self, pkg_dict):

        if not pkg_dict.get("my_geoms"):
            return pkg_dict

        pkg_dict["spatial_geom"] = []

        my_geoms = json.loads(pkg_dict["my_geoms"])

        if not isinstance(my_geoms, list):
            my_geoms = [my_geoms]

        for geom in my_geoms:

            shape = shapely.geometry.shape(geom)

            pkg_dict["spatial_geom"].append(shape.wkt)

        return pkg_dict
