<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" schemaVersion="ISO19757-3" queryBinding="xslt2">
  <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <sch:ns prefix="gts" uri="http://www.isotc211.org/2005/gts"/>
  <sch:ns prefix="gmi" uri="http://www.isotc211.org/2005/gmi"/>
  <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>
  <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <!--
    ISO 19115 and 19115-2 Style Suggestions
    
    This schematron checks several recommended practices for of ISO Metadata.
    Following these practices is not essential, but it improves the metadata.
    
    Created by ted.habermann@noaa.gov 20120526
  -->
  <sch:pattern>
    <!-- The standard form for codeLists includes the value as an attribute and as content in the element -->
    <sch:title>Check the form of CodeLists</sch:title>
    <sch:rule context="//*[ends-with(name(./*[1]),'Code') and count(*)=1 and not(name(.)='gmd:topicCategory')]">
      <sch:assert test="normalize-space(./*[1]) = ./*[1]/@codeListValue">ME: The codeListValue attribute must match the content of the codeList element</sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern>
    <!--
      The uuid and uuidref attributes are expected to be valid Universally Unique Identifiers. These consist of
      32 characters optionally separated into groups of 8-4-4-4-12 characters by dashes.
    -->
    <sch:title>Check the form of uuid attributes</sch:title>
    <sch:rule context="//@uuid">
      <sch:assert test="matches(.,'^[\d|\w]{8}-[\d|\w]{4}-[\d|\w]{4}-[\d|\w]{4}-[\d|\w]{12}$') or matches(.,'^[\d|\w]{32}$')">uuid attributes must be valid uuids</sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern>
    <!--
       The uuid and uuidref attributes are expected to be valid Universally Unique Identifiers. These consist of
       32 characters optionally separated into groups of 8-4-4-4-12 characters by dashes.
     -->
    <sch:title>Check the form of uuidref attributes</sch:title>
    <sch:rule context="//@uuidref">
      <sch:assert test="matches(.,'^[\d|\w]{8}-[\d|\w]{4}-[\d|\w]{4}-[\d|\w]{4}-[\d|\w]{12}$') or matches(.,'^[\d|\w]{32}$')">uuidref attributes must be valid uuids</sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern>
    <!--
      onlineResources are a critical part of the interface between metadata and users. The ISO standard requires only
      the linkage element but the name, description, and function are important for improving usability of the metadata.
    -->
    <sch:title>Check onlineResources</sch:title>
    <sch:rule context="//gmd:CI_OnlineResource">
      <sch:assert test="gmd:name">onlineResources should have a name</sch:assert>
      <sch:assert test="gmd:description">onlineResources should have a description</sch:assert>
      <sch:assert test="gmd:function">onlineResources should have a function</sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- check the validity of a URL in gmx:Anchor tag -->
  <sch:pattern>
    <sch:title>Check xlink in gmx:Anchor</sch:title>
    <sch:rule context="//gmx:Anchor">
      <sch:let name="xlinkVoc" value="document(./attribute::xlink:href)"/>
      <sch:assert test="$xlinkVoc">
        <sch:value-of select="./attribute::xlink:href"/> is not a valid URL. </sch:assert>
    </sch:rule>
  </sch:pattern>
  <!-- Best Practices for @id in extent objects. Note: when there are repeating gmd:extents - this assertion incorrectly expects for each //xpath below to contain these id attributes.-->
  <!--  <pattern>
    <title>gmd:MD_DataIdentification/gmd:extent</title>
    <rule context="//gmd:MD_DataIdentification/gmd:extent">
    <assert test="gmd:EX_Extent/@id='boundingExtent'">One of the gmd:EX_Extent elements should have an attribute id = 'boundingExtent'.</assert>
    </rule>
    </pattern>
    <pattern>
    <title>gmd:MD_DataIdentification/gmd:extent</title>
    <rule context="//gmd:MD_DataIdentification/gmd:extent">
    <assert test="gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/@id='boundingGeographicBoundingBox'">One of the gmd:EX_GeographicBoundingBox elements should have an attribute id = 'boundingGeographicBoundingBox'.</assert>
    </rule>
    </pattern>
    <pattern>
    <title>gmd:MD_DataIdentification/gmd:extent</title>
    <rule context="//gmd:MD_DataIdentification/gmd:extent">
    <assert test="gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/@id='boundingTemporalExtent'">One of the gmd:EX_TemporalExtent elements should have an attribute id = 'boundingTemporalExtent'.</assert>
    </rule>
    </pattern>-->
</sch:schema>
