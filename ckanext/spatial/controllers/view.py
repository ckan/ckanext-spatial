import urllib2

from pylons.i18n import _

import ckan.lib.helpers as h, json
from ckan.lib.base import BaseController, c, g, request, \
                          response, session, render, config, abort, redirect

from ckan.model import Package

class ViewController(BaseController):

    def __before__(self, action, **env):
        super(ViewController, self).__before__(action, **env)
        # All calls to this controller must be with a sysadmin key
        if not self.authorizer.is_sysadmin(c.user):
            response_msg = _('Not authorized to see this page')
            status = 401
            abort(status, response_msg)

    def wms_preview(self,id):
        #check if package exists
        c.pkg = Package.get(id)
        if c.pkg is None:
            abort(404, 'Package not found')

        for res in c.pkg.resources:
            if res.format == "WMS":
                c.wms_url = res.url if not '?' in res.url else res.url.split('?')[0]
                break
        if not c.wms_url:
            abort(400, 'This package does not have a WMS resource')

        return render('ckanext/spatial/wms_preview.html')

    def proxy(self):
        if not 'url' in request.params:
            abort(400)
        try:
            server_response = urllib2.urlopen(request.params['url'])
            headers = server_response.info()
            if headers.get('Content-Type'):
                response.content_type = headers.get('Content-Type')
            return server_response.read()
        except urllib2.HTTPError as e:
            response.status_int = e.getcode()
            return
