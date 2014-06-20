try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO
import traceback
from datetime import datetime

from pylons import request, response, config
from lxml import etree
from owslib.csw import namespaces
from sqlalchemy import select,distinct,or_

from ckan.lib.base import BaseController
from ckan.lib.helpers import truncate
from ckan.model import Package
from ckan.model.meta import Session
from ckanext.harvest.model import HarvestObject, HarvestJob, HarvestSource

namespaces["xlink"] = "http://www.w3.org/1999/xlink"

log = __import__("logging").getLogger(__name__)

LOG_XML_LENGTH = config.get('cswservice.log_xml_length', 1000)

from random import random
class __rlog__(object):
    """
    Random log -- log wrapper to log a defined percentage
    of dialogues
    """
    def __init__(self, threshold=config["cswservice.rndlog_threshold"]):
        self.threshold = threshold
        self.i = random()
    def __getattr__(self, attr):
        if self.i > self.threshold:
            return self.dummy
        return getattr(log, attr)
    def dummy(self, *av, **kw):
        pass

def ntag(nselem):
    pfx, elem = nselem.split(":")
    return "{%s}%s" % (namespaces[pfx], elem)

class CatalogueServiceWebController(BaseController):
    '''Basic CSW server'''

    def _operations(self):
        '''Returns a list of this class\'s methods.
        '''
        return dict((x, getattr(self, x)) for x in dir(self) if not x.startswith("_"))

    def dispatch_get(self):
        self.rlog = __rlog__()
        self.rlog.info("request environ\n%s", request.environ)
        self.rlog.info("request headers\n%s", request.headers)
        ops = self._operations()
        req = dict(request.GET.items())
        
        ## special cases
	if "REQUEST" in req: req["request"] = req["REQUEST"]
        if "SERVICE" in req: req["service"] = req["SERVICE"]

        if "request" not in req:
            err = self._exception(exceptionCode="MissingParameterValue", locator="request")
            return self._render_xml(err)
        if req["request"] not in ops:
            err = self._exception(exceptionCode="OperationNotSupported",
                                 locator=req["request"])
            return self._render_xml(err)
        if "service" not in req:
            err = self._exception(exceptionCode="MissingParameterValue", locator="service")
            return self._render_xml(err)
        if req["service"] != "CSW":
            err = self._exception(exceptionCode="InvalidParameterValue", locator="service",
                                 text=req["service"])
            return self._render_xml(err)
        ## fill in some defaults
        startPosition = req.get("startPosition", 1)
        try:
            req["startPosition"] = int(startPosition)
        except:
            err = self._exception(exceptionCode="InvalidParameterValue", locator="startPosition",
                                  text=unicode(startPosition))
            return self._render_xml(err)
        maxRecords = req.get("maxRecords", 10)
        try:
            req["maxRecords"] = int(maxRecords)
        except:
            err = self._exception(exceptionCode="InvalidParameterValue", locator="maxRecords",
                                  text=unicode(maxRecords))
            return self._render_xml(err)
        req["id"] = [req["id"]] if "id" in req else []
        return ops[req["request"]](req)

    def dispatch_post(self):
        self.rlog = __rlog__()
        self.rlog.info("request environ\n%s", request.environ)
        self.rlog.info("request headers\n%s", request.headers)
        ops = self._operations()
        try:
            req = etree.parse(StringIO(request.body))
            self.rlog.info(u"request body\n%s", etree.tostring(req, pretty_print=True))
        except:
            self.rlog.info("request body\n%s", request.body)
            self.rlog.error("exception parsing body\n%s", traceback.format_exc())
            err = self._exception(exceptionCode="MissingParameterValue", locator="request")
            return self._render_xml(err)

        root = req.getroot()
        _unused, op = root.tag.rsplit("}", 1)
        if op not in ops:
            err = self._exception(exceptionCode="OperationNotSupported", locator=op)
            return self._render_xml(err)

        req = self._parse_xml_request(root)
        if not isinstance(req, dict):
            return req
        return ops[op](req)

    def _render_xml(self, root):
        tree = etree.ElementTree(root)
        data = etree.tostring(tree, pretty_print=True)
        response.headers["Content-Length"] = len(data)
        response.content_type = "application/xml"
        response.charset="UTF-8"
        self.rlog.info("response headers:\n%s", response.headers)
        self.rlog.info("response.body:\n%s", data)
        return data

    def _exception(self, text=None, **kw):
        metaargs = {
            "nsmap": namespaces,
            "version": "1.0.0",
            ntag("xsi:schemaLocation"): "http://schemas.opengis.net/ows/1.0.0/owsExceptionReport.xsd",
        }
        root = etree.Element(ntag("ows:ExceptionReport"), **metaargs)
        exc = etree.SubElement(root, ntag("ows:Exception"), **kw)
        if text is not None:
            txt = etree.SubElement(exc, ntag("ows:ExceptionText"))
            txt.text = text
        return root

    def _parse_xml_request(self, root):
        """
        Check common parts of the request for GetRecords, GetRecordById, etc.
        Return a dictionary of parameters or else an XML error message (string).
        The dictionary should be compatible with CSW GET requests
        """
        service = root.get("service")
        if service is None:
            err = self._exception(exceptionCode="MissingParameterValue", locator="service")
            return self._render_xml(err)
        elif service != "CSW":
            err = self._exception(exceptionCode="InvalidParameterValue", locator="service", text=service)
            return self._render_xml(err)
        outputSchema = root.get("outputSchema", namespaces["gmd"])
        if outputSchema != namespaces["gmd"]:
            err = self._exception(exceptionCode="InvalidParameterValue", locator="outputSchema", text=outputSchema)
            return self._render_xml(err)
        resultType = root.get("resultType", "results")
        if resultType not in ("results", "hits"):
            err = self._exception(exceptionCode="InvalidParameterValue", locator="resultType", text=resultType)
            return self._render_xml(err)
        outputFormat = root.get("outputFormat", "application/xml")
        if outputFormat != "application/xml":
            err = self._exception(exceptionCode="InvalidParameterValue", locator="outputFormat", text=outputFormat)
            return self._render_xml(err)
        elementSetName = root.get("elementSetName", "full")

        params = {
            "outputSchema": outputSchema,
            "resultType": resultType,
            "outputFormat": outputFormat,
            "elementSetName": elementSetName
            }

        startPosition = root.get("startPosition", "1")
        try:
            params["startPosition"] = int(startPosition)
        except:
            err = self._exception(exceptionCode="InvalidParameterValue", locator="startPosition")
            return self._render_xml(err)
        maxRecords = root.get("maxRecords", "10")
        try:
            params["maxRecords"] = int(maxRecords)
        except:
            err = self._exception(exceptionCode="InvalidParameterValue", locator="maxRecords")
            return self._render_xml(err)

        params["id"] = [x.text for x in root.findall(ntag("csw:Id"))]

        query = root.find(ntag("csw:Query"))
        if query is not None:
            params.update(self._parse_query(query))

        if params["elementSetName"] not in ("full", "brief", "summary"):
            err = self._exception(exceptionCode="InvalidParameterValue", locator="elementSetName",
                                 text=params["elementSetName"])
            return self._render_xml(err)

        return params

    def _parse_query(self, query):
        params = {}
        params["typeNames"] = query.get("typeNames", "csw:Record")
        esn = query.find(ntag("csw:ElementSetName"))
        if esn is not None:
            params["elementSetName"] = esn.text
        return params

    def GetCapabilities(self, req):
        site = request.host_url + request.path
        caps = etree.Element(ntag("csw:Capabilities"), nsmap=namespaces)
        srvid = etree.SubElement(caps, ntag("ows:ServiceIdentification"))
        title = etree.SubElement(srvid, ntag("ows:Title"))
        title.text = unicode(config["cswservice.title"])
        abstract = etree.SubElement(srvid, ntag("ows:Abstract"))
        abstract.text = unicode(config["cswservice.abstract"])
        keywords = etree.SubElement(srvid, ntag("ows:Keywords"))
        for word in [w.strip() for w in config["cswservice.keywords"].split(",")]:
            if word == "": continue
            kw = etree.SubElement(keywords, ntag("ows:Keyword"))
            kw.text = unicode(word)
        kwtype = etree.SubElement(keywords, ntag("ows:Type"))
        kwtype.text = unicode(config["cswservice.keyword_type"])
        srvtype = etree.SubElement(srvid, ntag("ows:ServiceType"))
        srvtype.text = "CSW"
        srvver = etree.SubElement(srvid, ntag("ows:ServiceTypeVersion"))
        srvver.text = "2.0.2"
        ### ows:Fees, ows:AccessConstraints

        provider = etree.SubElement(caps, ntag("ows:ServiceProvider"))
        provname = etree.SubElement(provider, ntag("ows:ProviderName"))
        provname.text = unicode(config["cswservice.provider_name"])
        attrs = {
            ntag("xlink:href"): site
            }
        etree.SubElement(provider, ntag("ows:ProviderSite"), **attrs)

        contact = etree.SubElement(provider, ntag("ows:ServiceContact"))
        name = etree.SubElement(contact, ntag("ows:IndividualName"))
        name.text = unicode(config["cswservice.contact_name"])
        pos = etree.SubElement(contact, ntag("ows:PositionName"))
        pos.text = unicode(config["cswservice.contact_position"])
        cinfo = etree.SubElement(contact, ntag("ows:ContactInfo"))
        phone = etree.SubElement(cinfo, ntag("ows:Phone"))
        voice = etree.SubElement(phone, ntag("ows:Voice"))
        voice.text = unicode(config["cswservice.contact_voice"])
        fax = etree.SubElement(phone, ntag("ows:Fax"))
        fax.text = unicode(config["cswservice.contact_fax"])
        addr = etree.SubElement(cinfo, ntag("ows:Address"))
        dpoint = etree.SubElement(addr, ntag("ows:DeliveryPoint"))
        dpoint.text= unicode(config["cswservice.contact_address"])
        city = etree.SubElement(addr, ntag("ows:City"))
        city.text = unicode(config["cswservice.contact_city"])
        region = etree.SubElement(addr, ntag("ows:AdministrativeArea"))
        region.text = unicode(config["cswservice.contact_region"])
        pcode = etree.SubElement(addr, ntag("ows:PostalCode"))
        pcode.text = unicode(config["cswservice.contact_pcode"])
        country = etree.SubElement(addr, ntag("ows:Country"))
        country.text = unicode(config["cswservice.contact_country"])
        email = etree.SubElement(addr, ntag("ows:ElectronicMailAddress"))
        email.text = unicode(config["cswservice.contact_email"])
        hours = etree.SubElement(cinfo, ntag("ows:HoursOfService"))
        hours.text = unicode(config["cswservice.contact_hours"])
        instructions = etree.SubElement(cinfo, ntag("ows:ContactInstructions"))
        instructions.text = unicode(config["cswservice.contact_instructions"])
        role = etree.SubElement(contact, ntag("ows:Role"))
        role.text = unicode(config["cswservice.contact_role"])

        opmeta = etree.SubElement(caps, ntag("ows:OperationsMetadata"))

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetCapabilities")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Get"), **attrs)
        post = etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(post, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetRecords")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Get"), **attrs)
        post = etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(post, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="resultType")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "results"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputFormat")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "application/xml"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputSchema")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "http://www.isotc211.org/2005/gmd"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="typeNames")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "gmd:MD_Metadata"

        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="GetRecordById")
        dcp = etree.SubElement(op, ntag("ows:DCP"))
        http = etree.SubElement(dcp, ntag("ows:HTTP"))
        attrs = { ntag("xlink:href"): site }
        etree.SubElement(http, ntag("ows:Get"), **attrs)
        post = etree.SubElement(http, ntag("ows:Post"), **attrs)
        pe = etree.SubElement(post, ntag("ows:Constraint"), name="PostEncoding")
        val = etree.SubElement(pe, ntag("ows:Value"))
        val.text = "XML"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="resultType")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "results"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputFormat")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "application/xml"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputSchema")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "http://www.isotc211.org/2005/gmd"
        param = etree.SubElement(op, ntag("ows:Parameter"), name="typeNames")
        val = etree.SubElement(param, ntag("ows:Value"))
        val.text = "gmd:MD_Metadata"

