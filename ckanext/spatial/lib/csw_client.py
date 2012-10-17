"""
Some very thin wrapper classes around those in OWSLib
for convenience.
"""

import logging

from owslib.etree import etree

log = logging.getLogger(__name__)

class CswError(Exception):
    pass

class OwsService(object):
    def __init__(self, endpoint=None):
        if endpoint is not None:
            self._ows(endpoint)
            
    def __call__(self, args):
        return getattr(self, args.operation)(**self._xmd(args))
    
    @classmethod
    def _operations(cls):
        return [x for x in dir(cls) if not x.startswith("_")]
    
    def _xmd(self, obj):
        md = {}
        for attr in [x for x in dir(obj) if not x.startswith("_")]:
            val = getattr(obj, attr)
            if not val:
                pass
            elif callable(val):
                pass
            elif isinstance(val, basestring):
                md[attr] = val
            elif isinstance(val, int):
                md[attr] = val
            elif isinstance(val, list):
                md[attr] = val
            else:
                md[attr] = self._xmd(val)
        return md
        
    def _ows(self, endpoint=None, **kw):
        if not hasattr(self, "_Implementation"):
            raise NotImplementedError("Needs an Implementation")
        if not hasattr(self, "__ows_obj__"):
            if endpoint is None:
                raise ValueError("Must specify a service endpoint")
            self.__ows_obj__ = self._Implementation(endpoint)
        return self.__ows_obj__
    
    def getcapabilities(self, debug=False, **kw):
        ows = self._ows(**kw)
        caps = self._xmd(ows)
        if not debug:
            if "request" in caps: del caps["request"]
            if "response" in caps: del caps["response"]
        if "owscommon" in caps: del caps["owscommon"]
        return caps
    
class CswService(OwsService):
    """
    Perform various operations on a CSW service
    """
    from owslib.csw import CatalogueServiceWeb as _Implementation
    def getrecords(self, qtype=None, keywords=[],
                   typenames="csw:Record", esn="brief",
                   skip=0, count=10, outputschema="gmd", **kw):
        from owslib.csw import namespaces
        csw = self._ows(**kw)
        kwa = {
            "qtype": qtype,
            "keywords": keywords,
            "typenames": typenames,
            "esn": esn,
            "startposition": skip,
            "maxrecords": count,
            "outputschema": namespaces[outputschema],
            }
        log.info('Making CSW request: getrecords %r', kwa)
        csw.getrecords(**kwa)
        if csw.exceptionreport:
            err = 'Error getting records: %r' % \
                  csw.exceptionreport.exceptions
            #log.error(err)
            raise CswError(err)
        return [self._xmd(r) for r in csw.records.values()]

    def getidentifiers(self, qtype=None, typenames="csw:Record", esn="brief",
                       keywords=[], limit=None, page=10, outputschema="gmd",
                       **kw):
        from owslib.csw import namespaces
        csw = self._ows(**kw)
        kwa = {
            "qtype": qtype,
            "keywords": keywords,
            "typenames": typenames,
            "esn": esn,
            "startposition": 0,
            "maxrecords": page,
            "outputschema": namespaces[outputschema],
            }
        i = 0
        while True:
            log.info('Making CSW request: getrecords %r', kwa)
            csw.getrecords(**kwa)
            if csw.exceptionreport:
                err = 'Error getting identifiers: %r' % \
                      csw.exceptionreport.exceptions
                #log.error(err)
                raise CswError(err)
            identifiers = csw.records.keys()
            if limit is not None:
                identifiers = identifiers[:(limit-startposition)]
            for ident in identifiers:
                yield ident
            if len(identifiers) < page:
                break
            i += len(identifiers)
            if limit is not None and i > limit:
                break
            kwa["startposition"] += page
            
    def getrecordbyid(self, ids=[], esn="full", outputschema="gmd", **kw):
        from owslib.csw import namespaces
        csw = self._ows(**kw)
        kwa = {
            "esn": esn,
            "outputschema": namespaces[outputschema],
            }
        # Ordinary Python version's don't support the metadata argument
        log.info('Making CSW request: getrecordbyid %r %r', ids, kwa)
        csw.getrecordbyid(ids, **kwa)
        if csw.exceptionreport:
            err = 'Error getting record by id: %r' % \
                  csw.exceptionreport.exceptions
            #log.error(err)
            raise CswError(err)
        if not csw.records:
            return
        record = self._xmd(csw.records.values()[0])

        ## strip off the enclosing results container, we only want the metadata
        #md = csw._exml.find("/gmd:MD_Metadata")#, namespaces=namespaces)
        # Ordinary Python version's don't support the metadata argument
        md = csw._exml.find("/{http://www.isotc211.org/2005/gmd}MD_Metadata")
        mdtree = etree.ElementTree(md)
        try:
            record["xml"] = etree.tostring(mdtree, pretty_print=True, xml_declaration=True)
        except TypeError:
            # API incompatibilities between different flavours of elementtree
            try:
                record["xml"] = etree.tostring(mdtree)
            except AssertionError:
                record["xml"] = etree.tostring(md)
        record["tree"] = mdtree
        return record
