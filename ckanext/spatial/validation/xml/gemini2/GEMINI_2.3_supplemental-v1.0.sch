<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt" schemaVersion="1.2">
    <sch:title>UK GEMINI Standard Draft Version 2.3 (supplemental)</sch:title>
    <!-- Namespaces from ISO 19139 Metadata encoding -->
    <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
    <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
    <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
    <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>
    <!-- Namespace for ISO 19119 - Metadata Describing Services -->
    <sch:ns prefix="srv" uri="http://www.isotc211.org/2005/srv"/>
    <!-- Namespace for ISO 19136 - Geography Mark-up Language -->
    <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2"/>
    <!-- Namespace for CSW responses -->
    <sch:ns prefix="csw" uri="http://www.opengis.net/cat/csw/2.0.2"/>
    <!-- Namespace other -->
    <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
    <sch:ns uri="http://www.isotc211.org/2005/gss" prefix="gss"/>
    <sch:ns uri="http://www.isotc211.org/2005/gts" prefix="gts"/>
    <sch:ns uri="http://www.isotc211.org/2005/gsr" prefix="gsr"/>
    <sch:p>This Schematron schema is designed to show metadata recommendations for the GEMINI2 discovery metadata standard.</sch:p>
    <!-- External document(s) -->
    <sch:let name="defaultCRScodes" value="document('https://agi.org.uk/images/xslt/d4.xml')" />
    <!-- IR titles -->
    <sch:let name="inspire1089" value="'Commission Regulation (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services'"/>
    <sch:let name="inspire1089x" value="'COMMISSION REGULATION (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services'"/>
    <!-- ========================================================================================== -->
    <sch:pattern fpi="metadata/2.0/rec/datasets-and-series/resource-locator-additional-info">
        <sch:title>Resource Locator ~ additional information</sch:title>
        <sch:p>Provide recommendation about providing additional information for transfer options
            for online linkages applies to all metadata types.</sch:p>
        <!-- The gmd:name, gmd:description, and gmd:function/gmd:CI_OnLineFunctionCode child elements of gmd:CI_OnlineResource element containing the given gmd:linkage element should also be provided -->
        <sch:rule
            context="//gmd:MD_Metadata[1]/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource">
            <sch:assert test="gmd:name">SP-1a: If possible a gmd:name should be supplied to provide more
                information about the URL link </sch:assert>
            <sch:assert test="gmd:description">SP-1b: If possible a gmd:description should be supplied to
                provide more information about the URL link </sch:assert>
            <sch:assert test="gmd:function">SP-1c: If possible a gmd:function should be supplied to
                provide more information about the URL link </sch:assert>
        </sch:rule>
    </sch:pattern>
    <!-- fpi="metadata/2.0/req/isdss/topological-consistency-descriptive-results-warn" has been removed. This was SP-2 -->
    <sch:pattern fpi="Gemini2-mi3-rec">
        <sch:title>Dataset language (recommendation)</sch:title>
        <sch:p>TG rec 1.7 ~ Specifies use of language name over code</sch:p>
        <sch:rule
            context="//gmd:MD_Metadata[1]/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:language/gmd:LanguageCode">
            <sch:report test="@codeListValue = current()">SP-3: You have the same text value as the
                codeListValue, recommendation is to have the name of the language as the human
                readable text </sch:report>
        </sch:rule>
    </sch:pattern>
    <sch:pattern fpi="Gemini2-mi17-refSysInfo-recs">
        <sch:title>Coordinate Reference System (warning)</sch:title>
        <sch:p>Checking whether coordinate reference system is a default CRS</sch:p>
        <sch:rule
            context="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/gmd:RS_Identifier[1]/gmd:code/gmx:Anchor[1]/@xlink:href">
            <sch:assert
                test="$defaultCRScodes//crs/text()[normalize-space(.) = normalize-space(current()/.)]"
                >SP-4a: Coordinate Reference System: <sch:value-of
                    select="normalize-space(current()/.)"/> is not a default CRS </sch:assert>
        </sch:rule>
        <sch:rule
            context="//gmd:MD_Metadata[1]/gmd:referenceSystemInfo/*[1]/gmd:referenceSystemIdentifier/gmd:RS_Identifier[1]/gmd:code/gco:CharacterString">
            <sch:assert
                test="$defaultCRScodes//crs/text()[normalize-space(.) = normalize-space(current()/.)]"
                >SP-4b: Coordinate Reference System: <sch:value-of
                    select="normalize-space(current()/.)"/> is not a default CRS </sch:assert>
        </sch:rule>
    </sch:pattern>
    <sch:pattern fpi="Gemini2-mi41-inspire1089x-WARN">
        <sch:title>1089/2010 Case (warning)</sch:title>
        <sch:p>This test checks for the title starting with `COMMISSION REGULATION` as ss. it should be 'Commission Regulation'...</sch:p>
        <sch:rule context="//gmd:MD_Metadata[1]/gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd:specification/gmd:CI_Citation/gmd:title/*[1][text() = 'COMMISSION REGULATION (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services']">
            <sch:report test=".">SP-5:
                To be fully compliant with the regulation the title should be <sch:value-of select="$inspire1089"/>. 
            </sch:report>
        </sch:rule>
    </sch:pattern>
</sch:schema>
