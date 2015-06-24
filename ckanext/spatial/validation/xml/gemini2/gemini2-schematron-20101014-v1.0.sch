<?xml version="1.0" encoding="utf-8"?>

<!-- ========================================================================================== -->
<!-- Schematron Schema for the UK GEMINI Standard Version 2.1                             -->
<!-- ========================================================================================== -->

<!-- 
     James Rapaport                                
     SeaZone Solutions Limited                                                  
     2010-07-13
     
     This Schematron schema has been developed for the UK Location Programme (UKLP) by SeaZone Solutions Limited. 	     (SeaZone), with funding from Defra and CLG. It is designed to validate the constraints introduced in the             GEMINI2.1 draft standard. Constraints have been taken from:
     
     UK GEMINI Standard, Version 2.1, August 2010.
     
     The schema has been developed for XSLT Version 1.0 and tested with the ISO 19757-3 Schematron
     XML Stylesheets issued on 2009-03-18 at http://www.schematron.com/tmp/iso-schematron-xslt1.zip 
     
     The schema tests constraints on ISO / TS 19139 encoded metadata. The rules expressed in this 
     schema apply in addition to validation by the ISO / TS 19139 XML schemas.
     
     The schema is designed to test ISO 19139 encoded metadata incorporating ISO 19136 (GML Version
     3.2.1) elements where necessary. Note that GML elements must be mapped to the Version 3.2.1 
     GML namespace - http://www.opengis.net/gml/3.2

     (C) Crown copyright, 2010

     You may use and re-use the information in this publication (not including logos) free of charge
     in any format or medium, under the terms of the Open Government Licence.
   

     Document History:
     
     2010-10-14 - Version 1.0
     Baselined version for beta release.  No technical changes against v0.11.
-->

