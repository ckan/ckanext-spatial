<?xml version="1.0" encoding="utf-8"?>
<!-- ========================================================================================== -->
<!-- Schematron Schema for the UK GEMINI Standard Version 2.3                             -->
<!-- ========================================================================================== -->
<!-- 
     James Passmore                                
     British Geological Survey                                                
     2017-09-08
     
     This Schematron schema has been developed for the UK Location Programme (UKLP) by
     British Geological Survey (BGS), with funding from AGI.

     It is designed to validate the constraints introduced in the GEMINI2.3 draft standard.
     Constraints have been taken from:
     
     UK GEMINI Standard, Version 2.3, September 2017.
     
     The schema has been developed for XSLT Version 1.0, and is based on the GEMINI 2.1 schematron, 
     which was tested with the ISO 19757-3 Schematron XML Stylesheets issued on 2009-03-18 at:
     http://www.schematron.com/tmp/iso-schematron-xslt1.zip (no longer available).
     
     The schema tests constraints on ISO / TS 19139 encoded metadata. The rules expressed in this 
     schema apply in addition to validation by the ISO / TS 19139 XML schemas.
     
     The schema is designed to test ISO 19139 encoded metadata incorporating ISO 19136 (GML Version
     3.2.1) elements where necessary. Note that GML elements must be mapped to the Version 3.2.1 
     GML namespace - http://www.opengis.net/gml/3.2

     You may use and re-use the information in this publication (not including logos) free of charge
     in any format or medium, under the terms of the Open Government Licence.

     Document History:
     
     2017-09-08 - Modified from GEMINI 2.1 Schematron Schema.sch
                ~ All contexts changed to allow checking of metadata either as CSW response or standalone metadata record
                ~ Namespace prefixes for all relevant XML schema added.
     2017-11-14 - Release Candidate 1
                ~ Added/amened rules for clarifications and changes for GEMINI 2.3
     2017-12-11 - Release Candidate 2 
                ~ removed Copyright statement, appropriate copyright still needs to be added
                ~ removed Gemini2-mi47-services-restriction as it doesn't apply.
                ~ added brackets around Unique for Resource Identifier text.
     2018-03-13 ~ Release Candidate 3
                ~ Added unique prefixes to all asserts/reports to allow esier debugging/reporting
                ~ Re-added Gemini2-mi47-services-restriction as it does apply (cf. TG Requirement 3.1:)
                ~ Added length test to Abstract
                ~ correction to count test in Quality Scope
                ~ added ancillary test (at-8) for ensuring reported scopes don't clash
                ~ corrected issue in Data Format
                ~ added abstract pattern TypeNillableVersionPattern
     2018-03-14 ~ Release Candidate 4
                ~ Removed ancillary test (at-8)
     2018-04-11 ~ Release Candidate 5
                ~ replaced references to XML files on BGS development server for files on AGI server
     2018-04-26 ~ Release Candidate 6
                ~ Spelling corrections/formatting
                ~ added pattern to Spatial representation type
                ~ corrected context in Conformity
                ~ added rule to hierarchyLevelName
                ~ corrected context in Topological consistency
                ~ added to list of nil version terms in Data Format
                ~ corrected context in Data Format
                ~ removed Ancillary test metadata/2.0/req/common/root-element as not testing the requirement
    2018-05-17  ~ Release Candidate 7
                ~ Added hints to possible locations for Abstract patterns
                ~ Added Metadata Item (titles) to MI debug reports
                ~ Removed requirement for gmd:useLimitation in MI-26 (Use Constraints) as superseded by new requirements
                ~ Added AT-8 to test we have at least two legal requirements sections.
                ~ Added new rule and removed old rules in Limitations on Public Access
                ~ Added IsoCodeListPattern to MI-26 (Use Constraints)
    2018-05-21  ~ Release Candidate 8
                ~ moved first sch:p to beneath last sch:ns, for compliance to RELAX NG schema for Schematron
                ~ moved sch:lets for debug reporting to top, for compliance to RELAX NG schema for Schematron
    2018-07-03  ~ Release Candidate 9
                ~ updated reference XML files to location on https://agi.org.uk/ 
