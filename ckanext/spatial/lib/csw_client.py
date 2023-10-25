"""
Some very thin wrapper classes around those in OWSLib
for convenience.
"""
import six
import logging

from owslib.etree import etree
from owslib.fes import PropertyIsEqualTo, SortBy, SortProperty

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
            elif isinstance(val, six.string_types):
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

    def __init__(self, endpoint=None):
        super(CswService, self).__init__(endpoint)
        self.sortby = SortBy([SortProperty('dc:identifier')])
        # check capabilities
        _cap = self.getcapabilities(endpoint)['response']
        self.capabilities = etree.ElementTree(etree.fromstring(_cap))
        self.output_schemas = {
            'GetRecords': self._get_output_schemas('GetRecords'),
            'GetRecordById': self._get_output_schemas('GetRecordById'),
        }

    def _get_output_schemas(self, operation):
        _cap_ns = self.capabilities.getroot().nsmap
        _ows_ns = _cap_ns.get('ows')
        if not _ows_ns:
            raise CswError('Bad getcapabilities response: OWS namespace not found ' + str(_cap_ns))
        _op = self.capabilities.find("//{{{}}}Operation[@name='{}']".format(_ows_ns, operation))
        _schemas = _op.find("{{{}}}Parameter[@name='outputSchema']".format(_ows_ns))
        _values = map(lambda v: v.text, _schemas.findall("{{{}}}Value".format(_ows_ns)))
        output_schemas = {}
        for key, value in _schemas.nsmap.items():
            if value in _values:
                output_schemas.update({key : value})
        return output_schemas

    def getrecords(self, qtype=None, keywords=[],
                   typenames="csw:Record", esn="brief",
                   skip=0, count=10, outputschema="gmd", **kw):

        constraints = []
        csw = self._ows(**kw)

        # check target csw server capabilities for requested output schema
        output_schemas = self.output_schemas['GetRecords']
        if not output_schemas.get(outputschema):
            raise CswError('Output schema \'{}\' not supported by target server: '.format(output_schemas))

        if qtype is not None:
           constraints.append(PropertyIsEqualTo("dc:type", qtype))

        kwa = {
            "constraints": constraints,
            "typenames": typenames,
            "esn": esn,
            "startposition": skip,
            "maxrecords": count,
            "outputschema": output_schemas[outputschema],
            "sortby": self.sortby
            }
        log.info('Making CSW request: getrecords2 %r', kwa)
        csw.getrecords2(**kwa)
        if csw.exceptionreport:
            err = 'Error getting records: %r' % \
                  csw.exceptionreport.exceptions
            #log.error(err)
            raise CswError(err)
        return [self._xmd(r) for r in list(csw.records.values())]

    def getidentifiers(self, qtype=None, typenames="csw:Record", esn="brief",
                       keywords=[], limit=None, page=10, outputschema="gmd",
                       startposition=0, cql=None, **kw):

        constraints = []
        csw = self._ows(**kw)

        # check target csw server capabilities for requested output schema
        output_schemas = self.output_schemas['GetRecords']
        if not output_schemas.get(outputschema):
            raise CswError('Output schema \'{}\' not supported by target server: '.format(output_schemas))

        if qtype is not None:
           constraints.append(PropertyIsEqualTo("dc:type", qtype))

        kwa = {
            "constraints": constraints,
            "typenames": typenames,
            "esn": esn,
            "startposition": startposition,
            "maxrecords": page,
            "outputschema": output_schemas[outputschema],
            "cql": cql,
            "sortby": self.sortby
            }
        i = 0
        matches = 0
        while True:
            log.info('Making CSW request: getrecords2 %r', kwa)

            csw.getrecords2(**kwa)
            if csw.exceptionreport:
                err = 'Error getting identifiers: %r' % \
                      csw.exceptionreport.exceptions
                #log.error(err)

            if matches == 0:
                matches = csw.results['matches']

            identifiers = list(csw.records.keys())
            if limit is not None:
                identifiers = identifiers[:(limit-startposition)]
            for ident in identifiers:
                yield ident

            if len(identifiers) == 0:
                break

            i += len(identifiers)
            if limit is not None and i > limit:
                break

            startposition += page
            if startposition >= (matches + 1):
                break

            kwa["startposition"] = startposition

    def getrecordbyid(self, ids=[], esn="full", outputschema="gmd", **kw):
        
        csw = self._ows(**kw)

        # fetch target csw server capabilities for requested output schema
        output_schemas=output_schemas = self.output_schemas['GetRecordById']
        if not output_schemas.get(outputschema):
            raise CswError('Output schema \'{}\' not supported by target server: '.format(output_schemas))

        kwa = {
            "esn": esn,
            "outputschema": output_schemas[outputschema],
            }
        # Ordinary Python version's don't support the metadata argument
        log.info('Making CSW request: getrecordbyid %r %r', ids, kwa)
        csw.getrecordbyid(ids, **kwa)
        if csw.exceptionreport:
            err = 'Error getting record by id: %r' % \
                  csw.exceptionreport.exceptions
            #log.error(err)
            raise CswError(err)
        elif csw.records:
            record = self._xmd(list(csw.records.values())[0])
        elif csw.response:
            record = self._xmd(etree.fromstring(csw.response))
        else:
            return

        ## strip off the enclosing results container, we only want the metadata
        # '/{schema}*' expression should be safe enough and is able to match the
        #  desired schema followed by both MD_Metadata or MI_Metadata (iso19115[-2])
        md = csw._exml.find("/{{{schema}}}*".format(schema=output_schemas[outputschema]))
        mdtree = etree.ElementTree(md)
        try:
            record["xml"] = etree.tostring(mdtree, pretty_print=True, encoding=str)
        except TypeError:
            # API incompatibilities between different flavours of elementtree
            try:
                record["xml"] = etree.tostring(mdtree, pretty_print=True, encoding=str)
            except AssertionError:
                record["xml"] = etree.tostring(md, pretty_print=True, encoding=str)

        record["xml"] = '<?xml version="1.0" encoding="UTF-8"?>\n' + record["xml"]
        record["tree"] = mdtree
        return record
