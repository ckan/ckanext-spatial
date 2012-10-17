import argparse
from pprint import pprint
import types
import logging

from ckanext.spatial.lib.csw_client import CswService

#remote = "http://www.nationaalgeoregister.nl/geonetwork/srv/eng/csw"
#remote = "http://locationmetadataeditor.data.gov.uk/geonetwork/srv/csw"

def cswinfo():
    """
    Hello World
    """
    log_format = '%(asctime)-7s %(levelname)s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)

    parser = argparse.ArgumentParser(description=cswinfo.__doc__)

    parser.add_argument("-d", "--debug", dest="debug", action="store_true")
    
    sub = parser.add_subparsers()
    csw_p = sub.add_parser("csw", description=CswService.__doc__)
    csw_p.add_argument("operation", action="store", choices=CswService._operations())
    csw_p.add_argument("endpoint", action="store")
    csw_p.add_argument("ids", nargs="*")
    csw_p.add_argument("--qtype", help="type of resource to query (i.e. service, dataset)")
    csw_p.add_argument("--keywords", default=[], action="append",
                       help="list of keywords")
    csw_p.add_argument("--typenames", help="the typeNames to query against (default is csw:Record)")
                       
    csw_p.add_argument("--esn", help="the ElementSetName 'full', 'brief' or 'summary'")
    csw_p.add_argument("-s", "--skip", default=0, type=int)
    csw_p.add_argument("-c", "--count", default=10, type=int)
    csw_p.set_defaults(service=CswService)
    
    args = parser.parse_args()
    service = args.service()
    value = service(args)
    if isinstance(value, basestring):
        print value
    elif isinstance(value, types.GeneratorType):
        count = 0
        for val in value:
            print val
            count += 1
        print '%i results' % count
    elif value is not None:
        pprint(value)
