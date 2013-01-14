from logging import getLogger

from ckan import plugins as p


log = getLogger(__name__)


class WMSPreview(p.SingletonPlugin):

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourcePreview, inherit=True)

    def update_config(self, config):
        ''' Set up the resource library, public directory and
        template directory for the preview
        '''
        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates/dataviewer')
        p.toolkit.add_resource('public', 'ckanext-wmspreview')

        self.proxy_enabled = config.get('ckan.resource_proxy_enabled', False)


    def setup_template_variables(self, context, data_dict):
        import ckanext.resourceproxy.plugin as proxy
        if self.proxy_enabled and not data_dict['resource']['on_same_domain']:
            p.toolkit.c.resource['proxy_url'] = proxy.get_proxified_resource_url(data_dict)
        else:
            p.toolkit.c.resource['proxy_url'] = data_dict['resource']['url']

    def can_preview(self, data_dict):
        format_lower = data_dict['resource']['format'].lower()

        check = format_lower in ['wms']
        if not self.proxy_enabled and check:
            check = data_dict['resource']['on_same_domain']

        return check

    def preview_template(self, context, data_dict):
        return 'wms.html'
