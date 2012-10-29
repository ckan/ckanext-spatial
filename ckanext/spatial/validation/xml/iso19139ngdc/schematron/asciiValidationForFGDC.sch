<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:geonet="http://www.fao.org/geonetwork" xmlns:iso="http://purl.oclc.org/dsdl/schematron" schemaVersion="ISO19757-3" queryBinding="xslt2">
  <!-- Purpose: to test for common non-ascii characters in FGDC XML. -->
  <!-- Update: June 22, 2010 Include report for non-html friendly characters, supplied by Kate.Wringe@sybase.com  -->
  <!-- To do: make test generic to test for ANY non-ascii character. Note: Due to simple FGDC XML design this outputs validation messages for every parent node of the tag with the non-ascii content.-->
  <pattern>
    <title>Report weird characters</title>
    <rule context="*">
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
