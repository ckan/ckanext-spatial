<?xml version="1.0" encoding="utf-8" ?>

<!-- ========================================================================================== -->
<!-- Schematron Schema for the ISO / TS 19139 Table A.1 Constraints                             -->
<!-- ========================================================================================== -->

<!-- 
     James Rapaport                                
     SeaZone Solutions Limited                                                  
     2009-05-03                                                        

     This Schematron schema has been developed by SeaZone Solutions Limited (SeaZone).  
     It is designed to validate the constraints set out in Table A.1 of ISO / TS 19139. The 
     schema is provided "as is," without warranty of any kind, express or implied.  
     Under no circumstances shall SeaZone or any contributing parties be held liable for any 
     damages arising in any way from the use of this schema.
     
     Copyright
     This Schematron schema and any associated material may be used and reproduced free of charge 
     provided that it is done so accurately and not in any misleading context or in a derogatory 
     manner. The Schematron schema must be acknowledged as being sourced from SeaZone Solutions 
     Limited (SeaZone) and this cited when it is reproduced as part of another schema, software, 
     publication or service.
     
     Disclaimer
     This Schematron schema and any associated material has been compiled from sources believed 
     to be proven in practice and reliable but no warranty, expressed or implied, is given that 
     it is complete or accurate nor that it is fit for any particular purpose.  All such 
     warranties are expressly disclaimed and excluded and users are therefore recommended to 
     seek professional advice prior to its use.

     This Schematron schema has been developed by SeaZone Solutions Limited. It is designed to 
     test the constraints presented in Table A.1 of ISO / TS 19139.
     
     The schema has been developed for XSLT Version 1.0 and tested with the ISO 19757-3 Schematron
     XML Stylesheets issued on 2009-03-18 at http://www.schematron.com/tmp/iso-schematron-xslt1.zip 
     
     The schema tests constraints on ISO / TS 19139 encoded metadata. The rules expressed in this 
     schema apply in addition to validation by the ISO / TS 19139 schemas.
     
     Document History:
     
     2009-05-03 - Version 0.1
     First draft
     
     2009-11-06 - Version 1.0
     Release - no changes from version 0.1
     
     2009-12-07 - Version 1.1
     Changed version number attribute in root element
     Added more report information to aid with debugging
     
     2010-01-15 - Version 1.2
     Table A.1 Row 10 - Test altered
     
     2010-02-01 - Version 1.3
     All sch:report elements removed from the schema. These elements cause svrl:successful-report
     elements to be output in SVRL. oXygen 10.x interprets these elements as warnings while 11.1
     interprets them as errors. The intention in the context of this schema was that svrl:successful-report
     would be interpretted as information.
-->

