<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:geonet="http://www.fao.org/geonetwork" xmlns:iso="http://purl.oclc.org/dsdl/schematron" schemaVersion="ISO19757-3" queryBinding="xslt2">
  <ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <ns prefix="gts" uri="http://www.isotc211.org/2005/gts"/>
  <ns prefix="gmi" uri="http://www.isotc211.org/2005/gmi"/>
  <ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>
  <ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <!--  ISO 19115 and 19115-2 rules that are not checked by 19139 schema validation -->
  <!-- 
		This schematron was translated from a schematron xsl provided by Geonetwork Opensource
		* add test for gmi namespace
		* edit assert statements to (hopefully) be more meaningful
		* enforce content for @id in extent objects (best practice)
	-->
  <!-- Editor: Anna.Milan@noaa.gov-->
  <!-- Date: April 30, 2010 -->
  <!-- Update: May 14, 2010 -->
  <!-- Update: June 22, 2010 include report for non-html friendly characters, supplied by Kate.Wringe@sybase.com -->
  <!-- Update Sept 30, 2011:  moved codelist test and weird character's test out of this schematron. See codeListValidation.sch, asciiValidationForISO.sch, and asciiValidationForFGDC.sch.-->
  <!-- Update Nov 28, 2011: changed gml namespace declaration to 3.2 -->
  <pattern>
    <title>gmd elements</title>
    <rule context="gmd:*|gmi:*">
      <assert test="./gco:CharacterString | ./@gco:nilReason | ./@xlink:href | @uuidref | ./@codeListValue | ./child::node()">Element must have content or one of the following attributes: nilReason, xlink:href or uuidref. </assert>
      <assert test="contains('missing inapplicable template unknown withheld', ./@gco:nilReason)">'<value-of select="./@gco:nilReason"/>' is not an accepted value. gco:nilReason attribute may only contain: missing, inapplicable, template, unknown, or withheld for element: <name path="."/>
      </assert>
    </rule>
  </pattern>
  <pattern>
    <title>gml elements</title>
    <rule context="gml:*">
      <assert test="./@indeterminatePosition | ./child::node()">The <name path="."/> Element must have content or, if allowed, an indeterminatePosition attribute.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>//gml:DirectPositionType</title>
    <rule context="//gml:DirectPositionType">
      <report test="not(@srsDimension) or @srsName">The presence of a dimension attribute implies the presence of the srsName attribute.</report>
      <report test="not(@axisLabels) or @srsName">The presence of an axisLabels attribute implies the presence of the srsName attribute.</report>
      <report test="not(@uomLabels) or @srsName">The presence of an uomLabels attribute implies the presence of the srsName attribute.</report>
      <report test="(not(@uomLabels) and not(@axisLabels)) or (@uomLabels and @axisLabels)">The presence of an uomLabels attribute implies the presence of the axisLabels attribute and vice versa.</report>
    </rule>
  </pattern>
  <pattern>
    <title>CI_ResponsibleParty</title>
    <rule context="//gmd:CI_ResponsibleParty">
      <assert test="(count(gmd:individualName) + count(gmd:organisationName) + count(gmd:positionName)) &gt; 0">You must specify one or more of gmd:individualName, gmd:organisationName or gmd:positionName.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>other restrictions in MD_LegalConstraints</title>
    <rule context="//gmd:MD_LegalConstraints">
      <report test="gmd:accessConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">If gmd:accessConstraints has a gmd:MD_RestrictionCode with a value of 'otherRestrictions' then gmd: otherConstraints must be documented.</report>
      <report test="gmd:useConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">If gmd:useConstraints has a gmd:MD_RestrictionCode with a value of 'otherRestrictions' then gmd: otherConstraints must be documented.</report>
    </rule>
  </pattern>
  <pattern>
    <title>MD_Band Units</title>
    <rule context="//gmd:MD_Band">
      <report test="(gmd:maxValue or gmd:minValue) and not(gmd:units)">gmd:units is mandatory if gmd:maxValue or gmd:minValue are provided.</report>
    </rule>
  </pattern>
  <pattern>
    <title>Source description or Source Extent</title>
    <rule context="//gmd:LI_Source | //gmi:LE_Source">
      <assert test="gmd:description or gmd:sourceExtent">If gmd:SourcExtent is not documented then gmd:description is mandatory.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>Lineage/source and Lineage/processStep</title>
    <rule context="//gmd:DQ_DataQuality">
      <report test="(((count(*/gmd:LI_Lineage/gmd:source) + count(*/gmd:LI_Lineage/gmd:processStep)) = 0) and (gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='series')) and not(gmd:lineage/gmd:LI_Lineage/gmd:statement) and (gmd:lineage)">If gmd:source and gmd:processStep do not exist and gmd:DQ_Dataquality/gmd:scope/gmd:level = 'dataset' or 'series' then gmd:statement is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>Lineage/source, statement and processStep</title>
    <rule context="//gmd:LI_Lineage">
      <report test="not(gmd:source) and not(gmd:statement) and not(gmd:processStep)">If gmd:statement and gmd:processStep are not documented under LI_LIneage then gmd:source is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>LI_Lineage/processStep, statement and source</title>
    <rule context="//gmd:LI_Lineage">
      <report test="not(gmd:processStep) and not(gmd:statement) and not(gmd:source)">If gmd:statement and gmd:source are not documented under LI_LIneage then gmd:processStep is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>DQ_DataQuality/DQ_Scope</title>
    <rule context="//gmd:DQ_DataQuality">
      <report test="gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' and not(gmd:report) and not(gmd:lineage)">If gmd:level/gmd:MD_ScopeCode is = 'dataset' then gmd:report or gmd:lineage is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>DQ_Scope</title>
    <rule context="//gmd:DQ_Scope">
      <assert test="gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:level/gmd:MD_ScopeCode/@codeListValue='series' or (gmd:levelDescription and ((normalize-space(gmd:levelDescription) != '') or (gmd:levelDescription/gmd:MD_ScopeDescription)))">If gmd:MD_ScopeCode is not equal to 'dataset' or 'series' then gmd:levelDescription is mandatory. </assert>
    </rule>
  </pattern>
  <pattern>
    <title>MD_Medium</title>
    <rule context="//gmd:MD_Medium">
      <report test="gmd:density and not(gmd:densityUnits)">If gmd:density is provided then gmd:densityUnits is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>gmd:MD_Distribution</title>
    <rule context="//gmd:MD_Distribution">
      <assert test="count(gmd:distributionFormat)&gt;0 or count(gmd:distributor/gmd:MD_Distributor/gmd:distributorFormat)&gt;0">You must provide either gmd:distributionFormat or gmd:distributorFormat.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>gmd:EX_Extent</title>
    <rule context="//gmd:EX_Extent">
      <assert test="count(gmd:description)&gt;0 or count(gmd:geographicElement)&gt;0 or count(gmd:temporalElement)&gt;0 or count(gmd:verticalElement)&gt;0">You must document at least one of the following under gmd:EX_Extent: gmd:description, gmd:geographicElement, or gmd:temporalElement.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>gmd:MD_DataIdentification Extent</title>
    <rule context="//gmd:MD_DataIdentification">
      <report test="(not(gmd:hierarchyLevel) or gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') and (count(//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox) + count (//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicDescription)) =0">If the metadata gmd:hierarchyLevel code = 'dataset' then you must document gmd:EX_GeographicBoundingBox or gmd:EX_GeographicDescription.</report>
    </rule>
  </pattern>
  <pattern>
    <title>//gmd:MD_DataIdentification</title>
    <rule context="//gmd:MD_DataIdentification">
      <report test="(not(../../gmd:hierarchyLevel) or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='series')) and (not(gmd:topicCategory))">If the metadata gmd:hierarchyLevel code = 'dataset' or 'series' then gmd:topicCategory is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>gmd:MD_AggregateInformation</title>
    <rule context="//gmd:MD_AggregateInformation">
      <assert test="gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier">Either gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier must be documented.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>gmd:language</title>
    <rule context="//gmd:MD_Metadata|//gmi:MI_Metadata">
      <report test="not(gmd:language) or (gmd:language/@gco:nilReason)">gmd:language is required if it is not defined by encoding.</report>
    </rule>
  </pattern>
  <pattern>
    <title>//gmd:MD_ExtendedElementInformation</title>
    <rule context="//gmd:MD_ExtendedElementInformation">
      <assert test="(gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelist' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='enumeration' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement') or (gmd:obligation or (gmd:obligation/gmd:MD_ObligationCode) or (gmd:obligation/@gco:nilReason))">If gmd:dataType notEqual 'codelist', 'enumeration' or 'codelistElement' then gmd:obligation is mandatory.</assert>
    </rule>
  </pattern>
  <pattern>
    <title>MD_ExtendedElementInformation</title>
    <rule context="//gmd:MD_ExtendedElementInformation">
      <report test="gmd:obligation/gmd:MD_ObligationCode='conditional' and not(gmd:condition)">If gmd:obligation = 'conditional' then gmd:condition is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>MD_ExtendedElementInformation</title>
    <rule context="//gmd:MD_ExtendedElementInformation">
      <report test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement' and not(gmd:domainCode)">If gmd:dataType = 'codelistElement' then gmd:domainCode is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>MD_ExtendedElementInformation</title>
    <rule context="//gmd:MD_ExtendedElementInformation">
      <report test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue!='codelistElement' and not(gmd:shortName)">If gmd:dataType is not equal to 'codelistElement' then gmd:shortName is mandatory.</report>
    </rule>
  </pattern>
  <pattern>
    <title>MD_Georectified</title>
    <rule context="//gmd:MD_Georectified">
      <report test="(gmd:checkPointAvailability/gco:Boolean='1' or gmd:checkPointAvailability/gco:Boolean='true') and not(gmd:checkPointDescription)">If gmd:checkPointAvailability = '1' or 'true' then gmd:checkPointDescription is mandatory.</report>
    </rule>
  </pattern>  
</schema>
