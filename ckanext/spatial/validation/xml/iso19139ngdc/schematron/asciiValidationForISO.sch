<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:iso="http://purl.oclc.org/dsdl/schematron" schemaVersion="ISO19757-3" queryBinding="xslt2">
  <ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
  <ns prefix="gts" uri="http://www.isotc211.org/2005/gts"/>
  <ns prefix="gmi" uri="http://www.isotc211.org/2005/gmi"/>
  <ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>
  <ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <!-- Purpose: to test for common non-ascii characters in ISO 19139 XML. -->  
  <!-- Update: June 22, 2010 Include report for non-html friendly characters, supplied by Kate.Wringe@sybase.com  -->
  <!-- Nov 28, 2011 Anna Milan. Udated gml namespace to 3.2. Added gmx, gml to rule context  -->
  <!-- To do: make test generic to test for ANY non-ascii character. -->
  <pattern>
    <title>Report weird characters</title>
    <rule context="gco:*|gmx:*|gml:*|gmd:LocalisedCharacterString">
      <report test="contains(.,'“')">[1]Replace the “ smart quotes.</report>
      <report test="contains(.,'”')">[1]Replace the ” smart quotes.</report>
      <report test="contains(.,'‘')">[1]Replace the ‘ smart quote.</report>
      <report test="contains(.,'’')">[1]Replace the ’ smart quote.</report>
      <report test="contains(.,'–')">[1]Replace the – dash.</report>
      <report test="contains(.,'—')">[1]Replace the — em dash entity.</report>
      <report test="contains(.,'®')">[1]Replace the ® registred trademark symbol.</report>
      <report test="contains(.,'°')">[1]Replace the ° degree symbol.</report>
      <report test="contains(.,'©')">[1]Replace the © symbol.</report>     
    </rule>
  </pattern>
</schema>