<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt" schemaVersion="1.3">

  <sch:title>ISO / TS 19139 Table A.1 Constraints</sch:title>

  <sch:p>
    This Schematron schema is designed to test the constraints presented in ISO / TS 19139 Table A.1.
  </sch:p>

  <!-- Namespaces from ISO 19139 Metadata encoding -->
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2" />
  <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>

  <!-- Namespace for ISO 19119 - Metadata Describing Services - Note: no standardised schema -->
  <sch:ns prefix="srv" uri="http://www.isotc211.org/2005/srv"/>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Conformance rules not enforceable with XML Schema                 -->
  <!-- ========================================================================================== -->

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 1                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW1">
    <sch:title>ISO / TS 19139 Table A.1 Row 1</sch:title>
    <sch:p>language: documented if not defined by the encoding standard</sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 2                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW2">
    <sch:title>ISO / TS 19139 Table A.1 Row 2</sch:title>
    <sch:p>
      characterSet: documented if ISO/IEC 10646 not used and not defined by the encoding standard
    </sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 3                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW3">
    <sch:title>ISO / TS 19139 Table A.1 Row 3</sch:title>
    <sch:p>
      characterSet: documented if ISO/IEC 10646 is not used
    </sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 4                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW4">
    <sch:title>ISO / TS 19139 Table A.1 Row 4</sch:title>
    <sch:p>
      MD_Metadata.hierarchyLevel = 'dataset' implies count (extent.geographicElement.EX_GeograpicBoundingBox) +
      count(extent.geographicElement.EX_GeographicDescription) >= 1
    </sch:p>
    <sch:rule context="//gmd:MD_Metadata | //*[@gco:isoType = 'gmd:MD_Metadata']">
      <sch:assert test="((not(gmd:hierarchyLevel) or gmd:hierarchyLevel/*/@codeListValue='dataset') 
                  and (count(gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox) + 
                  count(gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicDescription)) &gt;= 1) or
                  (gmd:hierarchyLevel/*/@codeListValue != 'dataset')">
        MD_DataIdentification: MD_Metadata.hierarchyLevel = 'dataset' implies count (extent.geographicElement.EX_GeographicBoundingBox) +
        count (extent.geographicElement.EX_GeographicDescription) >=1
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 5                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW5">
    <sch:title>ISO / TS 19139 Table A.1 Row 5</sch:title>
    <sch:p>
      MD_Metadata.hierarchyLevel notEqual 'dataset' implies topicCategory is not mandatory
    </sch:p>
    <sch:rule context="//gmd:MD_Metadata | //*[@gco:isoType = 'gmd:MD_Metadata']">
      <sch:assert test="(not(gmd:hierarchyLevel) or (gmd:hierarchyLevel/*/@codeListValue = 'dataset')) 
                  and (gmd:identificationInfo/*/gmd:topicCategory) or
                  gmd:hierarchyLevel/*/@codeListValue != 'dataset'">
        MD_DataIdentification: The topicCategory element is mandatory if hierarchyLevel is dataset.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 6                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW6">
    <sch:title>ISO / TS 19139 Table A.1 Row 6</sch:title>
    <sch:p>
      Either 'aggregateDataSetName' or 'aggregateDataSetIdentifier' must be documented
    </sch:p>
    <sch:rule context="//gmd:MD_AggregateInformation | //*[@gco:isoType = 'gmd:MD_AggregateInformation']">
      <sch:assert test="gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier">
        MD_AggregateInformation: Either 'aggregateDataSetName' or 'aggregateDataSetIdentifier' must be documented.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 7                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW7">
    <sch:title>ISO / TS 19139 Table A.1 Row 7</sch:title>
    <sch:p>
      otherConstraints: documented if accessConstraints = 'otherRestrictions'
    </sch:p>
    <sch:rule context="//gmd:MD_LegalConstraints | //*[@gco:isoType='gmd:MD_LegalConstraints']">
      <sch:assert test="(count(gmd:accessConstraints/*[@codeListValue = 'otherRestrictions']) &gt;= 1 and 
                  gmd:otherConstraints) or 
                  count(gmd:accessConstraints/*[@codeListValue = 'otherRestrictions']) = 0">
        MD_LegalConstraints: otherConstraints: documented if accessConstraints = 'otherRestrictions'.
      </sch:assert>
      <sch:assert test="(count(gmd:useConstraints/*[@codeListValue = 'otherRestrictions']) &gt;= 1 and 
                  gmd:otherConstraints) or
                  count(gmd:useConstraints/*[@codeListValue = 'otherRestrictions']) = 0">
        MD_LegalConstraints: otherConstraints: documented if useConstraints = 'otherRestrictions'
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="ISO19139A1_ROW7_InnerTextPattern">
    <sch:param name="context" value="//gmd:MD_LegalConstraints | //*[@gco:isoType='gmd:MD_LegalConstraints']"/>
    <sch:param name="element" value="gmd:otherConstraints"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 8                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW8">
    <sch:title>ISO / TS 19139 Table A.1 Row 8</sch:title>
    <sch:p>
      'report' or 'lineage' role is mandatory if scope.DQ_Scope.level = 'dataset'
    </sch:p>
    <sch:rule context="//gmd:DQ_DataQuality | //*[@gco:isoType = 'gmd:DQ_DataQuality']">
      <sch:assert test="(gmd:scope/*/gmd:level/*/@codeListValue = 'dataset') and ((count(gmd:report) + count(gmd:lineage)) > 0) or
                  (gmd:scope/*/gmd:level/*/@codeListValue != 'dataset')">
        DQ_DataQuality: 'report' or 'lineage' role is mandatory if scope.DQ_Scope.level = 'dataset'
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 9                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW9">
    <sch:title>ISO / TS 19139 Table A.1 Row 9</sch:title>
    <sch:p>
      'levelDescription' is mandatory if 'level' notEqual 'dataset' or 'series'
    </sch:p>
    <sch:rule context="//gmd:DQ_Scope | //*[@gco:isoType = 'gmd:DQ_Scope']">
      <sch:assert test="gmd:level/*/@codeListValue = 'dataset' or gmd:level/*/@codeListValue = 'series' or gmd:levelDescription">
        DQ_Scope: 'levelDescription' is mandatory if 'level' notEqual 'dataset' or 'series'.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 10                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW10">
    <sch:title>ISO / TS 19139 Table A.1 Row 10</sch:title>
    <sch:p>
      If (count(source) + count(processStep) = 0) and (DQ_DataQuality.scope.level = 'dataset'
      or 'series') then statement is mandatory
    </sch:p>
    <sch:rule context="//gmd:LI_Lineage | //*[@gco:isoType = 'gmd:LI_Lineage']">
      <sch:assert test="((count(gmd:source) + count(gmd:processStep) = 0) and
                  (../../gmd:scope/*/gmd:level/*/@codeListValue = 'dataset' or ../../gmd:scope/*/gmd:level/*/@codeListValue = 'series') and
                  count(gmd:statement) = 1) or 
                  (../../gmd:scope/*/gmd:level/*/@codeListValue != 'dataset' or ../../gmd:scope/*/gmd:level/*/@codeListValue != 'series')">
        LI_Lineage: If (count(source) + count(processStep) = 0) and (DQ_DataQuality.scope.level = 'dataset'
        or 'series') then statement is mandatory. <sch:value-of select="count(gmd:statement)"/>
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 11 and Row 12                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW11">
    <sch:title>ISO / TS 19139 Table A.1 Rows 11 and 12</sch:title>
    <sch:p>
      Row 11 - 'source' role is mandatory if LI_Lineage.statement and 'processStep' role are not documented
    </sch:p>
    <sch:p>
      Row 12 - 'processStep' role is mandatory if LI_Lineage.statement and 'source' role are not documented
    </sch:p>
    <sch:rule context="//gmd:LI_Lineage | //*[@gco:isoType = 'gmd:LI_Lineage']">
      <sch:assert test="(not(gmd:statement) and not(gmd:processStep) and gmd:source) or 
                  (not(gmd:statement) and not(gmd:source) and gmd:processStep) or
                  gmd:statement">
        LI_Lineage: 'source' role is mandatory if LI_Lineage.statement and 'processStep' role are not documented.
        LI_Lineage: 'processStep' role is mandatory if LI_Lineage.statement and 'source' role are not documented.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 13                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW13">
    <sch:title>ISO / TS 19139 Table A.1 Row 13</sch:title>
    <sch:p>
      'description' is mandatory if 'sourceExtent' is not documented
    </sch:p>
    <sch:rule context="//gmd:LI_Source | //*[@gco:isoType = 'gmd:LI_Source']">
      <sch:assert test="gmd:sourceExtent or gmd:description">
        LI_Source: 'description' is mandatory if 'sourceExtent' is not documented.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 14                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW14">
    <sch:title>ISO / TS 19139 Table A.1 Row 14</sch:title>
    <sch:p>
      'sourceExtent' is mandatory if 'description' is not documented
    </sch:p>
    <sch:rule context="//gmd:LI_Source | //*[@gco:isoType = 'gmd:LI_Source']">
      <sch:assert test="gmd:sourceExtent or gmd:description">
        LI_Source: 'sourceExtent' is mandatory if 'description' is not documented.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 15                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW15">
    <sch:title>ISO / TS 19139 Table A.1 Row 15</sch:title>
    <sch:p>
      'checkPointDescription' is mandatory if 'checkPointAvailability' = 1
    </sch:p>
    <sch:rule context="//gmd:MD_Georectified | //*[@gco:isoType = 'gmd:MD_Georectified']">
      <sch:assert test="(gmd:checkPointAvailability/gco:Boolean = '1' or 
                  gmd:checkPointAvailability/gco:Boolean = 'true') and
                  gmd:checkPointDescription">
        MD_Georectified: 'checkPointDescription' is mandatory if 'checkPointAvailability' = 1
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 16                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW16">
    <sch:title>ISO / TS 19139 Table A.1 Row 16</sch:title>
    <sch:p>
      'units' is mandatory if 'maxValue' or 'minValue' are provided
    </sch:p>
    <sch:rule context="//gmd:MD_Band | //*[@gco:isoType = 'gmd:MD_Band']">
      <sch:assert test="((gmd:maxValue or gmd:minValue) and gmd:units) or 
                  (not(gmd:maxValue) and not(gmd:minValue) and not(gmd:units))">
        MD_Band: 'units' is mandatory if 'maxValue' or 'minValue' are provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 17                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW17">
    <sch:title>ISO / TS 19139 Table A.1 Row 17</sch:title>
    <sch:p>
      'densityUnits' is mandatory if 'density' is provided
    </sch:p>
    <sch:rule context="//gmd:MD_Medium | //*[@gco:isoType = 'gmd:MD_Medium']">
      <sch:assert test="(gmd:density and gmd:densityUnits) or (not(gmd:density) and not(gmd:densityUnits))">
        MD_Medium: 'densityUnits' is mandatory if 'density' is provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 18                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW18">
    <sch:title>ISO / TS 19139 Table A.1 Row 18</sch:title>
    <sch:p>
      count(distributionFormat + distributorFormat) > 0
    </sch:p>
    <sch:rule context="//gmd:MD_Distribution | //*[@gco:isoType = 'gmd:MD_Distribution']">
      <sch:assert test="count(gmd:distributionFormat) &gt; 0 or 
                  count(gmd:distributor/*/gmd:distributorFormat) &gt; 0">
        MD_Distribution / MD_Format: count(distributionFormat + distributorFormat) > 0.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 19                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW19">
    <sch:title>ISO / TS 19139 Table A.1 Row 19</sch:title>
    <sch:p>
      if 'dataType' notEqual 'codelist', 'enumeration' or 'codeListElement' then 'obligation',
      'maximumOccurrence' and 'domainValue' are mandatory
    </sch:p>
    <sch:rule context="//gmd:MD_ExtendedElementInformation | //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']">
      <sch:assert test="(gmd:dataType/*/@codeListValue = 'codelist' or 
                  gmd:dataType/*/@codeListValue = 'enumeration' or 
                  gmd:dataType/*/@codeListValue = 'codelistElement') or
                  gmd:obligation">
        MD_ExtendedElementInformation: if 'dataType' notEqual 'codelist', 
        'enumeration' or 'codelistElement' then 'obligation' is mandatory.
      </sch:assert>
      <sch:assert test="(gmd:dataType/*/@codeListValue = 'codelist' or 
                  gmd:dataType/*/@codeListValue = 'enumeration' or 
                  gmd:dataType/*/@codeListValue = 'codelistElement') or
                  gmd:maximumOccurrence">
        MD_ExtendedElementInformation: if 'dataType' notEqual 'codelist', 
        'enumeration' or 'codelistElement' then 'maximumOccurence' is mandatory.
      </sch:assert>
      <sch:assert test="(gmd:dataType/*/@codeListValue = 'codelist' or 
                  gmd:dataType/*/@codeListValue = 'enumeration' or 
                  gmd:dataType/*/@codeListValue = 'codelistElement') or
                  gmd:domainValue">
        MD_ExtendedElementInformation: if 'dataType' notEqual 'codelist', 
        'enumeration' or 'codelistElement' then 'domainValue' is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="ISO19139A1_ROW19_InnerTextPattern_Obligation">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation | //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']"/>
    <sch:param name="element" value="gmd:obligation"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="ISO19139A1_ROW19_GcoTypeTestPattern_MaximumOccurrence">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation/gmd:maximumOccurrence | 
               //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']/gmd:maximumOccurrence"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="ISO19139A1_ROW19_GcoTypeTestPattern_DomainValue">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation/gmd:domainValue | 
               //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']/gmd:domainValue"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 20                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW20">
    <sch:title>ISO / TS 19139 Table A.1 Row 20</sch:title>
    <sch:p>
      if 'obligation' = 'conditional' then 'condition' is mandatory
    </sch:p>
    <sch:rule context="//gmd:MD_ExtendedElementInformation | //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']">
      <sch:assert test="((gmd:obligation/*/@codeListValue = 'conditional') and gmd:condition) or
                  gmd:obligation/*/@codeListValue != 'conditional' or not(gmd:obligation)">
        MD_ExtendedElementInformation: if 'obligation' = 'conditional' then 'condition' is mandatory
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="ISO19139A1_ROW20_GcoTypeTestPattern">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation/gmd:condition | 
               //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']/gmd:condition"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 21                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW21">
    <sch:title>ISO / TS 19139 Table A.1 Row 21</sch:title>
    <sch:p>
      if 'dataType' = 'codeListElement' then 'domainCode' is mandatory
    </sch:p>
    <sch:rule context="//gmd:MD_ExtendedElementInformation | //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']">
      <sch:assert test="((gmd:dataType/*/@codeListValue = 'codelistElement') and gmd:domainCode) or
                  gmd:dataType/*/@codeListValue != 'codelistElement'">
        MD_ExtendedElementInformation: if 'dataType' = 'codeListElement' then 'domainCode' is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="ISO19139A1_ROW21_GcoTypeTestPattern">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation/gmd:domainCode | 
               //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']/gmd:domainCode"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 22                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW22">
    <sch:title>ISO / TS 19139 Table A.1 Row 22</sch:title>
    <sch:p>
      if 'dataType' notEqual 'codeListElement' then 'shortName' is mandatory
    </sch:p>
    <sch:rule context="//gmd:MD_ExtendedElementInformation | //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']">
      <sch:assert test="((gmd:dataType/*/@codeListValue != 'codelistElement') and gmd:shortName) or
                  gmd:dataType/*/@codeListValue = 'codelistElement'">
        MD_ExtendedElementInformation: if 'dataType' notEqual 'codeListElement' then 'shortName' is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="ISO19139A1_ROW22_GcoTypeTestPattern">
    <sch:param name="context" value="//gmd:MD_ExtendedElementInformation/gmd:shortName | 
               //*[@gco:isoType = 'gmd:MD_ExtendedElementInformation']/gmd:shortName"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 23                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW23">
    <sch:title>ISO / TS 19139 Table A.1 Row 23</sch:title>
    <sch:p>
      count(description + geographicElement + temporalElement + verticalElement) > 0
    </sch:p>
    <sch:rule context="//gmd:EX_Extent | //*[@gco:isoType = 'gmd:EX_Extent']">
      <sch:assert test="count(gmd:description) + count(gmd:geographicElement) + 
                  count(gmd:temporalElement) + count(gmd:verticalElement) > 0">
        EX_Extent: count(description + geographicElement + temporalExtent + verticalElement) > 0
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 24                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW24">
    <sch:title>ISO / TS 19139 Table A.1 Row 24</sch:title>
    <sch:p>
      count(individualName + organisationName + positionName) > 0
    </sch:p>
    <sch:rule context="//gmd:CI_ResponsibleParty | //*[@gco:isoType = 'gmd:CI_ResponsibleParty']">
      <sch:assert test="count(gmd:individualName) + count(gmd:organisationName) + count(gmd:positionName) > 0">
        count(individualName + organisationName + positionName) > 0
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 25                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW25">
    <sch:title>ISO / TS 19139 Table A.1 Row 25</sch:title>
    <sch:p>
      Distance: the UoM element of the Distance Type must be instantiated using the UomLength_PropertyType
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoUomTestPattern" id="ISO19139A1_ROW25_GcoUomTestPattern">
    <sch:param name="context" value="//gco:Distance"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 26                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW26">
    <sch:title>ISO / TS 19139 Table A.1 Row 26</sch:title>
    <sch:p>
      Length: The UoM element of the Length Type must be instantiated using the UomLength_PropertyType
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoUomTestPattern" id="ISO19139A1_ROW26_GcoUomTestPattern">
    <sch:param name="context" value="//gco:Length"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 27                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW27">
    <sch:title>ISO / TS 19139 Table A.1 Row 27</sch:title>
    <sch:p>
      Scale: The UoM element of the Scale Type must be instantiated using the UomScale_PropertyType
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoUomTestPattern" id="ISO19139A1_ROW27_GcoUomTestPattern">
    <sch:param name="context" value="//gco:Scale"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- ISO / TS 19139 Table A.1 Row 28                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="ISO19139A1_ROW28">
    <sch:title>ISO / TS 19139 Table A.1 Row 28</sch:title>
    <sch:p>
      Angle: The UoM element of the Angle Type must be instantiated using the UomAngle_PropertyType
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoUomTestPattern" id="ISO19139A1_ROW28_GcoUomTestPattern">
    <sch:param name="context" value="//gco:Angle"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Test that all elements have child elements or are gco elements or have a nil reason        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="TestValues">
    <sch:title>Element Values or Nil Reason Attributes</sch:title>
    <sch:rule context="//*">
      <sch:assert test="count(*) &gt; 0 or 
                  namespace-uri() = 'http://www.isotc211.org/2005/gco' or
                  namespace-uri() = 'http://www.isotc211.org/2005/gmx' or
                  namespace-uri() = 'http://www.opengis.net/gml/3.2' or
                  namespace-uri() = 'http://www.opengis.net/gml' or
                  @codeList or
                  @codeListValue or
                  local-name() = 'MD_TopicCategoryCode' or
                  local-name() = 'URL' or
                  (@gco:nilReason = 'inapplicable' or
                  @gco:nilReason = 'missing' or 
                  @gco:nilReason = 'template' or
                  @gco:nilReason = 'unknown' or
                  @gco:nilReason = 'withheld') or 
                  @xlink:href">
        The '<sch:name/>' element has no child elements.
      </sch:assert>
      <sch:assert test="(namespace-uri() = 'http://www.isotc211.org/2005/gco' and string-length() &gt; 0) or
                  namespace-uri() != 'http://www.isotc211.org/2005/gco'">
        The '<sch:value-of select="name(../..)"/>/<sch:value-of select="name(..)"/>/<sch:name/>' gco element has no value.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Abstract Patterns                                                                          -->
  <!-- ========================================================================================== -->

  <!-- Test for GCO types -->
  <sch:pattern abstract="true" id="GcoTypeTestPattern">
    <sch:rule context="$context">
      <sch:assert test="(string-length(.) &gt; 0) or 
                  (@gco:nilReason = 'inapplicable' or
                  @gco:nilReason = 'missing' or 
                  @gco:nilReason = 'template' or
                  @gco:nilReason = 'unknown' or
                  @gco:nilReason = 'withheld')">
        The <sch:name/> element must have a value or a Nil Reason.
      </sch:assert>
    </sch:rule>
  </sch:pattern>
  
  <!-- Test that a gco element has a value or has a valid nilReason value -->
  <sch:pattern abstract="true" id="GcoUomTestPattern">
    <sch:rule context="$context">
      <!-- Test for uom on Distance, Length, Scale, Angle -->
      <sch:assert test="count(./@uom) = 1">
        The '<sch:value-of select="name(../..)"/>/<sch:value-of select="name(..)"/>/<sch:name/>' element must have a uom attribute.
      </sch:assert>
    </sch:rule>
  </sch:pattern>  
  
  <!-- Test that an element has a value and is not empty string -->
  <sch:pattern abstract="true" id="InnerTextPattern">
    <sch:rule context="$context">
      <sch:assert test="(count($element) = 0) or 
                  (string-length(normalize-space($element)) &gt; 0) or
                  ($element/@gco:nilReason = 'inapplicable' or
                  $element/@gco:nilReason = 'missing' or 
                  $element/@gco:nilReason = 'template' or
                  $element/@gco:nilReason = 'unknown' or
                  $element/@gco:nilReason = 'withheld')">
        The '<sch:value-of select="name($element)"/>' element should have a value.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test for the responsible party information -->
  <sch:pattern abstract="true" id="ResponsiblePartyPattern">
    <!-- Count of Organisation Name and Individual Name >= 1 -->
    <sch:rule context="$context">
      <sch:assert test="count(*/gmd:organisationName) + count(*/gmd:individualName) &gt;= 1">
        At least organisation name or individual name must be provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="$context/*/gmd:contactInfo/*/gmd:address/*">
      <sch:assert test="$countTest">
        One or more email addresses must be supplied.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>