#        op = etree.SubElement(opmeta, ntag("ows:Operation"), name="Harvest")
#        dcp = etree.SubElement(op, ntag("ows:DCP"))
#        http = etree.SubElement(dcp, ntag("ows:HTTP"))
#        attrs = { ntag("xlink:href"): site }
#        post = etree.SubElement(http, ntag("ows:Post"), **attrs)
#        pe = etree.SubElement(post, ntag("ows:Constraint"), name="PostEncoding")
#        val = etree.SubElement(pe, ntag("ows:Value"))
#        val.text = "XML"
#        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputFormat")
#        val = etree.SubElement(param, ntag("ows:Value"))
#        val.text = "application/xml"
#        param = etree.SubElement(op, ntag("ows:Parameter"), name="outputSchema")
#        val = etree.SubElement(param, ntag("ows:Value"))
#        val.text = "http://www.isotc211.org/2005/gmd"

        filcap = etree.SubElement(caps, ntag("ogc:Filter_Capabilities"))
        spacap = etree.SubElement(filcap, ntag("ogc:Spatial_Capabilities"))
        geomop = etree.SubElement(spacap, ntag("ogc:GeometryOperands"))
        spaceop = etree.SubElement(spacap, ntag("ogc:SpatialOperators"))

        scalcap = etree.SubElement(filcap, ntag("ogc:Scalar_Capabilities"))
        lop = etree.SubElement(scalcap, ntag("ogc:LogicalOperators"))
        cop = etree.SubElement(scalcap, ntag("ogc:ComparisonOperators"))

        idcap = etree.SubElement(filcap, ntag("ogc:Id_Capabilities"))
        eid = etree.SubElement(idcap, ntag("ogc:EID"))
        fid = etree.SubElement(idcap, ntag("ogc:FID"))

        data = self._render_xml(caps)
        log.info('GetCapabilities response: %r', truncate(data, LOG_XML_LENGTH))
        return data

    def GetRecords(self, req):
        resp = etree.Element(ntag("csw:GetRecordsResponse"), nsmap=namespaces)
        etree.SubElement(resp, ntag("csw:SearchStatus"), timestamp=datetime.utcnow().isoformat())

        cursor = Session.connection()

        q = Session.query(distinct(HarvestObject.guid)) \
                .join(Package) \
                .join(HarvestSource) \
                .filter(HarvestObject.current==True) \
                .filter(Package.state==u'active') \
                .filter(or_(HarvestSource.type=='gemini-single', \
                        HarvestSource.type=='gemini-waf', \
                        HarvestSource.type=='csw'))

        ### TODO Parse query instead of stupidly just returning whatever we like
        startPosition = req["startPosition"] if req["startPosition"] > 0 else 1
        maxRecords = req["maxRecords"] if req["maxRecords"] > 0 else 10
        rset = q.offset(startPosition-1).limit(maxRecords)

        total = q.count()
        attrs = {
            "numberOfRecordsMatched": total,
            "elementSet": req["elementSetName"], # we lie here. it's always really "full"
            }
        if req["resultType"] == "results":
            returned = rset.count()
            attrs["numberOfRecordsReturned"] = returned
            if (total-startPosition-1) > returned:
                attrs["nextRecord"] = startPosition + returned
            else:
                attrs["nextRecord"] = 0
        else:
            attrs["numberOfRecordsReturned"] = 0

        attrs = dict((k, unicode(v)) for k,v in attrs.items())
        results = etree.SubElement(resp, ntag("csw:SearchResults"), **attrs)

        if req["resultType"] == "results":
            for guid, in Session.execute(rset):
                doc = Session.query(HarvestObject) \
                        .join(Package) \
                        .filter(HarvestObject.guid==guid) \
                        .filter(HarvestObject.current==True) \
                        .filter(Package.state==u'active') \
                        .first()
                try:

                    record = etree.parse(StringIO(doc.content.encode("utf-8")))
                    results.append(record.getroot())
                except:
                    log.error("exception parsing document %s:\n%s", doc.id, traceback.format_exc())
                    raise

        data = self._render_xml(resp)
        log.info('GetRecords response: %r', truncate(data, LOG_XML_LENGTH))
        return data

    def GetRecordById(self, req):
        resp = etree.Element(ntag("csw:GetRecordByIdResponse"), nsmap=namespaces)
        seen = set()
        for ident in req["id"]:
            doc = Session.query(HarvestObject) \
                    .join(Package) \
                    .join(HarvestJob).join(HarvestSource) \
                    .filter(HarvestSource.active==True) \
                    .filter(HarvestObject.guid==ident) \
                    .filter(HarvestObject.package!=None) \
                    .filter(Package.state==u'active') \
                    .order_by(HarvestObject.gathered.desc()) \
                    .limit(1).first()

            if doc is None:
                continue

            if 'MD_Metadata' in doc.content:
                try:
                    record = etree.parse(StringIO(doc.content.encode("utf-8")))
                    resp.append(record.getroot())
                except:
                    log.error("exception parsing document %s:\n%s", doc.id, traceback.format_exc())
                    raise

        data = self._render_xml(resp)
        log.info('GetRecordById response: %r', truncate(data, LOG_XML_LENGTH))
        return data

### <ns0:GetRecords xmlns:ns0="http://www.opengis.net/cat/csw/2.0.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" outputSchema="http://www.isotc211.org/2005/gmd" outputFormat="application/xml" version="2.0.2" resultType="results" service="CSW" startPosition="1" maxRecords="5" xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
###     <ns0:Query typeNames="csw:Record">
###         <ns0:ElementSetName>full</ns0:ElementSetName>
###         <ns0:Constraint version="1.1.0">
###             <ns0:Filter xmlns:ns0="http://www.opengis.net/ogc">
###                 <ns0:PropertyIsEqualTo>
###                     <ns0:PropertyName>dc:type</ns0:PropertyName>
###                     <ns0:Literal>dataset</ns0:Literal>
###                 </ns0:PropertyIsEqualTo>
###             </ns0:Filter>
###         </ns0:Constraint>
###     </ns0:Query>
### </ns0:GetRecords>

