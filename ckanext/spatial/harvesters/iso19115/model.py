from lxml import etree
from owslib.util import element_to_string
import six
import json
import copy
import datetime
import re
import logging
log = logging.getLogger(__name__)

# Py2 vs Py3 encoding
def _encode(element):
    import sys 
    if sys.version_info[0] < 3:
        return element.encode('utf-8')
    else:
        return str(element)

from ckanext.spatial.model.harvested_metadata import MappedXmlElement, MappedXmlDocument

class ISOElement(MappedXmlElement):

    namespaces = {
        "gts": "http://www.isotc211.org/2005/gts",
        # "gml": "http://www.opengis.net/gml",
        "gml32": "http://www.opengis.net/gml/3.2",
        "gmx": "http://www.isotc211.org/2005/gmx",
        "gsr": "http://www.isotc211.org/2005/gsr",
        "gss": "http://www.isotc211.org/2005/gss",
        # "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        # "srv": "http://www.isotc211.org/2005/srv",
        # ISO19115-3
        "xlink": "http://www.w3.org/1999/xlink",
        "gml": "http://www.opengis.net/gml/3.2",
        "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
        # "fcc": "http://standards.iso.org/iso/19110/fcc/1.0",
        "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
        "gcx": "http://standards.iso.org/iso/19115/-3/gcx/1.0",
        "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
        "lan": "http://standards.iso.org/iso/19115/-3/lan/1.0",
        # "mac": "http://standards.iso.org/iso/19115/-3/mac/2.0",
        # "mas": "http://standards.iso.org/iso/19115/-3/mas/1.0",
        "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
        "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
        "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0",
        # "mdq": "http://standards.iso.org/iso/19157/-2/mdq/1.0",
        "mds": "http://standards.iso.org/iso/19115/-3/mds/2.0",
        "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
        # "mpc": "http://standards.iso.org/iso/19115/-3/mpc/1.0",
        # "mrc": "http://standards.iso.org/iso/19115/-3/mrc/2.0",
        "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
        "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
        "mrl": "http://standards.iso.org/iso/19115/-3/mrl/2.0",
        "mrs": "http://standards.iso.org/iso/19115/-3/mrs/1.0",
        # "msr": "http://standards.iso.org/iso/19115/-3/msr/2.0",
        "srv": "http://standards.iso.org/iso/19115/-3/srv/2.0",
        "xml": "http://www.w3.org/XML/1998/namespace",
        # "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        # "dqc": "http://standards.iso.org/iso/19157/-2/dqc/1.0",

    }


