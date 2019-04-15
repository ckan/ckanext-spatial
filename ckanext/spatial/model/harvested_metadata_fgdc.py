import re
from lxml import etree
from ckanext.harvest.harvesters.base import munge_tag

import logging
log = logging.getLogger(__name__)


class MappedXmlObject(object):
    elements = []


class MappedXmlDocument(MappedXmlObject):
    def __init__(self, xml_str=None, xml_tree=None):
        assert (xml_str or xml_tree is not None), 'Must provide some XML in one format or another'
        self.xml_str = xml_str
        self.xml_tree = xml_tree

    def read_values(self):
        '''For all of the elements listed, finds the values of them in the
        XML and returns them.'''
        values = {}
        tree = self.get_xml_tree()
        for element in self.elements:
            values[element.name] = element.read_value(tree)
        self.infer_values(values)
        return values

    def read_value(self, name):
        '''For the given element name, find the value in the XML and return
        it.
        '''
        tree = self.get_xml_tree()
        for element in self.elements:
            if element.name == name:
                return element.read_value(tree)
        raise KeyError

    def get_xml_tree(self):
        if self.xml_tree is None:
            parser = etree.XMLParser(remove_blank_text=True)
            if type(self.xml_str) == unicode:
                xml_str = self.xml_str.encode('utf8')
            else:
                xml_str = self.xml_str
            self.xml_tree = etree.fromstring(xml_str, parser=parser)
        return self.xml_tree

    def infer_values(self, values):
        pass


class MappedXmlElement(MappedXmlObject):
    namespaces = {}

    def __init__(self, name, search_paths=[], multiplicity="*", elements=[]):
        self.name = name
        self.search_paths = search_paths
        self.multiplicity = multiplicity
        self.elements = elements or self.elements

    def read_value(self, tree):
        values = []
        for xpath in self.get_search_paths():
            elements = self.get_elements(tree, xpath)
            values = self.get_values(elements)
            if values:
                break
        return self.fix_multiplicity(values)

    def get_search_paths(self):
        if type(self.search_paths) != type([]):
            search_paths = [self.search_paths]
        else:
            search_paths = self.search_paths
        return search_paths

    def get_elements(self, tree, xpath):
        return tree.xpath(xpath, namespaces=self.namespaces)

    def get_values(self, elements):
        values = []
        if len(elements) == 0:
            pass
        else:
            for element in elements:
                value = self.get_value(element)
                values.append(value)
        return values

    def get_value(self, element):
        if self.elements:
            value = {}
            for child in self.elements:
                value[child.name] = child.read_value(element)
            return value
        elif type(element) == etree._ElementStringResult:
            value = str(element)
        elif type(element) == etree._ElementUnicodeResult:
            value = unicode(element)
        else:
            value = self.element_tostring(element)
        return value

    def element_tostring(self, element):
        return etree.tostring(element, pretty_print=False)

    def fix_multiplicity(self, values):
        '''
        When a field contains multiple values, yet the spec says
        it should contain only one, then return just the first value,
        rather than a list.

        In the FGDC19115 specification, multiplicity relates to:
        * 'Association Cardinality'
        * 'Obligation/Condition' & 'Maximum Occurence'
        '''
        if self.multiplicity == "0":
            # 0 = None
            if values:
                log.warn("Values found for element '%s' when multiplicity should be 0: %s",  self.name, values)
            return ""
        elif self.multiplicity == "1":
            # 1 = Mandatory, maximum 1 = Exactly one
            if not values:
                log.warn("Value not found for element '%s'" % self.name)
                return ''
            return values[0]
        elif self.multiplicity == "*":
            # * = 0..* = zero or more
            return values
        elif self.multiplicity == "0..1":
            # 0..1 = Mandatory, maximum 1 = optional (zero or one)
            if values:
                return values[0]
            else:
                return ""
        elif self.multiplicity == "1..*":
            # 1..* = one or more
            return values
        else:
            log.warning('Multiplicity not specified for element: %s',
                        self.name)
            return values