-->
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt" schemaVersion="1.2">
  <sch:title>UK GEMINI Standard Draft Version 2.3</sch:title>
  <!-- Namespaces from ISO 19139 Metadata encoding -->
  <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>
  <!-- Namespace for ISO 19119 - Metadata Describing Services -->
  <sch:ns prefix="srv" uri="http://www.isotc211.org/2005/srv"/>
  <!-- Namespace for ISO 19136 - Geography Mark-up Language -->
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <sch:ns prefix="gml32" uri="http://www.opengis.net/gml/3.2"/>
  <!-- Namespace for CSW responses -->
  <sch:ns prefix="csw" uri="http://www.opengis.net/cat/csw/2.0.2"/>
  <!-- Namespace other -->
  <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <sch:ns prefix="xs" uri="http://www.w3.org/2001/XMLSchema"/>
  <sch:ns uri="http://www.isotc211.org/2005/gss" prefix="gss"/>
  <sch:ns uri="http://www.isotc211.org/2005/gts" prefix="gts"/>
  <sch:ns uri="http://www.isotc211.org/2005/gsr" prefix="gsr"/>
  <sch:p>This Schematron schema is designed to test the constraints introduced in the GEMINI2 discovery metadata standard.</sch:p>
  <!-- Define some generic parameters -->
  <sch:let name="hierarchyLevelCLValue"
    value="//gmd:MD_Metadata/gmd:hierarchyLevel[1]/gmd:MD_ScopeCode[1]/@codeListValue"/>
  <!-- IR titles -->
  <sch:let name="inspire1089"
    value="'Commission Regulation (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services'"/>
  <sch:let name="inspire1089x"
    value="'COMMISSION REGULATION (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services'"/>
  <sch:let name="inspire976"
    value="'Commission Regulation (EC) No 976/2009 of 19 October 2009 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards the Network Services'"/>
  <!-- External documents -->
  <sch:let name="defaultCRScodes"
    value="document('https://agi.org.uk/images/xslt/d4.xml')"/>
  <sch:let name="charSetCodes"
    value="document('https://agi.org.uk/images/xslt/MD_CharacterSetCode.xml')"/>
  <!-- Text for validation reporting -->
  <sch:let name="LPreportsupplement"
    value="'This test may be called by the following Metadata Items: 3 - Dataset Language and 33 - Metadata Language'"/>
  <sch:let name="RPreportsupplement"
    value="'This test may be called by the following Metadata Items: 23 - Responsible Organisation and 35 - Metadata Point of Contact'"/>
  <sch:let name="GBreportsupplement" value="'Issue in Metadata item 44: Bounding box'"/>
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
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:title"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 2 - Alternative Title                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi2">
    <sch:title>Alternative Title</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi2-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:alternateTitle"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 3 - Dataset Language                                                         -->
  <!-- No change for natural dataset language (code zxx)                                          -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi3">
    <sch:title>Dataset Language</sch:title>
  </sch:pattern>
  <sch:pattern is-a="LanguagePattern" id="Gemini2-mi3-Language">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:language"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 4 - Abstract                                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi4">
    <sch:title>Abstract</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi4-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:abstract"/>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/common/resource-abstract">
    <sch:title>Abstract free-text element check</sch:title>
    <sch:p>A human readable, non-empty description of the dataset, dataset series or service shall
      be provided</sch:p>
    <sch:rule context="//gmd:abstract">
      <sch:assert test="normalize-space(.) and *"> MI-4a (Abstract): A human readable, non-empty description of
        the dataset, dataset series, or service shall be provided </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/common/resource-abstract-len">
    <sch:title>Abstract length check</sch:title>
    <sch:rule context="//gmd:abstract/*[1]">
      <sch:assert test="string-length() &gt; 99"> MI-4b (Abstract): Abstract is too short. GEMINI 2.3 requires
        an abstract of at least 100 characters, but abstract "<sch:value-of
          select="normalize-space(.)"/>" has only <sch:value-of select="string-length(.)"/>
        characters </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/common/resource-abstract-text">
    <sch:title>Abstract is not the same as Title...</sch:title>
    <sch:rule context="//gmd:abstract/*[1]">
      <sch:let name="resourceTitle"
        value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:title/*[1][normalize-space()]"/>
      <sch:let name="resourceAbstract" value="normalize-space(.)"/>
      <sch:assert test="$resourceAbstract != $resourceTitle"> MI-4c (Abstract): Abstract "<sch:value-of
          select="$resourceAbstract"/>" must not be the same text as the title "<sch:value-of
          select="$resourceTitle"/>")). </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 5 - Topic Category                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi5">
    <sch:title>Topic Category</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert
        test="
          ((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          count(gmd:topicCategory) >= 1) or
          (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(../../gmd:hierarchyLevel) = 0"
        >MI-5a (Topic Category): Topic category is mandatory for datasets and series. One or more shall be provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:topicCategory">
      <sch:assert
        test="
          ((../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          ../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          count(@gco:nilReason) = 0) or
          (../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          ../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(../../../gmd:hierarchyLevel) = 0"
        >MI-5b (Topic Category): Topic Category shall not be null. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 6 - Keyword                                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi6">
    <sch:title>Keyword</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:descriptiveKeywords) &gt;= 1"> MI-6 (Keyword): Descriptive keywords are
        mandatory. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi6-Keyword-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:keyword"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi6-Thesaurus-Title-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:thesaurusName/*[1]/gmd:title"
    />
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi6-Thesaurus-DateType-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:descriptiveKeywords/*[1]/gmd:thesaurusName/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 7 - Temporal Extent                                                          -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi7">
    <sch:title>Temporal extent</sch:title>
    <sch:rule
      context="
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent">
      <sch:assert test="count(gml:TimePeriod) = 1 or count(gml:TimeInstant) = 1"> MI-7a (Temporal Extent): Temporal
        extent shall be implemented using gml:TimePeriod or gml:TimeInstant. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi7-endpos">
    <sch:rule
      context="
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent/gml:TimePeriod/gml:endPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent/gml:TimePeriod/gml:endPosition">
      <sch:report
        test="((@indeterminatePosition = 'unknown' or @indeterminatePosition = 'now') and normalize-space(.))"
        > MI-7b (Temporal Extent): When indeterminatePosition='unknown' or indeterminatePosition='now' are specified
        endPosition should be empty </sch:report>
      <sch:assert
        test="string-length() = 0 or string-length() = 4 or string-length() = 7 or string-length() = 10 or string-length() = 19"
        > MI-7c (Temporal Extent): Date string doesn't have correct length, check it conforms to Gregorian calendar
        and UTC as per ISO 8601 </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi7-begpos">
    <sch:rule
      context="
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent/gml:TimePeriod/gml:beginPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition |
        //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:temporalElement/*[@gco:isoType = 'gmd:EX_TemporalExtent'][1]/gmd:extent/gml:TimePeriod/gml:beginPosition">
      <sch:report test="(@indeterminatePosition = 'unknown' and normalize-space(.))"> MI-7d (Temporal Extent): When
        indeterminatePosition='unknown' is specified beginPosition should be empty </sch:report>
      <sch:assert
        test="string-length() = 0 or string-length() = 4 or string-length() = 7 or string-length() = 10 or string-length() = 19"
        > MI-7e (Temporal Extent): Date string doesn't have correct length, check it conforms to Gregorian calendar
        and UTC as per ISO 8601 </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 8 - Dataset Reference Date                                                   -->
  <!-- Also see ancilliary tests (Gemini2-at5)                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi8">
    <sch:title>Dataset reference date</sch:title>
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi8-ReferenceDate-DateType-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 10 - Lineage                                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi10">
    <sch:title>Lineage</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert
        test="
          ((gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          count(gmd:dataQualityInfo[1]/*[1]/gmd:lineage/*[1]/gmd:statement) = 1) or
          (gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(gmd:hierarchyLevel) = 0"
        > MI-10a (Lineage): Lineage is mandatory for datasets and series. One shall be provided. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi10-Statement-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:dataQualityInfo[1]/*[1]/gmd:lineage/*[1]/gmd:statement"/>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi10-scoped">
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo[1]/gmd:DQ_DataQuality[1]/gmd:scope[1]/gmd:DQ_Scope[1]/gmd:level[1]/gmd:MD_ScopeCode[1][@codeListValue = 'dataset']">
      <sch:assert
        test="count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:lineage) = 1"
        > MI-10b (Lineage): The gmd:dataQualityInfo scoped to dataset must have a lineage section
      </sch:assert>
    </sch:rule>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo[1]/gmd:DQ_DataQuality[1]/gmd:scope[1]/gmd:DQ_Scope[1]/gmd:level[1]/gmd:MD_ScopeCode[1][@codeListValue = 'series']">
      <sch:assert
        test="count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:lineage) = 1"
        > MI-10c (Lineage): The gmd:dataQualityInfo scoped to series must have a lineage section </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 11, 12, 13, 14 - Geographic Bounding Box                                     -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi11">
    <sch:title>West and East longitude, North and South latitude</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert
        test="
          ((../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          (count(gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox) &gt;= 1) or
          count(gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType = 'gmd:EX_GeographicBoundingBox'][1]) &gt;= 1) or
          (../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          ../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(../../gmd:hierarchyLevel) = 0"
        > MI-(11,12,13,13  Geographic Bounding Box): Geographic bounding box is mandatory for datasets and series. One or
        more shall be provided. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="GeographicBoundingBoxPattern" id="Gemini2-mi11-BoundingBox">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'] [1]|
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'][1]"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-West-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:westBoundLongitude |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:westBoundLongitude"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-East-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:eastBoundLongitude |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:eastBoundLongitude"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi11-South-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:southBoundLatitude |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:southBoundLatitude"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mill-North-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[1]/gmd:northBoundLatitude |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[1]/gmd:northBoundLatitude"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 15 - Extent                                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi15">
    <sch:title>Extent</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi15-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/*[1]/gmd:code | 
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicDescription'][1]/gmd:geographicIdentifier/*[1]/gmd:code |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/gmd:EX_GeographicDescription/gmd:geographicIdentifier/*[1]/gmd:code |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:extent/*[1]/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicDescription'][1]/gmd:geographicIdentifier/*[1]/gmd:code"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 16 - Vertical Extent Information                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi16">
    <sch:title>Vertical extent information</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi16-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:verticalElement/*[1]/gmd:minimumValue |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:extent/*[1]/gmd:verticalElement/*[1]/gmd:maximumValue"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 17 - Spatial Reference System                                                -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi17">
    <sch:title>Spatial reference system</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi17-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/*[1]/gmd:code"
    />
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi17-refSysInfo-1">
    <sch:p>The coordinate reference system(s) used in the described dataset or dataset series shall
      be given using element
      gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier
      INSPIRE Requirements metadata/2.0/req/sds-interoperable/crs and metadata/2.0/req/isdss/crs </sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert
        test="count(//gmd:MD_Metadata[1]/child::gmd:referenceSystemInfo/descendant::gmd:RS_Identifier) &gt; 0"
        > MI-17a (Spatial Reference System): At least one coordinate reference system used in the described dataset, dataset
        series, or service shall be given using
        gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi17-refSysInfo-3">
    <sch:p>If the coordinate reference system is listed in the table Default Coordinate Reference
      System Identifiers in Annex D.4, ... The gmd:codeSpace element shall not be used in this
      case.</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/gmd:RS_Identifier[1]/gmd:code/gmx:Anchor[1]/@xlink:href">
      <!-- associated test for whether code is a default CRS is in supplemental -->
      <sch:report
        test="
          $defaultCRScodes//crs/text()[normalize-space(.) = normalize-space(current()/.)] and
          count(parent::gmx:Anchor/parent::gmd:code/parent::gmd:RS_Identifier/child::gmd:codeSpace) &gt; 0"
        > MI-17b (Spatial Reference System): The coordinate reference system <sch:value-of
          select="normalize-space(current()/.)"/> is listed in Default Coordinate Reference System
        Identifiers in Annex D.4. Such identifiers SHALL NOT use gmd:codeSpace </sch:report>
    </sch:rule>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/gmd:RS_Identifier[1]/gmd:code/gco:CharacterString">
      <!-- associated test for whether code is a default CRS is in supplemental -->
      <sch:report
        test="
          $defaultCRScodes//crs/text()[normalize-space(.) = normalize-space(current()/.)] and
          count(parent::gmd:code/parent::gmd:RS_Identifier/child::gmd:codeSpace) &gt; 0"
        > MI-17c (Spatial Reference System): The coordinate reference system <sch:value-of
          select="normalize-space(current()/.)"/> is listed in Default Coordinate Reference System
        Identifiers in Annex D.4. Such identifiers SHALL NOT use gmd:codeSpace </sch:report>
    </sch:rule>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/gmd:RS_Identifier[1]/gmd:code/gmx:Anchor">
      <sch:report
        test="
          $defaultCRScodes//crs/text()[normalize-space(.) = normalize-space(current()/.)] and
          count(parent::gmd:code/parent::gmd:RS_Identifier/child::gmd:codeSpace) &gt; 0"
        > MI-17d (Spatial Reference System): The coordinate reference system <sch:value-of
          select="normalize-space(current()/.)"/> is listed in Default Coordinate Reference System
        Identifiers in Annex D.4. Such identifiers SHALL NOT use gmd:codeSpace </sch:report>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 18 - Spatial Resolution                                                      -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi18">
    <sch:title>Spatial Resolution</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi18-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution/*[1]/gmd:distance"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 19 - Resource Locator                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi19">
    <sch:title>Resource locator</sch:title>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:distributionInfo/*[1]/gmd:transferOptions/*[1]/gmd:onLine/*[1]">
      <sch:assert
        test="
          count(gmd:linkage) = 0 or
          (starts-with(normalize-space(gmd:linkage/*[1]), 'http://') or
          starts-with(normalize-space(gmd:linkage/*[1]), 'https://') or
          starts-with(normalize-space(gmd:linkage/*[1]), 'ftp://'))"
        > MI-19 (Resource Locator): The value of resource locator does not appear to be a valid URL. It has a value of
          '<sch:value-of select="gmd:linkage/*[1]"/>'. The URL must start with either http://,
        https:// or ftp://. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi19-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:distributionInfo/*[1]/gmd:transferOptions/*[1]/gmd:onLine/*[1]/gmd:linkage"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 21 - Data Format (metadata/2.0/req/isdss/data-encoding)                      -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi21">
    <sch:title>Data Format</sch:title>
    <sch:p>The encoding and the storage or transmission format of the provided datasets or dataset
      series shall be given using the gmd:distributionFormat/gmd:MD_Format element. The multiplicity
      of this element is 1..*. </sch:p>
    <sch:let name="MDFs"
      value="count(//gmd:MD_Metadata[1]/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format)"/>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:distributionInfo/gmd:MD_Distribution">
      <sch:report
        test="($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and ($MDFs &lt; 1)"
        > MI-21a (Data Format): Datasets or dataset series must have at least one
        gmd:distributionFormat/gmd:MD_Format We have <sch:value-of select="$MDFs"/>
      </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi21-versionNils">
    <sch:p>If the version of the encoding is unknown or if the encoding is not versioned, the
      gmd:version shall be left empty and the nil reason attribute shall be provided with either
      value "unknown" or "inapplicable" correspondingly</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:version/*[1]">
      <sch:report
        test="
          ($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and
          (normalize-space(.) = 'NotApplicable' or normalize-space(.) = 'Not Applicable' or
          normalize-space(.) = 'Not entered' or normalize-space(.) = 'Not Entered' or
          normalize-space(.) = 'Missing' or normalize-space(.) = 'missing' or
          normalize-space(.) = 'Unknown' or normalize-space(.) = 'unknown')"
        > MI-21b (Data Format): A value of <sch:value-of select="normalize-space(.)"/> is not expected here. If
        the version of the encoding is not known, then use nilReason='unknown', otherwise if the
        encoding is not versioned use nilReason='inapplicable', like: &lt;gmd:version
        nilReason='unknown' /&gt; </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi21-Name-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:distributionInfo/*[1]/gmd:distributionFormat/*[1]/gmd:name"/>
  </sch:pattern>
  <sch:pattern is-a="TypeNillableVersionPattern" id="Gemini2-mi21-Version-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:distributionInfo/*[1]/gmd:distributionFormat/*[1]/gmd:version"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 23 - Responsible Organisation                                                -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-23">
    <sch:title>Responsible organisation</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:pointOfContact) &gt;= 1"> MI-23a (Responsible Organisation): Responsible organisation is
        mandatory. At least one shall be provided. </sch:assert>
    </sch:rule>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact">
      <sch:assert test="count(@gco:nilReason) = 0"> MI-23b (Responsible Organisation): The value of responsible organisation
        shall not be null. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="ResponsiblePartyPattern" id="Gemini2-mi23-ResponsibleParty">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact"/>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi23-OrganisationName-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:organisationName |
      //gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress"
    />
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi23-Role-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:pointOfContact/*[1]/gmd:role/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 24 - Frequency of Update                                                     -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi24">
    <sch:title>Frequency of update</sch:title>
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi24-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceMaintenance/*[1]/gmd:maintenanceAndUpdateFrequency/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 25 - Limitations on Public Access                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi25-LimitationsOnPublicAccess">
    <sch:title>LimitationsOnPublicAccess codelist</sch:title>
    <sch:p>We need metadata to have a gmx:Anchor linking to one of the LimitationsOnPublicAccess codelist values from: http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess</sch:p>
    <sch:let name="LoPAurl" value="'http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/'"/>
    <sch:let name="LoPAurlNum" value="count(//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gmx:Anchor/@xlink:href[contains(.,$LoPAurl)])"/>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:report test="$LoPAurlNum != 1">
        MI-25c (Limitations on Public Access): There must be one (and only one) LimitationsOnPublicAccess code list value specified using a gmx:Anchor in gmd:otherConstraints.
        We have <sch:value-of select="$LoPAurlNum"/>
      </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi25-OtherConstraints-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:otherConstraints"
    />
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi25-AccessConstraints-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:accessConstraints/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 26 - Use Constraints                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi26-UseConstraints-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:resourceConstraints/*[1]/gmd:useConstraints/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 27 - Additional Information Source                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi27">
    <sch:title>Additional information source</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi27-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:supplementalInformation"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 30 - Metadata Date                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi30">
    <sch:title>Metadata date</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi30-NotNillable">
    <sch:param name="context" value="//gmd:MD_Metadata[1]/gmd:dateStamp/gco:Date"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 33 - Metadata Language                                                       -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi33">
    <sch:title>Metadata language</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert test="count(gmd:language) = 1"> MI-33 (Metadata Language): Metadata language is mandatory. One shall
        be provided. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="LanguagePattern" id="Gemini2-mi33-Language">
    <sch:param name="context" value="//gmd:MD_Metadata[1]/gmd:language"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 35 - Metadata Point of Contact                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi35">
    <sch:title>Metadata point of contact</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:contact">
      <sch:assert test="count(@gco:nilReason) = 0"> MI-35a (Metadata Point of Contact): The value of metadata point of contact
        shall not be null. </sch:assert>
      <sch:assert
        test="count(parent::node()[gmd:contact/*[1]/gmd:role/*[1]/@codeListValue = 'pointOfContact']) >= 1"
        > MI-35b (Metadata Point of Contact): At least one metadata point of contact shall have the role 'pointOfContact'.
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="ResponsiblePartyPattern" id="Gemini2-mi35-ResponsibleParty">
    <sch:param name="context" value="//gmd:MD_Metadata[1]/gmd:contact"/>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi35-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:contact/*[1]/gmd:organisationName | //gmd:MD_Metadata[1]/gmd:contact/*[1]/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 36 - (Unique) Resource Identifier                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi36">
    <sch:title>(Unique) Resource Identifier</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]">
      <sch:assert
        test="
          ((../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          ../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          count(gmd:identifier) &gt;= 1) or
          (../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          ../../../../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(../../../../gmd:hierarchyLevel) = 0"
        > MI-36 (Unique) Resource Identifier: (Unique) Resource Identifier is mandatory for datasets and series. One or more
        shall be provided. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Ensure that (Unique) Resource Identifier has a value -->
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi36-Code-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:identifier/*[1]/gmd:code"
    />
  </sch:pattern>
  <!-- Ensure that a code space value is provided if the element is encoded -->
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi36-CodeSpace-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation/*[1]/gmd:identifier/*[1]/gmd:codeSpace"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 37 - Spatial Data Service Type                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi37">
    <sch:title>Spatial data service type</sch:title>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/srv:SV_ServiceIdentification | /*[1]/gmd:identificationInfo[1]/*[@gco:isoType = 'srv:SV_ServiceIdentification'][1]">
      <sch:assert
        test="
          (../../gmd:hierarchyLevel/*[1]/@codeListValue = 'service' and
          count(srv:serviceType) = 1) or
          ../../gmd:hierarchyLevel/*[1]/@codeListValue != 'service'"
        > MI-37a (Spatial Data Service Type): If the resource type is service, one spatial data service type shall be provided. </sch:assert>
      <sch:assert
        test="
          srv:serviceType/*[1] = 'discovery' or
          srv:serviceType/*[1] = 'view' or
          srv:serviceType/*[1] = 'download' or
          srv:serviceType/*[1] = 'transformation' or
          srv:serviceType/*[1] = 'invoke' or
          srv:serviceType/*[1] = 'other'"
        > MI-37b (Spatial Data Service Type): Service type shall be one of 'discovery', 'view', 'download', 'transformation',
        'invoke' or 'other' following INSPIRE generic names. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi37-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:serviceType"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 38 - Coupled Resource                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi38">
    <sch:title>Coupled resource</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/srv:operatesOn">
      <sch:assert test="count(@xlink:href) = 1"> MI-38 (Coupled Resource): Coupled resource shall be implemented by
        reference using the xlink:href attribute. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 39 - Resource Type (aka 46 - Hierarchy Level)                                -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi39">
    <sch:title>Resource type</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert test="count(gmd:hierarchyLevel) = 1"> MI-39a (Resource Type): Resource type is mandatory. One
        shall be provided. </sch:assert>
      <sch:assert
        test="
          gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series' or
          gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'service'"
        > MI-39b (Resource Type): Value of resource type shall be 'dataset', 'series' or 'service'. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi39-CodeList">
    <sch:param name="context" value="//gmd:MD_Metadata[1]/gmd:hierarchyLevel/*[1]"/>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 41 - Conformity                                                              -->
  <!-- Explanation is a required element but can be empty                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi41">
    <sch:title>Conformity</sch:title>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi41-confResult">
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert
        test="count(gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult) &gt; 0"
        > MI-41a (Conformity): There must be at least one gmd:DQ_ConformanceResult </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- We need tests that WHEN we have INSPIRE conformance sections they have correct content -->
  <sch:pattern fpi="Gemini2-mi41-inspire1089">
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = 'Commission Regulation (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services']">
      <sch:let name="localPassPath"
        value="parent::gmd:title/parent::gmd:CI_Citation/parent::gmd:specification/following-sibling::gmd:pass"/>
      <sch:let name="localDatePath"
        value="parent::gmd:title/following-sibling::gmd:date/gmd:CI_Date"/>
      <sch:assert test="$localPassPath/gco:Boolean or $localPassPath/@gco:nilReason = 'unknown'">
        MI-41b (Conformity): The pass value shall be true, false, or have a nil reason of 'unknown', in a
        conformance statement for <sch:value-of select="$inspire1089"/>
      </sch:assert>
      <!-- Other dates (creation 2010-11-23, revision 2013-12-30) ref: http://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:02010R1089-20131230 -->
      <!-- Publication date ref: https://inspire.ec.europa.eu/inspire-legislation/26 -->
      <sch:assert test="$localDatePath/gmd:date/gco:Date[normalize-space(text()) = '2010-12-08']">
        MI-41c (Conformity): The date reported shall be 2010-12-08 (date of publication), in a conformance
        statement for <sch:value-of select="$inspire1089"/>
      </sch:assert>
      <sch:assert
        test="$localDatePath/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue = 'publication']">
        MI-41d (Conformity): The dateTypeCode reported shall be publication, in a conformance statement for
          <sch:value-of select="$inspire1089"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi41-inspire1089x">
    <sch:p>This test allows for the title to start with `COMMISSION REGULATION` but ss. it should be
      'Commission Regulation'</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = 'COMMISSION REGULATION (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services']">
      <sch:let name="localPassPath"
        value="parent::gmd:title/parent::gmd:CI_Citation/parent::gmd:specification/following-sibling::gmd:pass"/>
      <sch:let name="localDatePath"
        value="parent::gmd:title/following-sibling::gmd:date/gmd:CI_Date"/>
      <sch:assert test="$localPassPath/gco:Boolean or $localPassPath/@gco:nilReason = 'unknown'">
        MI-41e (Conformity): The pass value shall be true, false, or have a nil reason of 'unknown', in a
        conformance statement for <sch:value-of select="$inspire1089"/>
      </sch:assert>
      <!-- Other dates (creation 2010-11-23, revision 2013-12-30) ref: http://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:02010R1089-20131230 -->
      <!-- Publication date ref: https://inspire.ec.europa.eu/inspire-legislation/26 -->
      <sch:assert test="$localDatePath/gmd:date/gco:Date[normalize-space(text()) = '2010-12-08']">
        MI-41f (Conformity): The date reported shall be 2010-12-08 (date of publication), in a conformance
        statement for <sch:value-of select="$inspire1089"/>
      </sch:assert>
      <sch:assert
        test="$localDatePath/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue = 'publication']">
        MI-41g (Conformity): The DateTypeCode reported shall be publication, in a conformance statement for
          <sch:value-of select="$inspire1089"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi41-inspire976">
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = 'Commission Regulation (EC) No 976/2009 of 19 October 2009 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards the Network Services']">
      <sch:let name="localPassPath"
        value="parent::gmd:title/parent::gmd:CI_Citation/parent::gmd:specification/following-sibling::gmd:pass"/>
      <sch:let name="localDatePath"
        value="parent::gmd:title/following-sibling::gmd:date/gmd:CI_Date"/>
      <sch:assert test="$localPassPath/gco:Boolean or $localPassPath/@gco:nilReason = 'unknown'">
        MI-41h (Conformity): The pass value shall be true, false, or have a nil reason of 'unknown', in a
        conformance statement for <sch:value-of select="$inspire976"/>
      </sch:assert>
      <!-- Other dates (creation 2009-10-19, revision 2010-12-28) ref: http://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:02009R0976-20101228 -->
      <!-- Publication date ref: https://inspire.ec.europa.eu/inspire-legislation/26 -->
      <sch:assert test="$localDatePath/gmd:date/gco:Date[normalize-space(text()) = '2010-12-08']">
        MI-41i (Conformity): The date reported shall be 2010-12-08 (date of publication), in a conformance
        statement for <sch:value-of select="$inspire976"/>
      </sch:assert>
      <sch:assert
        test="$localDatePath/gmd:dateType/gmd:CI_DateTypeCode[@codeListValue = 'publication']">
        MI-41j (Conformity): The dateTypeCode reported shall be publication, in a conformance statement for
          <sch:value-of select="$inspire976"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi41-inspireConf-sv">
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'service']">
      <sch:let name="count1089"
        value="count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089])"/>
      <sch:let name="count1089x"
        value="count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089x])"/>
      <sch:let name="count976"
        value="count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire976])"/>
      <sch:assert test="$count1089 &lt;= 1"> M1-41k (Conformity): A service record should have no more than one
        Conformance report to [1089/2010] (counted <sch:value-of select="$count1089"/>) </sch:assert>
      <sch:assert test="$count1089x &lt;= 1"> M1-41l (Conformity): A service record should have no more than one
        Conformance report to [1089/2010] (counted <sch:value-of select="$count1089"/>) </sch:assert>
      <sch:assert test="$count976 &lt;= 1"> M1-41m (Conformity): A service record should have no more than one
        Conformance report to [976/2009] (counted <sch:value-of select="$count976"/>) </sch:assert>
      <sch:report
        test="
          not(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089]) and
          not(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089x]) and
          not(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire976])"
        > M1-41n (Conformity): A service record should have a Conformance report to [976/2009] or [1089/2010]
      </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi41-inspireConf-dss">
    <sch:rule
      context="
        //gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'dataset'] |
        //gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'series']">
      <sch:assert
        test="
          count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089]) = 1 or
          count(parent::gmd:level/parent::gmd:DQ_Scope/parent::gmd:scope/following-sibling::gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][normalize-space(text()) = $inspire1089x]) = 1"
        > MI-41o (Conformity): Datasets and series must provide a conformance report to [1089/2010]. The INSPIRE
        rule tells us this must be the EXACT title of the regulation, which is: <sch:value-of
          select="$inspire1089"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi41-Explanation-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:explanation"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 42 - Specification                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi42">
    <sch:title>Specification</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-mi42-Title-NotNillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:title"
    />
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi42-Date-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:date/*[1]/gmd:date"
    />
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi42-DateType-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/*[1]/gmd:report/*[1]/gmd:result/*[1]/gmd:specification/*[1]/gmd:date/*[1]/gmd:date/*[1]/gmd:dateType/*[1]"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 43 - Equivalent scale                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi43">
    <sch:title>Equivalent scale</sch:title>
  </sch:pattern>
  <sch:pattern is-a="TypeNillablePattern" id="Gemini2-mi43-Nillable">
    <sch:param name="context"
      value="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:spatialResolution/*[1]/gmd:equivalentScale/*[1]/gmd:denominator"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 44 - Geographic Bounding Box  (see MI 11, 12, 13, 14)                        -->
  <!-- ========================================================================================== -->
  <!-- ========================================================================================== -->
  <!-- Metadata Item 47 - Hierarchy level name                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi47">
    <sch:title>Hierarchy level name</sch:title>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi47-general">
    <sch:p>Hierarchy level name is mandatory for dataset series and services, not required for
      datasets</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:let name="hierLevelNameCount" value="count(gmd:hierarchyLevelName)"/>
      <sch:report
        test="$hierLevelNameCount = 0 and ($hierarchyLevelCLValue = 'service' or $hierarchyLevelCLValue = 'series')"
        > MI-47a (Hierarchy level name): Need at least one hierarchyLevelName have: <sch:value-of
          select="$hierLevelNameCount"/>
      </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi47-services-restriction">
    <sch:p>TG Requirement 3.1: metadata/2.0/req/sds/resource-type Additionally the name of the
      hierarchy level shall be given using element gmd:hierarchyLevelName element with a Non-empty
      Free Text Element containing the term "service" in the language of the metadata.</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:hierarchyLevelName/*[1]">
      <sch:let name="hierLevelcListVal" value="preceding::gmd:hierarchyLevel/*/@codeListValue"/>
      <sch:let name="hierLevelNameText" value="descendant-or-self::text()"/>
      <sch:report test="($hierLevelcListVal = 'service' and $hierLevelNameText != 'service')">
        MI-47b (Hierarchy level name): Hierarchy level name for services must have value "service" </sch:report>
      <sch:assert test="normalize-space(.)"> MI-47c: Hierarchy level name for services must have
        value "service" </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 48 - Quality Scope                                                           -->
  <!-- Also see AT 8                                                                              -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi48">
    <sch:title>Quality Scope</sch:title>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert test="count(gmd:dataQualityInfo) &gt; 0"> MI-48a (Quality Scope): There must be at least one
        gmd:dataQualityInfo </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi48-series">
    <sch:p>TG Requirement 1.9: metadata/2.0/req/datasets-and-series/one-data-quality-element</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:hierarchyLevel/gmd:MD_ScopeCode[@codeListValue = 'series']">
      <sch:let name="dssDQ"
        value="count(//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'series'])"/>
      <sch:assert test="$dssDQ = 1"> MI-48b (Quality Scope): There shall be exactly one
        gmd:dataQualityInfo/gmd:DQ_DataQuality element scoped to the entire described dataset
        series, but here we have <sch:value-of select="$dssDQ"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi48-dataset">
    <sch:p>TG Requirement 1.9: metadata/2.0/req/datasets-and-series/one-data-quality-element</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:hierarchyLevel/gmd:MD_ScopeCode[@codeListValue = 'dataset']">
      <sch:let name="dsDQ"
        value="count(//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'dataset'])"/>
      <sch:assert test="$dsDQ = 1"> MI-48c (Quality Scope): There shall be exactly one
        gmd:dataQualityInfo/gmd:DQ_DataQuality element scoped to the entire described dataset, but
        here we have <sch:value-of select="$dsDQ"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi48-service">
    <sch:p>TG Requirement 3.8: metadata/2.0/req/sds/only-one-dq-element</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:hierarchyLevel/gmd:MD_ScopeCode[@codeListValue = 'service']">
      <sch:let name="svDQ"
        value="count(//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'service'])"/>
      <sch:assert test="$svDQ = 1"> MI-48d (Quality Scope): There shall be exactly one
        gmd:dataQualityInfo/gmd:DQ_DataQuality element scoped to the entire described service, but
        here we have <sch:value-of select="$svDQ"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-mi48-service-1">
    <sch:p>The level shall be named using element
      gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other element with a
      Non-empty Free Text Element containing the term "service" in the language of the metadata.
      (metadata/2.0/req/sds/only-one-dq-element)</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode[@codeListValue = 'service']">
      <sch:assert test="count(following::gmd:levelDescription) = 1"> MI-48e (Quality Scope): gmd:levelDescription is
        missing ~ the level shall be named using element
        gmd:scope/gmd:DQ_Scope/gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other element with a
        Non-empty Free Text Element containing the term "service" </sch:assert>
      <sch:report
        test="
          following::gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other/gco:CharacterString/text() != 'service' or
          following::gmd:levelDescription/gmd:MD_ScopeDescription/gmd:other/gmx:Anchor/text() != 'service'"
        > MI-48f (Quality Scope): Value (gmd:MD_ScopeDescription/gmd:other) should be "service" </sch:report>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 50 - Spatial representation type                                             -->
  <!-- metadata/2.0/req/isdss/spatial-representation-type                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="metadata/2.0/req/isdss/spatial-representation-type">
    <sch:title>Spatial Representation Type</sch:title>
    <sch:p>Dataset and dataset series must have a MD_SpatialRepresentationTypeCode</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/gmd:MD_DataIdentification[1]">
      <sch:assert
        test="($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and count(gmd:spatialRepresentationType) &gt; 0"
        > MI-50a (Spatial representation type): Dataset and dataset series metadata must have at least one
        gmd:spatialRepresentationType with gmd:MD_SpatialRepresentationTypeCode. The codeListValue
        must be one of 'vector', 'grid', 'tin', or 'textTable' </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/isdss/spatial-representation-type-values">
    <sch:p>MD_SpatialRepresentationTypeCode, ... must be one of 'vector', 'grid', 'tin', or
      'textTable'</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/gmd:MD_DataIdentification[1]/gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode">
      <sch:assert
        test="
          ($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and
          (@codeListValue = 'vector' or @codeListValue = 'grid' or @codeListValue = 'tin' or @codeListValue = 'textTable')"
        > MI-50b (Spatial representation type): codeListValue must be one of 'vector', 'grid', 'tin', or 'textTable' </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/isdss/spatial-representation-typeNN">
    <sch:title>Spatial Representation Type is not nillable for dataset/series</sch:title>
    <sch:p>Dataset and dataset series must have a MD_SpatialRepresentationTypeCode</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/gmd:MD_DataIdentification[1]/gmd:spatialRepresentationType">
      <sch:assert
        test="($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and count(gmd:MD_SpatialRepresentationTypeCode) &gt; 0"
        > MI-50c (Spatial representation type): Dataset and dataset series metadata must have at least one
        gmd:spatialRepresentationType with gmd:MD_SpatialRepresentationTypeCode. The codeListValue
        must be one of 'vector', 'grid', 'tin', or 'textTable' </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi50-SRType-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 51 - Character encoding                                                      -->
  <!-- metadata/2.0/req/isdss/character-encoding                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-mi51">
    <sch:title>Character encoding</sch:title>
    <sch:p>The character encoding(s) shall be given for datasets and datasets series which use
      encodings not based on UTF-8 by using element gmd:characterSet/gmd:MD_CharacterSetCode
      referring to one of the values of ISO 19139 code list MD_CharacterSetCode.</sch:p>
    <sch:p>The multiplicity of this element is 0..n. If more than one character encoding is used
      within the described dataset or datasets series, all used character encodings, including UTF-8
      (code list value "utf8"), shall be given using this element</sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:characterSet/gmd:MD_CharacterSetCode[1]/@codeListValue">
      <sch:assert
        test="
          ($hierarchyLevelCLValue = 'dataset' or $hierarchyLevelCLValue = 'series') and
          $charSetCodes//gml:identifier/text()[normalize-space(.) = normalize-space(current()/.)]"
        > MI-51 (Character encoding): "<sch:value-of select="normalize-space(.)"/>" is not one of the values of ISO 19139
        code list MD_CharacterSetCode </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="IsoCodeListPattern" id="Gemini2-mi51-CharSet-CodeList">
    <sch:param name="context"
      value="//gmd:MD_Metadata/gmd:identificationInfo[1]/gmd:MD_DataIdentification/gmd:characterSet/gmd:MD_CharacterSetCode"
    />
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Metadata Item 52 - Topological consistency                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="metadata/2.0/req/isdss/topological-consistency-quantitative-results">
    <sch:p>When we have a DQ_QuantitativeResult for a gmd:DQ_TopologicalConsistency report, the
      result type shall be declared using the xsi:type attribute of the gco:Record element </sch:p>
    <sch:rule
      context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_TopologicalConsistency/gmd:result/gmd:DQ_QuantitativeResult/gmd:value">
      <sch:assert test="count(gco:Record/@xsi:type) = 1"> MI-52a (Topological consistency): The result type shall be declared
        using the xsi:type attribute of the gco:Record element </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/isdss/topological-consistency-descriptive-results">
    <sch:title>Topological consistency</sch:title>
    <sch:p>In the event that a Topological consistency report is required for a Generic Network
      Model dataset, check that the correct date/datetype and boolean values are given. Test relies
      on the citation having the required title...</sch:p>
    <sch:let name="GenericNetworkModelValue"
      value="'INSPIRE Data Specifications - Base Models - Generic Network Model'"/>
    <sch:let name="GenericNetworkModelDate" value="'2013-04-05'"/>
    <sch:rule
      context="//gmd:DQ_TopologicalConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/gco:CharacterString[normalize-space(text()) = 'INSPIRE Data Specifications - Base Models - Generic Network Model']">
      <sch:report test="following::gmd:date/gmd:CI_Date/gmd:date/gco:Date[text() != '2013-04-05']">
        MI-52b (Topological consistency): When TopologicalConsistency is for <sch:value-of select="$GenericNetworkModelValue"
        />, the date given shall be the date of publication of the Generic Network Model, which is
        2013-04-05 </sch:report>
      <sch:report
        test="following::gmd:dateType/gmd:CI_DateTypeCode[@codeListValue != 'publication']"> MI-52c (Topological consistency):
        When TopologicalConsistency is for <sch:value-of select="$GenericNetworkModelValue"/>, the
        code list value shall always be publication </sch:report>
      <!-- explanation is needed, empty free text is caught elsewhere and gmd:explanation is required by schema -->
      <sch:assert test="count(following::gmd:explanation/@gco:nilReason) = 0"> MI-52d (Topological consistency): When
        TopologicalConsistency is for <sch:value-of select="$GenericNetworkModelValue"/>, Some
        statement on topological consistency must be provided in the explanation</sch:assert>
      <sch:assert test="following::gmd:pass/gco:Boolean = 'false'"> MI-52e (Topological consistency): When
        TopologicalConsistency is for <sch:value-of select="$GenericNetworkModelValue"/>, The value
        shall always be false to indicate that the data does not assure the centerline topology for
        the network </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Ancillary Tests                                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="Gemini2-at1">
    <sch:title>Data identification citation</sch:title>
    <sch:p>The identification information citation cannot be null.</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]/gmd:citation">
      <sch:assert test="count(@gco:nilReason) = 0"> AT-1: Identification information citation shall
        not be null. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at2">
    <sch:title>Metadata resource type test</sch:title>
    <sch:p>Test to ensure that metadata about datasets include the gmd:MD_DataIdentification element
      and metadata about services include the srv:SV_ServiceIdentification element</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]">
      <sch:assert
        test="
          ((../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'dataset' or
          ../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'series') and
          (local-name(*) = 'MD_DataIdentification' or */@gco:isoType = 'gmd:MD_DataIdentification')) or
          (../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'dataset' and
          ../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'series') or
          count(../gmd:hierarchyLevel) = 0"
        > AT-2a: The first identification information element shall be of type
        gmd:MD_DataIdentification. </sch:assert>
      <sch:assert
        test="
          ((../gmd:hierarchyLevel[1]/*[1]/@codeListValue = 'service') and
          (local-name(*) = 'SV_ServiceIdentification' or */@gco:isoType = 'srv:SV_ServiceIdentification')) or
          (../gmd:hierarchyLevel[1]/*[1]/@codeListValue != 'service') or
          count(../gmd:hierarchyLevel) = 0"
        > AT-2b: The first identification information element shall be of type
        srv:SV_ServiceIdentification. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at3">
    <sch:title>Metadata file identifier</sch:title>
    <sch:p>A file identifier is required</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]">
      <sch:assert test="count(gmd:fileIdentifier) = 1"> AT-3a: A metadata file identifier shall be
        provided. Its value shall be a system generated GUID. </sch:assert>
      <sch:report test="contains(gmd:fileIdentifier, '{') or contains(gmd:fileIdentifier, '}')">
        AT-3b: File identifier shouldn't contain braces </sch:report>
    </sch:rule>
  </sch:pattern>
  <sch:pattern is-a="TypeNotNillablePattern" id="Gemini2-at3-NotNillable">
    <sch:param name="context" value="//gmd:MD_Metadata[1]/gmd:fileIdentifier"/>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at4">
    <sch:title>Constraints</sch:title>
    <sch:p>Constraints (Limitations on public access and use constraints) are required.</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo[1]/*[1]">
      <sch:assert test="count(gmd:resourceConstraints) &gt;= 1"> AT-4: Limitations on public access
        and use constraints are required. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at5">
    <!-- metadata/2.0/req/common/max-1-date-of-creation -->
    <sch:title>Creation date type</sch:title>
    <sch:p>Constrain citation date type = creation to one occurrence.</sch:p>
    <sch:rule context="//gmd:CI_Citation | //*[@gco:isoType = 'gmd:CI_Citation'][1]">
      <sch:assert test="count(gmd:date/*[1]/gmd:dateType/*[1][@codeListValue = 'creation']) &lt;= 1"
        > AT-5: There shall not be more than one creation date. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at6">
    <sch:title>Non-empty free text content</sch:title>
    <sch:p>Don't allow empty Free text gco:CharacterString or gmx:Anchor</sch:p>
    <sch:rule context="//gco:CharacterString | //gmx:Anchor">
      <sch:assert test="normalize-space(.)"> AT-6: Free text elements should not be empty
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="metadata/2.0/req/common/max-1-date-of-last-revision">
    <sch:title>Revision date type</sch:title>
    <sch:p>Constrain citation date type = revision to one occurrence.</sch:p>
    <sch:rule context="//gmd:CI_Citation | //*[@gco:isoType = 'gmd:CI_Citation'][1]">
      <sch:assert test="count(gmd:date/*[1]/gmd:dateType/*[1][@codeListValue = 'revision']) &lt;= 1"
        > AT-7: There shall not be more than one revision date. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern fpi="Gemini2-at8">
    <sch:title>Legal Constraints</sch:title>
    <sch:p>To satisfy INSPIRE TG Requirement C.18, there must be at least two gmd:resourceConstraints : md:MD_LegalConstraints element blocks
      One for "Limitations on public access" and the other for "Conditions for access and use".  Applies to all metadata</sch:p>
    <sch:rule context="//gmd:MD_Metadata[1]/gmd:identificationInfo">
      <sch:let name="legalCons" value="count(//gmd:MD_Metadata[1]/gmd:identificationInfo/*[1]/gmd:resourceConstraints/gmd:MD_LegalConstraints)"/>
      <sch:assert test="$legalCons &gt; 1">
        AT-8: There must be at least two Legal Constraints sections (gmd:resourceConstraints/gmd:MD_LegalConstraints) in the metadata but we have <sch:value-of select="$legalCons"/>.  
        One section shall be provided to describe the "Limitations on public access" and another shall be provided to describe the 
        "Conditions for access and use"
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- ========================================================================================== -->
  <!-- Abstract Patterns                                                                          -->
  <!-- ========================================================================================== -->
  <!-- Test that an element has a value or has a valid nilReason value -->
  <sch:pattern abstract="true" id="TypeNillablePattern">
    <sch:rule context="$context">
      <sch:assert
        test="
          (string-length(normalize-space(.)) &gt; 0) or
          (@gco:nilReason = 'inapplicable' or
          @gco:nilReason = 'missing' or
          @gco:nilReason = 'template' or
          @gco:nilReason = 'unknown' or
          @gco:nilReason = 'withheld' or
          starts-with(@gco:nilReason, 'other:'))"
        > AP-1a: The <sch:name/> element shall have a value or a valid Nil Reason. This test may be called by the 
        following Metadata Items: 2 - Alternative Title, 36 - (Unique) Resource Identifier,
        37 - Spatial Data Service Type 41 - Conformity, 42 - Specification, and 43 - Equivalent
        scale </sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern abstract="true" id="TypeNillableVersionPattern">
    <sch:rule context="$context">
      <sch:assert
        test="
          (string-length(normalize-space(.)) &gt; 0) or
          (@gco:nilReason = 'inapplicable' or @gco:nilReason = 'unknown')"
        > AP-1b: The <sch:name/> element shall have a value OR a nil reason of either 'inapplicable'
        or 'unknown'. This test may be called by the following Metadata Items: 21 - Data Format</sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Test that an element has a value - the value is not nillable -->
  <sch:pattern abstract="true" id="TypeNotNillablePattern">
    <sch:rule context="$context">
      <sch:assert test="string-length(.) &gt; 0 and count(./@gco:nilReason) = 0"> AP-2: The
        <sch:name/> element is not nillable and shall have a value. This test may be called by the following 
        Metadata Items: 1 - Title, 4 - Abstract, 6 - Keyword, 11, 12, 13, 14 - Geographic Bounding
        Box, 17 - Spatial Reference System, 23 - Responsible Organisation, 30 - Metadata Date, 35 -
        Metadata Point of Contact, 36 - (Unique) Resource Identifier, 42 - Specification, and in the
        Ancillary test 3 - Metadata file identifier </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Test ISO code lists -->
  <sch:pattern abstract="true" id="IsoCodeListPattern">
    <sch:rule context="$context">
      <sch:assert test="string-length(@codeListValue) &gt; 0"> AP-3: The codeListValue attribute
        does not have a value. This test may be called by the following Metadata Items: 6 - Keyword, 8 -
        Dataset Reference Date, 23 - Responsible Organisation, 24 - Frequency of Update, 25 -
        Limitations on Public Access, 26 - Use Constraints, 39 - Resource Type (aka 46 - Hierarchy Level), 42 -
        Specification, 50 - Spatial representation type, and 51 - Character encoding </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Test the language values (Metadata and Resource) -->
  <sch:pattern abstract="true" id="LanguagePattern">
    <sch:rule context="$context">
      <sch:assert test="count(gmd:LanguageCode) = 1"> AP-4a: Language shall be implemented with
        gmd:LanguageCode. <sch:value-of select="$LPreportsupplement"/>
      </sch:assert>
    </sch:rule>
    <sch:rule context="$context/gmd:LanguageCode">
      <sch:assert test="string-length(@codeListValue) &gt; 0"> AP-4b: The language code list value
        is absent. When a dataset has no natural language use code zxx. <sch:value-of
          select="$LPreportsupplement"/>
      </sch:assert>
      <sch:report test="string-length(@codeListValue) != 3"> AP-4c: The language code should be
        three characters. <sch:value-of select="$LPreportsupplement"/>
      </sch:report>
    </sch:rule>
  </sch:pattern>
  <!-- Test for the responsible party information -->
  <sch:pattern abstract="true" id="ResponsiblePartyPattern">
    <!-- Count of Organisation Name and Individual Name >= 1 -->
    <sch:rule context="$context">
      <sch:assert test="count(*/gmd:organisationName) = 1"> AP-5a: One organisation name shall be
        provided. <sch:value-of select="$RPreportsupplement"/>
      </sch:assert>
      <sch:assert
        test="count(*/gmd:contactInfo/*[1]/gmd:address/*[1]/gmd:electronicMailAddress) = 1"> AP-5b:
        One email address shall be provided. <sch:value-of select="$RPreportsupplement"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Test for gmd:MD_GeographicBoundingBox values -->
  <sch:pattern abstract="true" id="GeographicBoundingBoxPattern">
    <sch:rule context="$context">
      <!-- West Bound Longitude -->
      <sch:assert
        test="string-length(gmd:westBoundLongitude) = 0 or (gmd:westBoundLongitude &gt;= -180.0 and gmd:westBoundLongitude &lt;= 180.0)"
        > AP-6a: West bound longitude has a value of <sch:value-of select="gmd:westBoundLongitude"/>
        which is outside bounds. <sch:value-of select="$GBreportsupplement"/></sch:assert>
      <!-- East Bound Longitude -->
      <sch:assert
        test="string-length(gmd:eastBoundLongitude) = 0 or (gmd:eastBoundLongitude &gt;= -180.0 and gmd:eastBoundLongitude &lt;= 180.0)"
        >AP-6b: East bound longitude has a value of <sch:value-of select="gmd:eastBoundLongitude"/>
        which is outside bounds. <sch:value-of select="$GBreportsupplement"/></sch:assert>
      <!-- South Bound Latitude -->
      <sch:assert
        test="string-length(gmd:southBoundLatitude) = 0 or (gmd:southBoundLatitude &gt;= -90.0 and gmd:southBoundLatitude &lt;= gmd:northBoundLatitude)"
        >AP-6c: South bound latitude has a value of <sch:value-of select="gmd:southBoundLatitude"/>
        which is outside bounds. <sch:value-of select="$GBreportsupplement"/></sch:assert>
      <!-- North Bound Latitude -->
      <sch:assert
        test="string-length(gmd:northBoundLatitude) = 0 or (gmd:northBoundLatitude &lt;= 90.0 and gmd:northBoundLatitude &gt;= gmd:southBoundLatitude)"
        >AP-6d: North bound latitude has a value of <sch:value-of select="gmd:northBoundLatitude"/>
        which is outside bounds. <sch:value-of select="$GBreportsupplement"/></sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
