# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

from ckanext.spatial.harvesters.csw import CSWHarvester
from ckanext.spatial.harvesters.waf import WAFHarvester
from ckanext.spatial.harvesters.doc import DocHarvester