class FGDCElement(MappedXmlElement):

    namespaces = {
       "gts": "http://www.isotc211.org/2005/gts",
       "gml": "http://www.opengis.net/gml",
       "gml32": "http://www.opengis.net/gml/3.2",
       "gmx": "http://www.isotc211.org/2005/gmx",
       "gsr": "http://www.isotc211.org/2005/gsr",
       "gss": "http://www.isotc211.org/2005/gss",
       "gco": "http://www.isotc211.org/2005/gco",
       "gmd": "http://www.isotc211.org/2005/gmd",
       "srv": "http://www.isotc211.org/2005/srv",
       "xlink": "http://www.w3.org/1999/xlink",
       "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }


class FGDCAttribute(FGDCElement):
    elements = [
        FGDCElement(
            name="attribute-label",
            search_paths="attrlabl/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="attribute-definition",
            search_paths="attrdef/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="attribute-definition-source",
            search_paths="attrdefs/text()",
            multiplicity="0..1",
        ),
    ]


class FGDCEntityAndAttribute(FGDCElement):
    elements = [
        FGDCElement(
            name="entity-type-label",
            search_paths=[
                "enttyp/enttypl/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="entity-type-definition",
            search_paths=[
                "enttyp/enttypd/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="entity-type-definition-source",
            search_paths=[
                "enttyp/enttypds/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCAttribute(
            name="attribute",
            search_paths="attr",
            multiplicity="*",
        ),
    ]


class FGDCResourceLocator(FGDCElement):
    elements = [
        FGDCElement(
            name="url",
            search_paths=[
                "digtopt/onlinopt/computer/networka/networkr/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="format-name",
            search_paths=[
                "digtinfo/formname/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="format-info-content",
            search_paths=[
                "digtinfo/formcont/text()",
            ],
            multiplicity="0..1",
        ),
    ]


class FGDCContactInfo(FGDCElement):
    elements = [
        FGDCElement(
            name="individual-name",
            search_paths=[
                "cntperp/cntorg/text()",
                "cntorgp/cntper/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="organisation-name",
            search_paths=[
                "cntperp/cntorg/text()",
                "cntorgp/cntorg/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="position-name",
            search_paths=[
                "cntpos/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="contact-address",
            search_paths=[
                "cntaddr",
            ],
            multiplicity="*",
            elements = [
                FGDCElement(
                    name="addrtype",
                    search_paths=[
                        "addrtype/text()",
                    ],
                    multiplicity="0..1",
                ),
                FGDCElement(
                    name="address",
                    search_paths=[
                        "address/text()",
                    ],
                    multiplicity="*",
                ),
                FGDCElement(
                    name="city",
                    search_paths=[
                        "city/text()",
                    ],
                    multiplicity="0..1",
                ),
                FGDCElement(
                    name="state",
                    search_paths=[
                        "state/text()",
                    ],
                    multiplicity="0..1",
                ),
                FGDCElement(
                    name="postal",
                    search_paths=[
                        "postal/text()",
                    ],
                    multiplicity="0..1",
                ),
                FGDCElement(
                    name="country",
                    search_paths=[
                        "country/text()",
                    ],
                    multiplicity="0..1",
                ),
            ]
        ),
        FGDCElement(
            name="telephone",
            search_paths=[
                "cntvoice/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="fax",
            search_paths=[
                "cntfax/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="email",
            search_paths=[
                "cntemail/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="hours-of-service",
            search_paths=[
                "hours/text()",
            ],
            multiplicity="0..1",
        ),
        FGDCElement(
            name="contact-instructions",
            search_paths=[
                "cntinst/text()",
            ],
            multiplicity="0..1",
        )
    ]


class FGDCCitation(FGDCElement):
    elements = [
        FGDCElement(
            name="origin",
            search_paths="origin/text()",
            multiplicity="*",
        ),
        FGDCElement(
            name="pubdate",
            search_paths="pubdate/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="title",
            search_paths="title/text()",
            multiplicity="1",
        ),
        FGDCElement(
            name="edition",
            search_paths="edition/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="geoform",
            search_paths="geoform/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="sername",
            search_paths="serinfo/sername/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="issue",
            search_paths="serinfo/issue/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="pubplace",
            search_paths="pubinfo/pubplace/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="publish",
            search_paths="pubinfo/publish/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="othercit",
            search_paths="othercit/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="onlink",
            search_paths="onlink/text()",
            multiplicity="*",
        ),
   ]


class FGDCSingleDates(FGDCElement):
    elements = [
        FGDCElement(
            name="caldate",
            search_paths="caldate/text()",
            multiplicity="1",
        ),
        FGDCElement(
            name="time",
            search_paths="time/text()",
            multiplicity="0..1",
        ),
    ]


class FGDCRangeOfDates(FGDCElement):
    elements = [
        FGDCElement(
            name="begdate",
            search_paths="begdate/text()",
            multiplicity="1",
        ),
        FGDCElement(
            name="begtime",
            search_paths="begtime/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="enddate",
            search_paths="enddate/text()",
            multiplicity="1",
        ),
        FGDCElement(
            name="endtime",
            search_paths="endtime/text()",
            multiplicity="0..1",
        ),
    ]


class FGDCBoundingBox(FGDCElement):
    elements = [
        FGDCElement(
            name="west",
            search_paths=[
                "westbc/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="east",
            search_paths=[
                "eastbc/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="north",
            search_paths=[
                "northbc/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="south",
            search_paths=[
                "southbc/text()",
            ],
            multiplicity="1",
        ),
    ]


class FGDCBoundingAltitude(FGDCElement):
    elements = [
        FGDCElement(
            name="minimum-altitude",
            search_paths=[
                "altmin/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="maximum-altitude",
            search_paths=[
                "altmax/text()",
            ],
            multiplicity="1",
        ),
        FGDCElement(
            name="altitude-units",
            search_paths=[
                "altunits/text()",
            ],
            multiplicity="1",
        ),
    ]


class FGDCKeywords(FGDCElement):
    elements = [
        FGDCElement(
            name="theme-keyword",
            search_paths=[
                "theme/themekey/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="theme-thesaurus",
            search_paths=[
                "theme/themekt/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="place-keyword",
            search_paths=[
                "place/placekey/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="place-thesaurus",
            search_paths=[
                "place/placekt/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="stratum-keyword",
            search_paths=[
                "stratum/stratumkey/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="stratum-thesaurus",
            search_paths=[
                "stratum/stratumkt/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="temporal-keyword",
            search_paths=[
                "temporal/temporalkey/text()",
            ],
            multiplicity="*",
        ),
        FGDCElement(
            name="temporal-thesaurus",
            search_paths=[
                "temporal/temporalkt/text()",
            ],
            multiplicity="*",
        ),
   ]


class FGDCGeologicAge(FGDCElement):
    elements = [
        FGDCElement(
            name="geologic-time-scale",
            search_paths="geolscal/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="geologic-age-estimate",
            search_paths="geolest/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="geologic-age-uncertainty",
            search_paths="geolun/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="geologic-age-explanation",
            search_paths="geolexpl/text()",
            multiplicity="0..1",
        ),
    ]


class FGDCPlanarCoordinateInformation(FGDCElement):
    elements = [
        FGDCElement(
            name="planar-coordinate-encoding-method",
            search_paths="plance/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="abscissa-resolution",
            search_paths="coordrep/absres/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="ordinate-resolution",
            search_paths="coordrep/ordres/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="planar-distance-units",
            search_paths="plandu/text()",
            multiplicity="0..1",
        ),
    ]


class FGDCDocument(MappedXmlDocument):
    elements = [
        FGDCElement(
            name="guid",
            search_paths="idinfo/datasetid/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="title",
            search_paths="idinfo/citation/citeinfo/title/text()",
            multiplicity="0..1",
        ),
        FGDCEntityAndAttribute(
            name="entity-and-attribute",
            search_paths="eainfo/detailed",
            multiplicity="*",
        ),
        FGDCResourceLocator(
            name="resource-locator",
            search_paths="distinfo/stdorder/digform",
            multiplicity="*",
        ),
        FGDCElement(
            name="contact-email",
            search_paths="idinfo/ptcontac/cntinfo/cntemail/text()",
            multiplicity="*",
        ),
        FGDCCitation(
            name="idinfo-citation",
            search_paths="idinfo/citation/citeinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="abstract",
            search_paths="idinfo/descript/abstract/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="purpose",
            search_paths="idinfo/descript/purpose/text()",
            multiplicity="0..1",
        ),
        FGDCSingleDates(
            name="idinfo-single-dates",
            search_paths=[
                "idinfo/timeperd/timeinfo/sngdate",
                "idinfo/timeperd/timeinfo/mdattim/sngdate",
            ],
            multiplicity="*",
        ),
        FGDCRangeOfDates(
            name="idinfo-range-of-dates",
            search_paths="idinfo/timeperd/timeinfo/rngdates",
            multiplicity="0..1",
        ),
        FGDCGeologicAge(
            name="geologic-age",
            search_paths=[
                "idinfo/timeperd/timeinfo/sngdate/geolage",
                "idinfo/timeperd/timeinfo/mdattim/geolage",
            ],
            multiplicity="*",
        ),
        FGDCGeologicAge(
            name="beginning-geologic-age",
            search_paths="idinfo/timeperd/timeinfo/rngdates/beggeol/geolage",
            multiplicity="0..1",
        ),
        FGDCGeologicAge(
            name="ending-geologic-age",
            search_paths="idinfo/timeperd/timeinfo/rngdates/endgeol/geolage",
            multiplicity="0..1",
        ),
        FGDCCitation(
            name="geologic-citation",
            search_paths="idinfo/timeperd/timeinfo/sngdate/geolage/geolcit/citeinfo",
            multiplicity="0..1",
        ),
        FGDCCitation(
            name="beginning-geologic-citation",
            search_paths="idinfo/timeperd/timeinfo/rngdates/beggeol/geolage/geolcit/citeinfo",
            multiplicity="0..1",
        ),
        FGDCCitation(
            name="ending-geologic-citation",
            search_paths="idinfo/timeperd/timeinfo/rngdates/endgeol/geolage/geolcit/citeinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="current",
            search_paths="idinfo/timeperd/current/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="progress",
            search_paths="idinfo/status/progress/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="update",
            search_paths="idinfo/status/update/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="geographic-extent-description",
            search_paths="idinfo/spdom/descgeog/text()",
            multiplicity="0..1",
        ),
        FGDCBoundingBox(
            name="bbox",
            search_paths="idinfo/spdom/bounding",
            multiplicity="*",
        ),
        FGDCBoundingAltitude(
            name="bounding-altitude",
            search_paths="idinfo/spdom/bounding/boundalt",
            multiplicity="*",
        ),
        FGDCKeywords(
            name="keywords",
            search_paths="idinfo/keywords",
            multiplicity="*",
        ),
        FGDCElement(
            name="taxon-keywords",
            search_paths="idinfo/taxonomy/taxonkey/text()",
            multiplicity="*",
        ),
        FGDCCitation(
            name="classsys-citation",
            search_paths="idinfo/taxonomy/taxonsys/classsys/classcit/citeinfo",
            multiplicity="0..1",
        ),
        FGDCCitation(
            name="idref-citation",
            search_paths="idinfo/taxonomy/taxonsys/idref/citeinfo",
            multiplicity="0..1",
        ),
        FGDCContactInfo(
            name="ider-contact",
            search_paths="idinfo/taxonomy/taxonsys/ider/cntinfo",
            multiplicity="0..1",
        ),
        FGDCContactInfo(
            name="vouchers-contact",
            search_paths="idinfo/taxonomy/taxonsys/vouchers/reposit/cntinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="vouchers-specimen",
            search_paths="idinfo/taxonomy/taxonsys/vouchers/specimen/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="access-constraints",
            search_paths="idinfo/accconst/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="use-constraints",
            search_paths="idinfo/useconst/text()",
            multiplicity="0..1",
        ),
        FGDCContactInfo(
            name="point-of-contact",
            search_paths="idinfo/ptcontac/cntinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="credit",
            search_paths="idinfo/datacred/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="native-dataset-environment",
            search_paths="idinfo/native/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="attribute-accuracy-report",
            search_paths="dataqual/attracc/attraccr/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="completeness-report",
            search_paths="dataqual/complete/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="methodology-type",
            search_paths="dataqual/lineage/method/methtype/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="methodology-description",
            search_paths="dataqual/lineage/method/methdesc/text()",
            multiplicity="0..1",
        ),
        FGDCCitation(
            name="lineage-citation",
            search_paths="dataqual/lineage/method/methcite/citeinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="source-scale-denominator",
            search_paths="dataqual/lineage/srcinfo/srcscale/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="type-of-source-media",
            search_paths="dataqual/lineage/srcinfo/typesrc/text()",
            multiplicity="0..1",
        ),
        FGDCSingleDates(
            name="lineage-single-dates",
            search_paths=[
                "dataqual/lineage/srcinfo/srctime/timeinfo/sngdate",
                "dataqual/lineage/srcinfo/srctime/timeinfo/mdattim/sngdate",
            ],
            multiplicity="*",
        ),
        FGDCRangeOfDates(
            name="lineage-range-of-dates",
            search_paths="dataqual/lineage/srcinfo/srctime/timeinfo/rngdates",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="source-currentness-reference",
            search_paths="dataqual/lineage/srcinfo/srctime/srccurr/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="source-citation-abbreviation",
            search_paths="dataqual/lineage/srcinfo/srccitea/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="source-contribution",
            search_paths="dataqual/lineage/srcinfo/srccontr/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="process-description",
            search_paths="dataqual/lineage/procstep/procdesc/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="process-date",
            search_paths="dataqual/lineage/procstep/procdate/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="map-projection-name",
            search_paths="spref/horizsys/planar/mapproj/mapprojn/text()",
            multiplicity="0..1",
        ),
        FGDCPlanarCoordinateInformation(
            name="planar-coordinate-information",
            search_paths="spref/horizsys/planar/planci",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="horizontal-datum-name",
            search_paths="spref/horizsys/geodatic/horizdn/text()",
            multiplicity="0..1",
        ),
        FGDCContactInfo(
            name="distributor",
            search_paths="distinfo/distrib/cntinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="distribution-liability",
            search_paths="distinfo/distliab/text()",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="metd",
            search_paths="metainfo/metd/text()",
            multiplicity="0..1",
        ),
        FGDCContactInfo(
            name="metadata-contact",
            search_paths="metainfo/metc/cntinfo",
            multiplicity="0..1",
        ),
        FGDCElement(
            name="metadata-standard-name",
            search_paths="metainfo/metstdn/text()",
            multiplicity="0..1",
        ),
        FGDCSingleDates(
            name="available-single-dates",
            search_paths=[
                "distInfo/availabl/timeinfo/sngdate",
                "distInfo/availabl/timeinfo/mdattim/sngdate",
            ],
            multiplicity="*",
        ),
        FGDCRangeOfDates(
            name="available-range-of-dates",
            search_paths="distInfo/availabl/timeinfo/rngdates",
            multiplicity="0..1",
        ),
    ]


    def infer_values(self, values):
        self.infer_metadata_date(values)
        self.infer_tags(values)
        self.infer_thesaurus(values)
        self.infer_contact(values)
        return values

    def infer_tags(self, values):
        tags = []
        theme_keywords = []
        place_keywords = []
        stratum_keywords = []
        temporal_keywords = []

        if len(values.get('keywords', [])):
            key = values['keywords'][0]

        for theme in key.get('theme-keyword', []):
            if re.match('^[\w .-]+$', theme) is None:
                theme = munge_tag(theme)
            if theme not in tags:
                tags.append(theme)
            if theme not in theme_keywords:
                theme_keywords.append(theme)
        for place in key.get('place-keyword', []):
            if re.match('^[\w .-]+$', place) is None:
                place = munge_tag(place)
            if place not in place_keywords:
                place_keywords.append(place)
        for stratum in key.get('stratum-keyword', []):
            if re.match('^[\w .-]+$', stratum) is None:
                stratum = munge_tag(stratum)
            if stratum not in stratum_keywords:
                stratum_keywords.append(stratum)
        for temporal in key.get('temporal-keyword', []):
            if re.match('^[\w .-]+$', temporal) is None:
                temporal = munge_tag(temporal)
            if temporal not in temporal_keywords:
                temporal_keywords.append(temporal)

        values['tags'] = tags
        values['theme-keywords'] = theme_keywords
        values['place-keywords'] = place_keywords
        values['stratum-keywords'] = stratum_keywords
        values['temporal-keywords'] = temporal_keywords

    def infer_thesaurus(self, values):
        theme_thesaurus = []
        place_thesaurus = []
        stratum_thesaurus = []
        temporal_thesaurus = []
        taxon_thesaurus = []
        if len(values.get('keywords', [])):
            key = values['keywords'][0]
        for item in key.get('theme-thesaurus', []):
            if item not in theme_thesaurus:
                theme_thesaurus.append(item)
        for item in key.get('place-thesaurus', []):
            if item not in place_thesaurus:
                place_thesaurus.append(item)
        for item in key.get('stratum-thesaurus', []):
            if item not in stratum_thesaurus:
                stratum_thesaurus.append(item)
        for item in key.get('temporal-thesaurus', []):
            if item not in temporal_thesaurus:
                temporal_thesaurus.append(item)
        values['theme-thesaurus'] = theme_thesaurus
        values['place-thesaurus'] = place_thesaurus
        values['stratum-thesaurus'] = stratum_thesaurus
        values['temporal-thesaurus'] = temporal_thesaurus

    def infer_contact(self, values):
        value = '' 
        contact = values.get('point-of-contact', {})
        if contact:
            if contact['individual-name']:
                value = contact['individual-name']
            elif contact['organisation-name']:
                value = contact['organisation-name']
        values['contact'] = value

    def infer_metadata_date(self, values):
        value = ''
        dates = []

        if len(values.get('idinfo-citation', [])):
            citation_date = values['idinfo-citation'].get('pubdate')
            if citation_date and citation_date != 'N/A':
                dates.append(citation_date)

        if len(values.get('idinfo-range-of-dates', [])):
            enddate = values['idinfo-range-of-dates'].get('enddate')
            if enddate and enddate != 'N/A':
                dates.append(enddate)

        if values['metd'] and values['metd'] != 'N/A':
            dates.append(values['metd'])

        if len(dates):
            if len(dates) > 1:
                dates.sort(reverse=True)
            value = dates[0]

        values['metadata-date'] = value
