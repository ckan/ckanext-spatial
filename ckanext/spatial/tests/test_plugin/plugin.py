from ckan import plugins as p


class TestSpatialPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