<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt" schemaVersion="0.11">

  <sch:title>UK GEMINI Standard Draft Version 2.1</sch:title>

  <sch:p>This Schematron schema is designed to test the constraints introduced in the GEMINI2 discovery metadata standard.</sch:p>

  <!-- Namespaces from ISO 19139 Metadata encoding -->
  <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>

  <!-- Namespace for ISO 19119 - Metadata Describing Services -->
  <sch:ns prefix="srv" uri="http://www.isotc211.org/2005/srv"/>
  
  <!-- Namespace for ISO 19136 - Geography Mark-up Language -->
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2" />

  <!-- ========================================================================================== -->
  <!-- Concrete Patterns                                                                          -->
  <!-- ========================================================================================== -->

  <!-- ========================================================================================== -->
  <!-- Metadata Item 1 - Title                                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi1">
    <sch:title>Title</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi1-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:title"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 2 - Alternative Title                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi2">
    <sch:title>Alternative Title</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi2-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:alternateTitle"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 3 - Dataset Language                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi3">
    <sch:title>Dataset Language</sch:title>
  </sch:pattern>

  <sch:pattern is-a="LanguagePattern" id="Gemini2-mi3-Language">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:language"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 4 - Abstract                                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi4">
    <sch:title>Abstract</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi4-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:abstract"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 5 - Topic Category                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi5">
    <sch:title>Topic Category</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  count(gmd:topicCategory) >= 1) or 
                  (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../../gmd:hierarchyLevel) = 0">
        Topic category is mandatory for datasets and series. One or more shall be provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:topicCategory">
      <sch:assert test="((../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  count(@gco:nilReason) = 0) or 
                  (../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  ../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
                  count(../../../gmd:hierarchyLevel) = 0">
        Topic Category shall not be null.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 6 - Keyword                                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi6">
    <sch:title>Keyword</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:descriptiveKeywords) &gt;= 1">
        Descriptive keywords are mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi6-Keyword-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:keyword"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi6-Thesaurus-Title-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:thesaurusName/*[1]/gmd:title"/>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi6-Thesaurus-DateType-CodeList">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:thesaurusName/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 7 - Temporal Extent                                                          -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi7">
    <sch:title>Temporal extent</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  count(gmd:extent/*[1]/gmd:temporalElement) = 1) or 
                  (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../../gmd:hierarchyLevel) = 0">
        Temporal extent is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent |
              /*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/*[@gco:isoType='gmd:EX_TemporalExtent'][1]/gmd:extent |
              /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent |
              /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/*[@gco:isoType='gmd:EX_TemporalExtent'][1]/gmd:extent">
      <sch:assert test="count(gml:TimePeriod) = 1">
        Temporal extent shall be implemented using gml:TimePeriod.
      </sch:assert>
      <sch:assert test="count(gml:TimePeriod/gml:beginPosition) + count(gml:TimePeriod/gml:endPosition) = 2">
        Temporal extent shall be implemented using gml:beginPosition and gml:endPosition.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 8 - Dataset Reference Date                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi8">
    <sch:title>Dataset reference date</sch:title>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi8-ReferenceDate-DateType-CodeList">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 10 - Lineage                                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi10">
    <sch:title>Lineage</sch:title>
    <sch:rule context="/*[1]">
      <sch:assert test="((gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
                  count(gmd:dataQualityInfo[1]/*[1]/gmd:lineage/*[1]/gmd:statement) = 1) or
                  (gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(gmd:hierarchyLevel) = 0">
        Lineage is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi10-Statement-Nillable">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo[1]/*[1]/gmd:lineage/*[1]/gmd:statement"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 11, 12, 13, 14 - Geographic Bounding Box                                     -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi11">
    <sch:title>West and east longitude, north and south latitude</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  (count(gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox) = 1) or
                  count(gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'][1]) = 1) or
                  (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and 
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../../gmd:hierarchyLevel) = 0">
        Geographic bounding box is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GeographicBoundingBoxPattern" id="Gemini2-mi11-BoundingBox">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
               /*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'] [1]|
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'][1]"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-West-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:westBoundLongitude |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:westBoundLongitude"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-East-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:eastBoundLongitude |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:eastBoundLongitude"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-South-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:southBoundLatitude |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:southBoundLatitude"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mill-North-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:northBoundLatitude |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:northBoundLatitude"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 15 - Extent                                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi15">
    <sch:title>Extent</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi15-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/*[1]/gmd:code | 
               /*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicDescription'][1]/gmd:geographicIdentifier/*[1]/gmd:code |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/*[1]/gmd:code |
               /*[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicDescription'][1]/gmd:geographicIdentifier/*[1]/gmd:code"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 16 - Vertical Extent Information                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi16">
    <sch:title>Vertical extent information</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]">
      <sch:assert test="count(gmd:verticalElement) &lt;= 1">
        Vertical extent information is optional. Zero or one may be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi16-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:verticalElement/*[1]/gmd:minimumValue |
               /*[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:verticalElement/*[1]/gmd:maximumValue"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 17 - Spatial Reference System                                                -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi17">
    <sch:title>Spatial reference system</sch:title>
    <sch:rule context="/*[1]">
      <sch:assert test="((gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
                  count(gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/*[1]/gmd:code) = 1) or
                  (gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(gmd:hierarchyLevel) = 0">
        Spatial reference system is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi17-Nillable">
    <sch:param name="context" value="/*[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/*[1]/gmd:code"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 18 - Spatial Resolution                                                      -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi18">
    <sch:title>Spatial Resolution</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution/*[1]/gmd:distance/*[1]">
      <sch:assert test="@uom = 'urn:ogc:def:uom:EPSG::9001'">
        Distance measurement shall be metres. The unit of measure attribute value shall be 'urn:ogc:def:uom:EPSG::9001'.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi18-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution/*[1]/gmd:distance"/>
  </sch:pattern>
  
  <!-- ========================================================================================== -->
  <!-- Metadata Item 19 - Resource Locator                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi19">
    <sch:title>Resource locator</sch:title>
    <sch:rule context="/*[1]/gmd:distributionInfo/*[1]/gmd:transferOptions/*[1]/gmd:onLine/*[1]">
      <sch:assert test="count(gmd:linkage) = 0 or 
                  (starts-with(normalize-space(gmd:linkage/*[1]), 'http://')  or 
                  starts-with(normalize-space(gmd:linkage/*[1]), 'https://') or 
                  starts-with(normalize-space(gmd:linkage/*[1]), 'ftp://'))">
        The value of resource locator does not appear to be a valid URL. It has a value of '<sch:value-of select="gmd:linkage/*[1]"/>'. The URL must start with either http://, https:// or ftp://.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi19-Nillable">
    <sch:param name="context" value="/*[1]/gmd:distributionInfo/*[1]/gmd:transferOptions/*[1]/gmd:onLine/*[1]/gmd:linkage"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 21 - Data Format                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi21">
    <sch:title>Data Format</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi21-Name-Nillable">
    <sch:param name="context" value="/*[1]/gmd:distributionInfo/*[1]/gmd:distributionFormat/*[1]/gmd:name"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi21-Version-Nillable">
    <sch:param name="context" value="/*[1]/gmd:distributionInfo/*[1]/gmd:distributionFormat/*[1]/gmd:version"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 23 - Responsible Organisation                                                -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-23">
    <sch:title>Responsible organisation</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:pointOfContact) &gt;= 1">
        Responsible organisation is mandatory. At least one shall be provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact">
      <sch:assert test="count(@gco:nilReason) = 0">
        The value of responsible organisation shall not be null.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="Gemini2-mi23-ResponsibleParty">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi23-OrganisationName-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:organisationName |
               /*[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress"/>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi23-Role-CodeList">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:role/*[1]"/>
  </sch:pattern>
  
  <!-- ========================================================================================== -->
  <!-- Metadata Item 24 - Frequency of Update                                                     -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi24">
    <sch:title>Frequency of update</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  count(gmd:resourceMaintenance/*[1]/gmd:maintenanceAndUpdateFrequency) = 1) or 
                  (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../../gmd:hierarchyLevel) = 0">
        Frequency of update is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi24-CodeList">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceMaintenance/*[1]/gmd:maintenanceAndUpdateFrequency/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 25 - Limitations on Public Access                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi25">
    <sch:title>Limitations on public access</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/gmd:MD_LegalConstraints | /*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1][gco:isoType='gmd:MD_LegalConstraints']">
      <sch:assert test="count(gmd:accessConstraints[*/@codeListValue='otherRestrictions']) = 1">
        Limitations on public access code list value shall be 'otherRestrictions'.
      </sch:assert>
      <sch:assert test="count(gmd:otherConstraints) &gt;= 1">
        Limitations on public access shall be expressed using gmd:otherConstraints.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi25-OtherConstraints-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:otherConstraints"/>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi25-AccessConstraints-CodeList">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:accessConstraints/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 26 - Use Constraints                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi26">
    <sch:title>Use constraints</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:resourceConstraints/*[1]/gmd:useLimitation) &gt;= 1">
        Use constraints shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi26-UseLimitation-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:useLimitation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 27 - Additional Information Source                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi27">
    <sch:title>Additional information source</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi27-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:supplementalInformation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 36 - Unique Resource Identifier                                              -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi36">
    <sch:title>Unique resource identifier</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]">
      <sch:assert test="((../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  ../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and 
                  count(gmd:identifier) = 1) or 
                  (../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and 
                  ../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../../../../gmd:hierarchyLevel) = 0">
        Unique resource identifier is mandatory for datasets and series. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Ensure that Unique Resource Identifier has a value -->
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi36-Code-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:identifier/*[1]/gmd:code"/>
  </sch:pattern>

  <!-- Ensure that a code space value is provided if the element is encoded -->
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi36-CodeSpace-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:identifier/*[1]/gmd:codeSpace"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 39 - Resource Type                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi39">
    <sch:title>Resource type</sch:title>
    <sch:rule context="/*[1]">
      <sch:assert test="count(gmd:hierarchyLevel) = 1">
        Resource type is mandatory. One shall be provided.
      </sch:assert>
      <sch:assert test="gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or 
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series' or 
                  gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'service'">
        Value of resource type shall be 'dataset', 'series' or 'service'.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi39-CodeList">
    <sch:param name="context" value="/*[1]/gmd:hierarchyLevel/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 41 - Conformity                                                              -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi41">
    <sch:title>Conformity</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi41-Pass-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:pass"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi41-Explanation-Nillable">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:explanation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 42 - Specification                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi42">
    <sch:title>Specification</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi42-Title-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:title"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi42-Date-Nillable">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:date/*[1]/gmd:date"/>
  </sch:pattern>

  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi42-DateType-CodeList">
    <sch:param name="context" value="/*[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:date/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 43 - Equivalent scale                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi43">
    <sch:title>Equivalent scale</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution">
      <sch:assert test="count(gmd:spatialResolution/*[1]/gmd:equivalentScale) &lt;= 1">
        Equivalent scale is optional. Zero or one may be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi43-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution/*[1]/gmd:equivalentScale/*[1]/gmd:denominator"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 33 - Metadata Language                                                       -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi33">
    <sch:title>Metadata language</sch:title>
  </sch:pattern>

  <sch:pattern is-a="LanguagePattern" id="Gemini2-mi33-Language">
    <sch:param name="context" value="/*[1]/gmd:language"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 30 - Metadata Date                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi30">
    <sch:title>Metadata date</sch:title>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi30-Nillable">
    <sch:param name="context" value="/*[1]/gmd:dateStamp"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 35 - Metadata Point of Contact                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi35">
    <sch:title>Metadata point of contact</sch:title>
    <sch:rule context="/*[1]/gmd:contact">
      <sch:assert test="count(@gco:nilReason) = 0">
        The value of metadata point of contact shall not be null.
      </sch:assert>
      <sch:assert test="*/gmd:role/*[1]/@codeListValue = 'pointOfContact'">
        The metadata point of contact role shall be 'pointOfContact'.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="Gemini2-mi35-ResponsibleParty">
    <sch:param name="context" value="/*[1]/gmd:contact"/>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi35-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:contact/*[1]/gmd:organisationName | /*[1]/gmd:contact/*[1]/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 37 - Spatial Data Service Type                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi37">
    <sch:title>Spatial data service type</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/srv:SV_ServiceIdentification | /*[1]/gmd:identificationInfo[1]/*[@gco:isoType='srv:SV_ServiceIdentification'][1]">
      <sch:assert test="(../../gmd:hierarchyLevel/*[1]/@codeListValue = 'service' and 
                  count(srv:serviceType) = 1) or 
                  ../../gmd:hierarchyLevel/*[1]/@codeListValue != 'service'">
        If the resource type is service, one spatial data service type shall be provided.
      </sch:assert>
      <sch:assert test="srv:serviceType/*[1] = 'discovery' or
                  srv:serviceType/*[1] = 'view' or
                  srv:serviceType/*[1] = 'download' or
                  srv:serviceType/*[1] = 'transformation' or
                  srv:serviceType/*[1] = 'invoke' or
                  srv:serviceType/*[1] = 'other'">
        Service type shall be one of 'discovery', 'view', 'download', 'transformation', 'invoke' or 'other' following INSPIRE generic names.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi37-Nillable">
    <sch:param name="context" value="/*[1]/gmd:identificationInfo[1]/*[1]/srv:serviceType"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Metadata Item 38 - Coupled Resource                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi38">
    <sch:title>Coupled resource</sch:title>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/srv:SV_ServiceIdentification | /*[1]/gmd:identificationInfo[1]/*[@gco:isoType='srv:SV_ServiceIdentification'][1]">
      <sch:assert test="count(srv:operatesOn) &gt;= 1">
        Coupled resource shall be provided if the metadata is for a service.
      </sch:assert>
    </sch:rule>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/srv:operatesOn">
      <sch:assert test="count(@xlink:href) = 1">
        Coupled resource shall be implemented by reference using the xlink:href attribute.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Ancillary Tests                                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-at1">
    <sch:title>Data identification citation</sch:title>
    <sch:p>The identification information citation cannot be null.</sch:p>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]/gmd:citation">
      <sch:assert test="count(@gco:nilReason) = 0">
        Identification information citation shall not be null.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern fpi="Gemini2-at2">
    <sch:title>Metadata resource type test</sch:title>
    <sch:p>Test to ensure that metadata about datasets include the gmd:MD_DataIdentification element and metadata about services include the srv:SV_ServiceIdentification element</sch:p>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]">
      <sch:assert test="((../gmd:hierarchyLevel[1]/*[1]/@codeListValue='dataset' or 
                  ../gmd:hierarchyLevel[1]/*[1]/@codeListValue='series') and 
                  (local-name(*) = 'MD_DataIdentification' or */@gco:isoType='gmd:MD_DataIdentification')) or
                  (../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
                  ../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or 
                  count(../gmd:hierarchyLevel) = 0">
        The first identification information element shall be of type gmd:MD_DataIdentification.
      </sch:assert>
      <sch:assert test="((../gmd:hierarchyLevel[1]/*[1]/@codeListValue='service') and 
                  (local-name(*) = 'SV_ServiceIdentification' or */@gco:isoType='srv:SV_ServiceIdentification')) or
                  (../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'service') or 
                  count(../gmd:hierarchyLevel) = 0">
        The first identification information element shall be of type srv:SV_ServiceIdentification.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern fpi="Gemini2-at3">
    <sch:title>Metadata file identifier</sch:title>
    <sch:p>A file identifier is required</sch:p>
    <sch:rule context="/*[1]">
      <sch:assert test="count(gmd:fileIdentifier) = 1">
        A metadata file identifier shall be provided. Its value shall be a system generated GUID.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-at3-NotNillable">
    <sch:param name="context" value="/*[1]/gmd:fileIdentifier"/>
  </sch:pattern>

  <sch:pattern fpi="Gemini2-at4">
    <sch:title>Constraints</sch:title>
    <sch:p>Constraints (Limitations on public access and use constraints) are required.</sch:p>
    <sch:rule context="/*[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:resourceConstraints) &gt;= 1">
        Limitations on public access and use constrains are required.
      </sch:assert>
    </sch:rule>    
  </sch:pattern>

  <sch:pattern fpi="Gemini2-at5">
    <sch:title>Creation date type</sch:title>
    <sch:p>Constrain citation date type = creation to one occurrence.</sch:p>
    <sch:rule context="//gmd:CI_Citation | //*[@gco:isoType='gmd:CI_Citation'][1]">
      <sch:assert test="count(gmd:date/*[1]/gmd:dateType/*[1][@codeListValue='creation']) &lt;= 1">
        The shall not be more than one creation date.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Abstract Patterns                                                                          -->
  <!-- ========================================================================================== -->

  <!-- Test that an element has a value or has a valid nilReason value -->
  <sch:pattern abstract="true" id="TypeNillablePattern">
    <sch:rule context="$context">
      <sch:assert test="(string-length(.) &gt; 0) or 
                  (@gco:nilReason = 'inapplicable' or
                  @gco:nilReason = 'missing' or 
                  @gco:nilReason = 'template' or
                  @gco:nilReason = 'unknown' or
                  @gco:nilReason = 'withheld' or
                  starts-with(@gco:nilReason, 'other:'))">
        The <sch:name/> element shall have a value or a valid Nil Reason.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test that an element has a value - the value is not nillable -->
  <sch:pattern abstract="true" id="TypeNotNillablePattern">
    <sch:rule context="$context">
      <sch:assert test="string-length(.) &gt; 0 and count(./@gco:nilReason) = 0">
        The <sch:name/> element is not nillable and shall have a value.
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  
  <!-- Test ISO code lists -->
  <sch:pattern abstract="true" id="IsoCodeListPattern">
    <sch:rule context="$context">
      <sch:assert test="string-length(@codeListValue) &gt; 0">
        The codeListValue attribute does not have a value.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test the language values (Metadata and Resource) -->
  <sch:pattern abstract="true" id="LanguagePattern">
    <sch:rule context="$context">
      <sch:assert test="count(gmd:LanguageCode) = 1">
        Language shall be implemented with gmd:LanguageCode.
      </sch:assert>
    </sch:rule>
    <sch:rule context="$context/gmd:LanguageCode">
      <sch:assert test="string-length(@codeListValue) &gt; 0">
        The language code list value is absent.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test for the responsible party information -->
  <sch:pattern abstract="true" id="ResponsiblePartyPattern">
    <!-- Count of Organisation Name and Individual Name >= 1 -->
    <sch:rule context="$context">
      <sch:assert test="count(*/gmd:organisationName) = 1">
        One organisation name shall be provided.
      </sch:assert>
      <sch:assert test="count(*/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress) = 1">
        One email address shall be provided
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test for gmd:MD_GeographicBoundingBox values -->
  <sch:pattern abstract="true" id="GeographicBoundingBoxPattern">
    <sch:rule context="$context">
      <!-- West Bound Longitude -->
      <sch:assert test="string-length(gmd:westBoundLongitude) = 0 or (gmd:westBoundLongitude &gt;= -180.0 and gmd:westBoundLongitude &lt;= 180.0)">
        West bound longitude has a value of <sch:value-of select="gmd:westBoundLongitude"/> which is outside bounds.
      </sch:assert>
      <!-- East Bound Longitude -->
      <sch:assert test="string-length(gmd:eastBoundLongitude) = 0 or (gmd:eastBoundLongitude &gt;= -180.0 and gmd:eastBoundLongitude &lt;= 180.0)">
        East bound longitude has a value of <sch:value-of select="gmd:eastBoundLongitude"/> which is outside bounds.
      </sch:assert>
      <!-- South Bound Latitude -->
      <sch:assert test="string-length(gmd:southBoundLatitude) = 0 or (gmd:southBoundLatitude &gt;= -90.0 and gmd:southBoundLatitude &lt;= gmd:northBoundLatitude)">
        South bound latitude has a value of <sch:value-of select="gmd:southBoundLatitude"/> which is outside bounds.
      </sch:assert>
      <!-- North Bound Latitude -->
      <sch:assert test="string-length(gmd:northBoundLatitude) = 0 or (gmd:northBoundLatitude &lt;= 90.0 and gmd:northBoundLatitude &gt;= gmd:southBoundLatitude)">
        North bound latitude has a value of <sch:value-of select="gmd:northBoundLatitude"/> which is outside bounds.
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  
</sch:schema>