class ISOResourceLocator(ISOElement):

    elements = [
        ISOElement(
            name="url",
            search_paths=[
                "gmd:linkage/gmd:URL/text()",
                # 19115-3
                "cit:linkage/gco:CharacterString/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="function",
            search_paths=[
                "gmd:function/gmd:CI_OnLineFunctionCode/@codeListValue",
                # 19115-3
                "cit:function/cit:CI_OnLineFunctionCode/@codeListValue",
                "cit:function/cit:CI_OnLineFunctionCode/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="name",
            search_paths=[
                "gmd:name/gco:CharacterString/text()",
                "gmd:name/gmx:MimeFileType/text()",
                # 19115-3
                "cit:name/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="description",
            search_paths=[
                "gmd:description/gco:CharacterString/text()",
                # 19115-3
                "cit:description/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="protocol",
            search_paths=[
                "gmd:protocol/gco:CharacterString/text()",
                # 19115-3
                "cit:protocol/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        # 19115-3
        ISOElement(
            name="protocol-request",
            search_paths=[
                # 19115-3
                "cit:protocolRequest/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="application-profile",
            search_paths=[
                # 19115-3
                "cit:applicationProfile/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="distribution-format",
            search_paths=[
                "ancestor::mrd:MD_DigitalTransferOptions/mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:title/gco:CharacterString/text()"
            ],
            multiplicity="*"
        ),
        ISOElement(
            name="distributor-format",
            search_paths=[
                "ancestor::mrd:MD_Distributor/mrd:distributorFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:title/gco:CharacterString/text()"
            ],
            multiplicity="*"
        ),

        ISOElement(
            name="offline",
            search_paths=[
                "ancestor::mrd:MD_DigitalTransferOptions/mrd:offLine/mrd:MD_Medium/cit:CI_Citation/cit:title/gco:CharacterString/text()"
            ],
            multiplicity="*"
        ),
        ISOElement(
            name="transfer-size",
            search_paths=[
                "ancestor::mrd:MD_DigitalTransferOptions/mrd:transferSize/gco:Real/text()"
            ],
            multiplicity="0..1"
        ),
        ISOElement(
            name="units-of-distribution",
            search_paths=[
                "ancestor::mrd:MD_DigitalTransferOptions/mrd:unitsOfDistribution/gco:CharacterString/text()"
            ],
            multiplicity="0..1"
        )
    ]


class ISOResponsibleParty(ISOElement):

    elements = [
        ISOElement(
            name="individual-name",
            search_paths=[
                "gmd:individualName/gco:CharacterString/text()",
                # 19115-3
                "cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()",
                "cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:name/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="organisation-name",
            search_paths=[
                "gmd:organisationName/gco:CharacterString/text()",
                # 19115-3
                "cit:party/cit:CI_Organisation/cit:name/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="position-name",
            search_paths=[
                "gmd:positionName/gco:CharacterString/text()",
                # 19115-3
                "cit:party/cit:CI_Individual/cit:positionName/gco:CharacterString/text()",
                "cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:positionName/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="contact-info",
            search_paths=[
                "gmd:contactInfo/gmd:CI_Contact",
                # 19115-3
                "cit:party/cit:CI_Individual/cit:contactInfo/cit:CI_Contact",
                "cit:party/cit:CI_Organisation/cit:individual/cit:CI_Individual/cit:contactInfo/cit:CI_Contact",
                "cit:party/cit:CI_Organisation/cit:contactInfo/cit:CI_Contact",
            ],
            multiplicity="0..1",
            elements = [
                ISOElement(
                    name="email",
                    search_paths=[
                        "gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString/text()",
                        # 19115-3
                        "cit:address/cit:CI_Address/cit:electronicMailAddress/gco:CharacterString/text()",
                    ],
                    multiplicity="0..1",
                ),
                ISOResourceLocator(
                    name="online-resource",
                    search_paths=[
                        "gmd:onlineResource/gmd:CI_OnlineResource",
                        # 19115-3
                        "cit:onlineResource/cit:CI_OnlineResource",
                    ],
                    multiplicity="0..1",
                ),

            ]
        ),
        ISOElement(
            name="role",
            search_paths=[
                "gmd:role/gmd:CI_RoleCode/@codeListValue",
                # 19115-3
                "gmd:role/gmd:CI_RoleCode/text()",
                "cit:role/cit:CI_RoleCode/@codeListValue",
                "cit:role/cit:CI_RoleCode/text()",
            ],
            multiplicity="0..1",
        ),
    ]


class ISODataFormat(ISOElement):

    elements = [
        ISOElement(
            name="name",
            search_paths=[
                "gmd:name/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="version",
            search_paths=[
                "gmd:version/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
    ]


class ISOReferenceDate(ISOElement):

    elements = [
        ISOElement(
            name="type",
            search_paths=[
                "gmd:dateType/gmd:CI_DateTypeCode/@codeListValue",
                "gmd:dateType/gmd:CI_DateTypeCode/text()",
                # 19115-3
                "cit:dateType/cit:CI_DateTypeCode/@codeListValue",
                "cit:dateType/cit:CI_DateTypeCode/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="value",
            search_paths=[
                "gmd:date/gco:Date/text()",
                "gmd:date/gco:DateTime/text()",
                # 19115-3
                "cit:date/gco:Date/text()",
                "cit:date/gco:DateTime/text()",
            ],
            multiplicity="1",
            #TODO check multiplicity="0..1",
        ),
    ]

class ISOCoupledResources(ISOElement):

    elements = [
        ISOElement(
            name="title",
            search_paths=[
                "@xlink:title",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="href",
            search_paths=[
                "@xlink:href",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="uuid",
            search_paths=[
                "@uuidref",
            ],
            multiplicity="*",
        ),

    ]


class ISOBoundingBox(ISOElement):

    elements = [
        ISOElement(
            name="west",
            search_paths=[
                "gmd:westBoundLongitude/gco:Decimal/text()",
                # ISO19115-3
                "gex:westBoundLongitude/gco:Decimal/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="east",
            search_paths=[
                "gmd:eastBoundLongitude/gco:Decimal/text()",
                # ISO19115-3
                "gex:eastBoundLongitude/gco:Decimal/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="north",
            search_paths=[
                "gmd:northBoundLatitude/gco:Decimal/text()",
                # ISO19115-3
                "gex:northBoundLatitude/gco:Decimal/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="south",
            search_paths=[
                "gmd:southBoundLatitude/gco:Decimal/text()",
                # ISO19115-3
                "gex:southBoundLatitude/gco:Decimal/text()",
            ],
            multiplicity="1",
        ),
    ]

class ISOBrowseGraphic(ISOElement):

    elements = [
        ISOElement(
            name="file",
            search_paths=[
                "gmd:fileName/gco:CharacterString/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="description",
            search_paths=[
                "gmd:fileDescription/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="type",
            search_paths=[
                "gmd:fileType/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
    ]

# ISO19115-3
class ISOLocalised(ISOElement):

    elements = [
        ISOElement(
            name="default",
            search_paths=[
                "gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name='local',
            search_paths=[
                "gmd:PT_FreeText/gmd:textGroup",
                "lan:PT_FreeText/lan:textGroup",
            ],
            multiplicity="0..1",
            elements=[
                ISOElement(
                    name="value",
                    search_paths=[
                        "gmd:LocalisedCharacterString/text()",
                        "lan:LocalisedCharacterString/text()",
                    ],
                    multiplicity="0..1",
                ),
                ISOElement(
                    name="language_code",
                    search_paths=[
                        "gmd:LocalisedCharacterString/@locale",
                        "lan:LocalisedCharacterString/@locale",
                    ],
                    multiplicity="0..1",
                )
            ]
        )
    ]


class ISOKeyword(ISOElement):

    elements = [
        ISOElement(
            name="keyword",
            search_paths=[
                #"gmd:keyword/gco:CharacterString/text()",
                "gmd:keyword",
                # ISO19115-3
                "mri:keyword",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="type",
            search_paths=[
                "gmd:type/gmd:MD_KeywordTypeCode/@codeListValue",
                "gmd:type/gmd:MD_KeywordTypeCode/text()",
                # ISO19115-3
                "mri:type/mri:MD_KeywordTypeCode/@codeListValue",
                "mri:type/mri:MD_KeywordTypeCode/text()",
            ],
            multiplicity="0..1",
        ),
        # If Thesaurus information is needed at some point, this is the
        # place to add it
    ]

    def infer_keywords(self, values):
        keywords = values['keywords']

        defaultLangKey = cleanLangKey(values.get('metadata-language', 'en'))

        value = []
        if isinstance(keywords, list):
            for klist in keywords:
                ktype = klist.get('type')
                for item in klist.get('keywords', []):
                    LangDict = local_to_dict(item, defaultLangKey)
                    value.append({
                        'keyword': json.dumps(LangDict),
                        'type': ktype
                    })
        else:
            for item in keywords:
                LangDict = local_to_dict(item, defaultLangKey)
                value.append({
                    'keyword': json.dumps(LangDict),
                    'type': item.get('type')
                })
        values['keywords'] = value

    def infer_values(self, values):
        #iso19139-3
        self.infer_keywords(values)
        return values

# ISO19115-3
class ISOTemporalExtent(ISOElement):

    elements = [
        ISOElement(name="begin",
                   search_paths=[
                       "gml:beginPosition/text()",
                       "gml32:beginPosition/text()",
                   ],
                   multiplicity="0..1"
                   ),
        ISOElement(name="end",
                   search_paths=[
                       "gml:endPosition/text()",
                       "gml32:endPosition/text()",
                   ],
                   multiplicity="0..1"
                   )
    ]

# ISO19115-3
class ISOVerticalExtent(ISOElement):

    elements = [
        ISOElement(name="min",
                   search_paths=[
                       "gmd:minimumValue/gco:Real/text()",
                       "gex:minimumValue/gco:Real/text()",
                   ],
                   multiplicity="0..1"
                   ),
        ISOElement(name="max",
                   search_paths=[
                       "gmd:maximumValue/gco:Real/text()",
                       "gex:maximumValue/gco:Real/text()",
                   ],
                   multiplicity="0..1"
                   )
    ]

# ISO19115-3
class ISOIdentifier(ISOElement):

    elements = [
        ISOElement(
            name="code",
            search_paths=[
                # ISO19115-3
                "mcc:code/gco:CharacterString/text()",
                "mcc:code/gcx:Anchor/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="authority",
            search_paths=[
                # ISO19115-3
                "mcc:authority/cit:CI_Citation/cit:title/gco:CharacterString/text()",
                "mcc:authority/cit:CI_Citation/cit:title/gcx:Anchor/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="code-space",
            search_paths=[
                # ISO19115-3
                "mcc:codeSpace/gco:CharacterString/text()",
                "mcc:codeSpace/gcx:Anchor/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="version",
            search_paths=[
                # ISO19115-3
                "mcc:version/gco:CharacterString/text()",
                "mcc:version/gcx:Anchor/text()",
            ],
            multiplicity="0..1",
        ),
    ]

class ISOUsage(ISOElement):

    elements = [
        ISOElement(
            name="usage",
            search_paths=[
                "gmd:specificUsage/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOResponsibleParty(
            name="contact-info",
            search_paths=[
                "gmd:userContactInfo/gmd:CI_ResponsibleParty",
            ],
            multiplicity="0..1",
        ),
    ]

class ISOAggregationInfo(ISOElement):

    elements = [
        ISOElement(
            name="aggregate-dataset-name",
            search_paths=[
                "gmd:aggregateDatasetName/gmd:CI_Citation/gmd:title/gco:CharacterString/text()",
                # ISO19115-3
                "mri:name/cit:CI_Citation/cit:title/gco:CharacterString/text()"
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="aggregate-dataset-identifier",
            search_paths=[
                "gmd:aggregateDatasetIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                # ISO19115-3
                "mri:name/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()"
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="association-type",
            search_paths=[
                "gmd:associationType/gmd:DS_AssociationTypeCode/@codeListValue",
                "gmd:associationType/gmd:DS_AssociationTypeCode/text()",
                # ISO19115-3
                "mri:associationType/mri:DS_AssociationTypeCode/@codeListValue",
                "mri:associationType/mri:DS_AssociationTypeCode/text()"
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="initiative-type",
            search_paths=[
                "gmd:initiativeType/gmd:DS_InitiativeTypeCode/@codeListValue",
                "gmd:initiativeType/gmd:DS_InitiativeTypeCode/text()",
                # ISO19115-3
                "mri:initiativeType/mri:DS_InitiativeTypeCode/@codeListValue",
                "mri:initiativeType/mri:DS_InitiativeTypeCode/text()",
            ],
            multiplicity="0..1",
        ),
   ]

# ISO19115-3
class ISOCitation(ISOElement):
    elements = [
        ISOElement(
            name="type",
            search_paths=[
                # 19115-3
                "ancestor::mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/@codeListValue",
                "ancestor::mdb:MD_Metadata/mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/text()",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="id",
            search_paths=[
                # 19115-3
                "ancestor::mdb:MD_Metadata/mdb:metadataIdentifier/mcc:MD_Identifier",
            ],
            multiplicity="0..1",
            elements=[
                ISOElement(
                    name="code",
                    search_paths=[
                        # ISO19115-3
                        "mcc:code/gco:CharacterString/text()",
                        "mcc:code/gcx:Anchor/text()",
                    ],
                    multiplicity="0..1",
                ),
                ISOElement(
                    name="authority",
                    search_paths=[
                        # ISO19115-3
                        "mcc:authority/cit:CI_Citation/cit:title/gco:CharacterString/text()",
                        "mcc:authority/cit:CI_Citation/cit:title/gcx:Anchor/text()",
                    ],
                    multiplicity="0..1",
                ),
                ISOElement(
                    name="code-space",
                    search_paths=[
                        # ISO19115-3
                        "mcc:codeSpace/gco:CharacterString/text()",
                        "mcc:codeSpace/gcx:Anchor/text()",
                    ],
                    multiplicity="0..1",
                ),
                ISOElement(
                    name="version",
                    search_paths=[
                        # ISO19115-3
                        "mcc:version/gco:CharacterString/text()",
                        "mcc:version/gcx:Anchor/text()",
                    ],
                    multiplicity="0..1",
                ),
            ]
        ),
        ISOResponsibleParty(
            name="author",
            search_paths=[
                # 19115-3
                "cit:citedResponsibleParty/cit:CI_Responsibility"
            ],
            multiplicity="1..*",
        ),
        ISOReferenceDate(
            name="issued",
            search_paths=[
                # 19115-3
                "ancestor::mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:date/cit:CI_Date[cit:dateType/cit:CI_DateTypeCode/@codeListValue != 'creation']",
                "ancestor::mdb:MD_Metadata/mdb:dateInfo/cit:CI_Date"
            ],
            multiplicity="1..*",
        ),
        ISOLocalised(
            name="abstract",
            search_paths=[
                # ISO19115-3
                "ancestor::mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract",
                "ancestor::mdb:MD_Metadata/mdb:identificationInfo/srv:SV_ServiceIdentification/mri:abstract",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="publisher",
            search_paths=[
                # 19115-3
                "cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='publisher']/cit:party/cit:CI_Individual/cit:name/gco:CharacterString/text()[boolean(.)]",
                "cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='publisher']/cit:party/cit:CI_Organisation/cit:name/gco:CharacterString/text()[boolean(.)]",

            ],
            multiplicity="1",
        ),
        ISOLocalised(
            name="title",
            search_paths=[
                # 19115-3
                "cit:title",
            ],
            multiplicity="1",
        ),
    ]

    def infer_values(self, values):
        self.infer_citation(values)
        return values
    
    def infer_citation(self, values):
        if 'citation' not in values or not values['citation']:
            return   
        value = values['citation'][0]
        if len(value['issued']):
            dates = value['issued']
            if isinstance(dates[0], str):
                dates.sort(reverse=True)
            else:  # it's an object
                dates = sorted(dates, key=lambda k: k['value'], reverse=True)
            issued_date = str(dates[0]['value'])
            value['issued'] = [{"date-parts": [issued_date[:4], issued_date[5:7], issued_date[8:10]]}]
        value['id'] = calculate_identifier(value['id'])

        # remove duplicate entries
        author_list = [
            {"individual-name": x['individual-name'],
             "organisation-name": x['organisation-name'],
            } for x in value['author']]
        author_list = [i for n, i in enumerate(author_list) if i not in author_list[n + 1:]]

        #clear author list
        value['author'] = []

        for author in author_list:
            ind = author.get('individual-name')
            org = author.get('organisation-name')
            if ind:
                name_list = ind.split()
                value['author'].append({
                    "given": ' '.join(name_list[0:-1]),
                    "family": name_list[-1]
                })
            else:
                value['author'].append({"literal": org})

        defaultLangKey = cleanLangKey(values.get('metadata-language', 'en'))
        value['title'] = local_to_dict(value['title'], defaultLangKey)
        value['abstract'] = local_to_dict(value['abstract'], defaultLangKey)

        identifier = values.get('unique-resource-identifier-full', {})
        if identifier:
            doi = calculate_identifier(identifier)
            doi = re.sub(r'^http.*doi\.org/', '', doi, flags=re.IGNORECASE)  # strip https://doi.org/ and the like
            if doi and re.match(r'^10.\d{4,9}\/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE):
                value['DOI'] = doi
        # TODO: could we have more then one doi?
        import ckan.lib.munge as munge
        from ckan.lib.helpers import url_for
        field = {}
        for lang in ['fr', 'en']:
            field[lang] = copy(value)
            title = field[lang]['title']
            field[lang]['title'] = title.get(lang)
            abstract = field[lang]['abstract']
            field[lang]['abstract'] = abstract.get(lang)
            field[lang]['language'] = lang
            field[lang]['URL'] = url_for(
                controller='dataset',
                action='read',
                id=munge.munge_name(values.get('guid', '')),
                local=lang,
                qualified=True
            )
            field[lang] = json.dumps([field[lang]])
            # the dump converts utf-8 escape sequences to unicode escape
            # sequences so we have to convert back again
            # if(field[lang] and re.search(r'\\u[0-9a-fA-F]{4}', field[lang])):
            #     field[lang] = field[lang].decode("raw_unicode_escape")
            # double escape any double quotes that are already escaped
            field[lang] = field[lang].replace('\"', '\\"')
        values['citation'] = json.dumps(field)


class ISO19115Document(MappedXmlDocument):

    # Attribute specifications from "XPaths for GEMINI" by Peter Parslow.

    elements = [
        # TODO check why commented out
        # ISOElement(
        #     name="guid",
        #     search_paths="gmd:fileIdentifier/gco:CharacterString/text()",
        #     multiplicity="0..1",
        # ),
        ISOIdentifier(
            name="guid",
            search_paths=[
                # ISO 19139
                "gmd:fileIdentifier/gco:CharacterString/text()",
                # 19115-3
                "mdb:metadataIdentifier/mcc:MD_Identifier"
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="metadata-language",
            search_paths=[
                "gmd:language/gmd:LanguageCode/@codeListValue",
                "gmd:language/gmd:LanguageCode/text()",
                "gmd:language/gco:CharacterString/text()",
                # 19115-3
                "mdb:defaultLocale/lan:PT_Locale/lan:language/lan:LanguageCode/@codeListValue",
                "mdb:defaultLocale/lan:PT_Locale/lan:language/lan:LanguageCode/text()",
            ],
            multiplicity="1",
            # TODO check why changed
            # multiplicity="0..1",
        ),
        ISOElement(
            name="metadata-standard-name",
            search_paths="gmd:metadataStandardName/gco:CharacterString/text()",
            multiplicity="0..1",
        ),
        ISOElement(
            name="metadata-standard-version",
            search_paths="gmd:metadataStandardVersion/gco:CharacterString/text()",
            multiplicity="0..1",
        ),
        ISOElement(
            name="resource-type",
            search_paths=[
                "gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue",
                "gmd:hierarchyLevel/gmd:MD_ScopeCode/text()",
                # 19115-3
                "mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/@codeListValue",
                "mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode/text()",
            ],
            multiplicity="*",
        ),
        ISOResponsibleParty(
            name="metadata-point-of-contact",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty",
                # 19115-3
                "mdb:contact/cit:CI_Responsibility",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='pointOfContact']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='pointOfContact']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceMaintenance/mmi:MD_MaintenanceInformation/mmi:contact/cit:CI_Responsibility",
            ],
            multiplicity="1..*",
        ),
        # 19115-3
        ISOResponsibleParty(
            name="cited-responsible-party",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility",
            ],
            multiplicity="1..*",
        ),
        ISOReferenceDate(
            name="metadata-reference-date",
            search_paths=[
                # 19115-3
                "mdb:dateInfo/cit:CI_Date",
            ],
            multiplicity="1..*",
        ),

        ISOElement(
            name="metadata-date",
            search_paths=[
                "gmd:dateStamp/gco:DateTime/text()",
                "gmd:dateStamp/gco:Date/text()",
                # 19115-3
                "mdb:dateInfo/cit:CI_Date/cit:date/gco:Date/text()",
                "mdb:dateInfo/cit:CI_Date/cit:date/gco:DateTime/text()"
            ],
            multiplicity="1..*",
            #TODO check why changed
            # multiplicity="1",
        ),
        ISOElement(
            name="spatial-reference-system",
            search_paths=[
                "gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        # ISOElement(
        ISOLocalised(
            name="title",
            search_paths=[
                # "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString/text()",
                # "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString/text()",
                # inferred by 'citation'
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:title",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:title",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="alternate-title",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString/text()",
            ],
            multiplicity="*",
        ),
        ISOReferenceDate(
            name="dataset-reference-date",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date",
                # 19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:date/cit:CI_Date"
            ],
            multiplicity="1..*",
        ),
        ISOElement(
            name="unique-resource-identifier",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                "gmd:identificationInfo/gmd:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                # 19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
                "mdb:identificationInfo/mri:SV_ServiceIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        # 19115-3
        ISOIdentifier(
            # this would commonly be a DOI
            name="unique-resource-identifier-full",
            search_paths=[
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier",
                "mdb:identificationInfo/mri:SV_ServiceIdentification/mri:citation/cit:CI_Citation/cit:identifier/mcc:MD_Identifier",
            ],
            multiplicity="0..1",
        ),

        ISOElement(
            name="presentation-form",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:presentationForm/gmd:CI_PresentationFormCode/text()",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:presentationForm/gmd:CI_PresentationFormCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:presentationForm/gmd:CI_PresentationFormCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:presentationForm/gmd:CI_PresentationFormCode/@codeListValue",

            ],
            multiplicity="*",
        ),
        ISOElement(
            name="abstract",
            search_paths=[
                # "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString/text()",
                # "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:abstract/gco:CharacterString/text()",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:abstract",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:abstract",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:abstract",
            ],
            multiplicity="1",
        ),
        ISOElement(
            name="purpose",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:purpose/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:purpose/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOResponsibleParty(
            name="responsible-organisation",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:pointOfContact/gmd:CI_ResponsibleParty",
                "gmd:contact/gmd:CI_ResponsibleParty",
                # 19115-3
                "mdb:contact/cit:CI_Responsibility[cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='pointOfContact' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='originator' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='owner' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='rightsHolder' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='pointOfContact' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='originator' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='owner' and cit:party/cit:CI_Organisation]",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='rightsHolder' and cit:party/cit:CI_Organisation]",
            ],
            multiplicity="1..*",
        ),
        ISOElement(
            name="frequency-of-update",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode/@codeListValue",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode/text()",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceMaintenance/mmi:MD_MaintenanceInformation/mmi:maintenanceAndUpdateFrequency/mmi:MD_MaintenanceFrequencyCode/@codeListValue",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceMaintenance/mmi:MD_MaintenanceInformation/mmi:maintenanceAndUpdateFrequency/mmi:MD_MaintenanceFrequencyCode/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="maintenance-note",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceNote/gco:CharacterString/text()",
                "gmd:identificationInfo/gmd:SV_ServiceIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceNote/gco:CharacterString/text()",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceMaintenance/mmi:MD_MaintenanceInformation/mmi:maintenanceNote/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="progress",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:status/gmd:MD_ProgressCode/@codeListValue",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:status/gmd:MD_ProgressCode/text()",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:status/mcc:MD_ProgressCode/@codeListValue",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:status/mcc:MD_ProgressCode/@codeListValue",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:status/mcc:MD_ProgressCode/text()",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:status/mcc:MD_ProgressCode/text()",
            ],
            multiplicity="*",
        ),
        ISOKeyword(
            name="keywords",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:descriptiveKeywords/mri:MD_Keywords",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:descriptiveKeywords/mri:MD_Keywords",
            ],
            multiplicity="*"
        ),
        ISOElement(
            name="keyword-inspire-theme",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString/text()",
            ],
            multiplicity="*",
        ),
        # Deprecated: kept for backwards compatibilty
        ISOElement(
            name="keyword-controlled-other",
            search_paths=[
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:keywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString/text()",
            ],
            multiplicity="*",
        ),
        ISOUsage(
            name="usage",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceSpecificUsage/gmd:MD_Usage",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceSpecificUsage/gmd:MD_Usage",
            ],
            multiplicity="*"
        ),
        ISOElement(
            name="limitations-on-public-access",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString/text()",
                # 19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/gco:CharacterString/text()",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/gcx:Anchor/text()",
                "mdb:identificationInfo/mri:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/gco:CharacterString/text()",
                "mdb:identificationInfo/mri:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:otherConstraints/gcx:Anchor/text()",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="access-constraints",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode/@codeListValue",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints/gmd:MD_RestrictionCode/text()",
                # 19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode/@codeListValue",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode/@codeListValue",
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode/text()",
                "mdb:identificationInfo/srv:SV_ServiceIdentification/mri:resourceConstraints/mco:MD_LegalConstraints/mco:accessConstraints/mco:MD_RestrictionCode/text()",
            ],
            multiplicity="*",
        ),

        ISOElement(
            name="use-constraints",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useLimitation/gco:CharacterString/text()",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_Constraints/mco:useLimitation/gco:CharacterString/text()",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_LegalConstraints/mco:useLimitation/gco:CharacterString/text()",
            ],
            # TODO check why this has changed
            # multiplicity="*",
            multiplicity="0..1",
        ),
        # 19115-3
        ISOElement(
            name="use-constraints-code",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useConstraints/gmd:MD_RestrictionCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:resourceConstraints/gmd:MD_Constraints/gmd:useConstraints/gmd:MD_RestrictionCode/text()",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_Constraints/mco:useConstraints/mco:MD_RestrictionCode/@codeListValue",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_Constraints/mco:useConstraints/mco:MD_RestrictionCode/text()",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_LegalConstraints/mco:useConstraints/mco:MD_RestrictionCode/@codeListValue",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_LegalConstraints/mco:useConstraints/mco:MD_RestrictionCode/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="legal-constraints-reference-code",
            search_paths=[

                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:resourceConstraints/mco:MD_LegalConstraints/mco:reference/cit:CI_Citation/cit:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),

        ISOAggregationInfo(
            name="aggregation-info",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:aggregationInfo/gmd:MD_AggregateInformation",
                "gmd:identificationInfo/gmd:SV_ServiceIdentification/gmd:aggregationInfo/gmd:MD_AggregateInformation",
                # ISO19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:associatedResource/mri:MD_AssociatedResource"
            ],
            multiplicity="*"
        ),
        ISOElement(
            name="spatial-data-service-type",
            search_paths=[
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:serviceType/gco:LocalName/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="spatial-resolution",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="spatial-resolution-units",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance/@uom",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance/@uom",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="equivalent-scale",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer/text()",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="dataset-language",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:language/gmd:LanguageCode/@codeListValue",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:language/gmd:LanguageCode/@codeListValue",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:language/gmd:LanguageCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:language/gmd:LanguageCode/text()",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="topic-category",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode/text()",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:topicCategory/mri:MD_TopicCategoryCode/text()",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="extent-controlled",
            search_paths=[
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="extent-free-text",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
            ],
            multiplicity="*",
        ),
        ISOBoundingBox(
            name="bbox",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:extent/gex:EX_Extent/gex:geographicElement/gex:EX_GeographicBoundingBox",
            ],
            multiplicity="*",
        ),
        # ISO19115-3
        ISOElement(
            name="spatial",
            search_paths=[
                # ISO19139
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_BoundingPolygon/gmd:polygon/node()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:geographicElement/gmd:EX_BoundingPolygon/gmd:polygon/node()",
                # ISO19115-3
                "mdb:identificationInfo/mri:MD_DataIdentification/mri:extent/gex:EX_Extent/gex:geographicElement/gex:EX_BoundingPolygon/gex:polygon/node()",
            ],
            multiplicity="*",
        ),
        # TODO check why commented out
        # ISOElement(
        #     name="temporal-extent-begin",
        #     search_paths=[
        #         "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition/text()",
        #         "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:beginPosition/text()",
        #         "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition/text()",
        #         "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:beginPosition/text()",
        #     ],
        #     multiplicity="*",
        # ),
        # ISOElement(
        #     name="temporal-extent-end",
        #     search_paths=[
        #         "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition/text()",
        #         "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:endPosition/text()",
        #         "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition/text()",
        #         "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:endPosition/text()",
        #     ],
        #     multiplicity="*",
        # ),
        # ISO19115-3
        ISOTemporalExtent(
            name="temporal-extent",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod",
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod",
                # ISO19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:extent/gex:EX_Extent/gex:temporalElement/gex:EX_TemporalExtent/gex:extent/gml:TimePeriod"
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="vertical-extent",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent",
                # ISO19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:extent/gex:EX_Extent/gex:verticalElement/gex:EX_VerticalExtent",
            ],
            multiplicity="*",
        ),
        # ISO19115-3
        ISOElement(
            name="vertical-extent-crs",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRSId/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:extent/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRSId/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString/text()",
                # ISO19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:extent/gex:EX_Extent/gex:verticalElement/gex:EX_VerticalExtent/gex:verticalCRSId/mrs:MD_ReferenceSystem/mrs:referenceSystemIdentifier/mcc:MD_Identifier/mcc:code/gco:CharacterString/text()",
            ],
            multiplicity="*",
        ),

        ISOCoupledResources(
            name="coupled-resource",
            search_paths=[
                "gmd:identificationInfo/srv:SV_ServiceIdentification/srv:operatesOn",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="additional-information-source",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:supplementalInformation/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISODataFormat(
            name="data-format",
            search_paths=[
                "gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format",
                # 19115-3
                "mdb:distributionInfo/mrd:MD_Distribution/mrd:distributionFormat/mrd:MD_Format/mrd:formatSpecificationCitation/cit:CI_Citation/cit:title",
            ],
            multiplicity="*",
        ),
        ISOResponsibleParty(
            name="distributor",
            search_paths=[
                "gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty",
                # 19115-3
                "mdb:distributionInfo/mrd:MD_Distribution/mrd:distributor/mrd:MD_Distributor/mrd:distributorContact/cit:CI_Responsibility",
            ],
            multiplicity="*",
        ),
        ISOResourceLocator(
            name="resource-locator",
            search_paths=[
                "gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource",
                "gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorTransferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource",
                # 19115-3
                "mdb:distributionInfo/mrd:MD_Distribution/mrd:transferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource",
                "mdb:distributionInfo/mrd:MD_Distribution/mrd:distributor/mrd:MD_Distributor/mrd:distributorTransferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource",
            ],
            multiplicity="*",
        ),
        ISOResourceLocator(
            name="resource-locator-identification",
            search_paths=[
                "gmd:identificationInfo//gmd:CI_OnlineResource",
            ],
            multiplicity="*",
        ),
        ISOElement(
            name="conformity-specification",
            search_paths=[
                "gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="conformity-pass",
            search_paths=[
                "gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:pass/gco:Boolean/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="conformity-explanation",
            search_paths=[
                "gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:explanation/gco:CharacterString/text()",
            ],
            multiplicity="0..1",
        ),
        ISOElement(
            name="lineage",
            search_paths=[
                "gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString/text()",
                "mdb:resourceLineage/mrl:LI_Lineage/mrl:statement/gco:CharacterString/text()"
            ],
            multiplicity="0..1",
        ),
        ISOBrowseGraphic(
            name="browse-graphic",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:graphicOverview/gmd:MD_BrowseGraphic",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:graphicOverview/gmd:MD_BrowseGraphic",
            ],
            multiplicity="*",
        ),
        # 19115-3
        ISOResponsibleParty(
            name="author",
            search_paths=[
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty",
                "gmd:identificationInfo/srv:SV_ServiceIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty",
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='author']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='originator']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/@codeListValue ='owner']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='author']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='originator']",
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation/cit:citedResponsibleParty/cit:CI_Responsibility[cit:role/cit:CI_RoleCode/text() ='owner']",
            ],
            multiplicity="1..*",
        ),
        ISOCitation(
            name="citation",
            search_paths=[
                # 19115-3
                "mdb:identificationInfo/*[contains(local-name(), 'Identification')]/mri:citation/cit:CI_Citation"
            ],
            multiplicity="1..*",
        ),
    ]

    def infer_values(self, values):
        # Todo: Infer name.
        self.infer_date_released(values)
        self.infer_date_updated(values)
        self.infer_date_created(values)
        self.infer_url(values)
        # Todo: Infer resources.
        self.infer_tags(values)
        self.infer_publisher(values)
        self.infer_contact(values)
        self.infer_contact_email(values)

        #ISO19139-3
        self.clean_metadata_reference_date(values)
        self.clean_dataset_reference_date(values)
        self.infer_metadata_date(values)
        self.infer_spatial(values)
        self.infer_metadata_language(values)
        self.infer_multilingual(values)
        self.infer_guid(values)
        self.infer_temporal_vertical_extent(values)

        # self.infer_citation(values)
        # self.drop_empty_objects(values)
        # self.infert_keywords(values)

        return values
    
    def clean_metadata_reference_date(self, values):
        dates = []
        for date in values['metadata-reference-date']:
            date['value'] = iso_date_time_to_utc(date['value'])
            dates.append(date)
        if dates:
            dates.sort(key=lambda x: x['value'])  # sort list of objects by value attribute
            values['metadata-reference-date'] = dates

    def clean_dataset_reference_date(self, values):
        dates = []
        for date in values['dataset-reference-date']:
            try:
                date['value'] = iso_date_time_to_utc(date['value'])[:10]
            except Exception as e:
                date['value'] = date['value'][:10]
                log.warn('Problem converting dataset-reference-date to utc format. Defaulting to %s instead', date['value'])

            dates.append(date)
        if dates:
            dates.sort(key=lambda x: x['value'])  # sort list of objects by value attribute
            values['dataset-reference-date'] = dates

    def infer_metadata_date(self, values):
        dates = values.get('metadata-date', [])

        # use newest date in list
        if len(dates):
            dates.sort(reverse=True)
            values['metadata-date'] = dates[0]

    def infer_spatial(self, values):
        geom = None
        for xmlGeom in values.get('spatial', []):
            # convert bytes to str
            try:
                xmlGeom = xmlGeom.decode()
            except (UnicodeDecodeError, AttributeError):
                pass

            if isinstance(xmlGeom, list):
                for n, x in enumerate(xmlGeom):
                    try:
                        xmlGeom[n] = x.decode()
                    except (UnicodeDecodeError, AttributeError):
                        pass

            if isinstance(xmlGeom, list):
                if len(xmlGeom) == 1:
                    xmlGeom = xmlGeom[0]

            from osgeo import ogr
            try:
                geom = ogr.CreateGeometryFromGML(xmlGeom)
            except Exception:
                try:
                    geom = ogr.CreateGeometryFromWkt(xmlGeom)
                except Exception:
                    try:
                        geom = ogr.CreateGeometryFromJson(xmlGeom)
                    except Exception:
                        log.error('Spatial field is not GML, WKT, or GeoJSON. Can not convert spatial field.')
                        pass
                        return
        if geom:
            values['spatial'] = geom.ExportToJson()
            if not values.get('bbox'):
                extent = geom.GetEnvelope()
                if extent:
                    values['bbox'].append({'west': '', 'east': '', 'north': '', 'south': ''})
                    values['bbox'][0]['west'], values['bbox'][0]['east'], values['bbox'][0]['north'], values['bbox'][0]['south'] = extent

    def infer_metadata_language(self, values):
            # ckan uses en / fr for language codes as apposed to eng / fra which is common in th iso standard
            if values.get('metadata-language'):
                values['metadata-language'] = values['metadata-language'][:2].lower()

    def infer_multilingual(self, values):
        for key in values:
            value = values[key]

            # second case used to gracfully fail if no secondary language is defined
            if (
                isinstance(value, dict) and
                (
                    ('default' in value and 'local' in value and len(value) == 2) or
                    ('default' in value and len(value) == 1)
                )
            ):
                defaultLangKey = cleanLangKey(values.get('metadata-language', 'en'))
                LangDict = local_to_dict(values[key], defaultLangKey)
                values[key] = json.dumps(LangDict)


    def infer_date_released(self, values):
        value = ''
        for date in values['dataset-reference-date']:
            if date['type'] == 'publication':
                value = date['value']
                break
        values['date-released'] = value

    def infer_date_updated(self, values):
        value = ''
        dates = []
        # Use last of several multiple revision dates.
        for date in values['dataset-reference-date']:
            if date['type'] == 'revision':
                dates.append(date['value'])

        if len(dates):
            if len(dates) > 1:
                dates.sort(reverse=True)
            value = dates[0]

        values['date-updated'] = value

    def infer_date_created(self, values):
        value = ''
        for date in values['dataset-reference-date']:
            if date['type'] == 'creation':
                value = date['value']
                break
        values['date-created'] = value

    def infer_url(self, values):
        value = ''
        for locator in values['resource-locator']:
            if locator['function'] == 'information':
                value = locator['url']
                break
        values['url'] = value

    def infer_tags(self, values):
        tags = []
        for key in ['keyword-inspire-theme', 'keyword-controlled-other']:
            for item in values[key]:
                if item not in tags:
                    tags.append(item)
        values['tags'] = tags

    def infer_publisher(self, values):
        value = ''
        for responsible_party in values['responsible-organisation']:
            if responsible_party['role'] == 'publisher':
                value = responsible_party['organisation-name']
            if value:
                break
        values['publisher'] = value

    def infer_contact(self, values):
        value = ''
        for responsible_party in values['responsible-organisation']:
            value = responsible_party['organisation-name']
            if value:
                break
        values['contact'] = value

    def infer_contact_email(self, values):
        value = ''
        for responsible_party in values['responsible-organisation']:
            if isinstance(responsible_party, dict) and \
               isinstance(responsible_party.get('contact-info'), dict) and \
               'email' in responsible_party['contact-info']:
                value = responsible_party['contact-info']['email']
                if value:
                    break
        values['contact-email'] = value

    def infer_temporal_vertical_extent(self, values):
        value = {}
        te = values.get('temporal-extent', [])
        if te:
            blist = [x.get('begin') for x in te]
            elist = [x.get('end') for x in te]
            try:
                value['begin'] = iso_date_time_to_utc(min(blist))[:10]
                if max(elist):  # end is blank for datasets with ongoing collection
                    value['end'] = iso_date_time_to_utc(max(elist))[:10]
            except Exception as e:
                value['begin'] = min(blist)[:10]
                if max(elist):
                    value['end'] = max(elist)[:10]
                log.warn('Problem converting temporal-extent dates to utc format. Defaulting to %s and %s instead', value.get('begin',''), value.get('end',''))

            values['temporal-extent-begin'] = value['begin']
            values['temporal-extent-end'] = value['end']

        value = {}
        te = values.get('vertical-extent', [])
        if te:
            minlist = [x.get('min') for x in te]
            maxlist = [x.get('max') for x in te]
            value['min'] = min(minlist)
            value['max'] = max(maxlist)
            values['vertical-extent'] = value

    def infer_guid(self, values):
        identifier = values.get('guid', {})
        guid = calculate_identifier(identifier)
        if guid:
            values['guid'] = guid




def iso_date_time_to_utc(value):
    value = value.replace("Z", "+0000")
    post_remove = 99
    if re.search(r'[+-]\d{4}', value):
        post_remove = -5
        timedelta = datetime.timedelta(hours=int(value[-5:][1:3]), minutes=int(value[-5:][-2:])) * (-1 if value[-5:][0] == '+' else 1)
    else:
        timedelta = datetime.timedelta(hours=0, minutes=0)
    try:
        utc_dt = datetime.datetime.strptime(value, '%Y-%m-%d')  # date alone is valid
    except ValueError:
        try:
            utc_dt = datetime.datetime.strptime(value[:post_remove], '%Y-%m-%dT%H:%M:%S') + timedelta
        except Exception as e:
            try:
                utc_dt = datetime.datetime.strptime(value[:post_remove], '%Y-%m-%dT%H:%M:%S.%f') + timedelta
            except Exception as e:
                log.debug('Could not convert datetime value %s to UTC: %s', value, e)
                raise
    return utc_dt.strftime('%Y-%m-%d %H:%M:%S')

def calculate_identifier(identifier):
        if isinstance(identifier, str):
            return identifier
        code = identifier.get('code')
        codeSpace = identifier.get('code-space')
        authority = identifier.get('authority')
        version = identifier.get('version')
        guid = None
        if code:
            id_list = [authority, codeSpace, code, version]
            guid = '_'.join(x.strip() for x in id_list if x.strip())
        return guid

def cleanLangKey(key):
    key = re.sub("[^a-zA-Z]+", "", key)
    key = key[:2]
    return key

def local_to_dict(item, defaultLangKey):
    # XML parser seems to generate unicode strings containg utf-8 escape
    # charicters even though the file is utf-8. To fix must encode unicode
    # to latin1 then treet as regular utf-8 string. Seems this is not
    # true for all files so trying latin1 first and then utf-8 if it does
    # not encode.
    out = {}

    default = item.get('default').strip()
    # decode double escaped unicode chars
    if(default and re.search(r'\\\\u[0-9a-fA-F]{4}', default)):
        if isinstance(default, str):  # encode to get bytestring as decode only works on bytes
            default = default.encode().decode('unicode-escape')
        else:  # we have bytes
            default = default.decode('unicode-escape')

    # this will create a byte string so better to let the json.dumps library handle it
    # try:
    #     default = default.encode('utf-8')
    # except Exception:
    #     log.error('Failed to encode string "%r" as utf-8', default)
    if len(default) > 1:
        out.update({defaultLangKey: default})

    local = item.get('local')
    if isinstance(local, dict):
        langKey = cleanLangKey(local.get('language_code'))
        # langKey = langKey.encode('utf-8')

        LangValue = item.get('local').get('value')
        LangValue = LangValue.strip()
        # decode double escaped unicode chars
        if(LangValue and re.search(r'\\\\u[0-9a-fA-F]{4}', LangValue)):
            if isinstance(LangValue, str):  # encode to get bytestring as decode only works on bytes
                LangValue = LangValue.encode().decode('unicode-escape')
            else:  # we have bytes
                LangValue = LangValue.decode('unicode-escape')

        # this will create a byte string so better to let the json.dumps library handle it
        # try:
        #     LangValue = LangValue.encode('utf-8')
        # except Exception:
        #     log.error('Failed to encode string "%r" as utf-8', LangValue)
        if len(LangValue) > 1:
            out.update({langKey: LangValue})

    return out

    def drop_empty_objects(self, values):
        to_drop = []
        for key, value in values.items():
            if value == {} or value == []:
                to_drop.append(key)
        for key in to_drop:
            del values[key]