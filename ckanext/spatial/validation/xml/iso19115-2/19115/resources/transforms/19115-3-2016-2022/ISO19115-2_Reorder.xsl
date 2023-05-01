<xsl:stylesheet version="2.0"
    xmlns:mdb="https://schemas.isotc211.org/19115/-1/mdb/1.3"
    xmlns:xsi="https://www.w3.org/2001/XMLSchema-instance"
    xmlns:cit="https://schemas.isotc211.org/19115/-1/cit/1.3"
    xmlns:gex="https://schemas.isotc211.org/19115/-1/gex/1.3"
    xmlns:lan="https://schemas.isotc211.org/19115/-1/lan/1.3"
    xmlns:mas="https://schemas.isotc211.org/19115/-1/mas/1.3"
    xmlns:mcc="https://schemas.isotc211.org/19115/-1/mcc/1.3"
    xmlns:mco="https://schemas.isotc211.org/19115/-1/mco/1.3"
    xmlns:mda="https://schemas.isotc211.org/19115/-1/mda/1.3"
    xmlns:mex="https://schemas.isotc211.org/19115/-1/mex/1.3"
    xmlns:mmi="https://schemas.isotc211.org/19115/-1/mmi/1.3"
    xmlns:mpc="https://schemas.isotc211.org/19115/-1/mpc/1.3"
    xmlns:mrc="https://schemas.isotc211.org/19115/-1/mrc/1.3"
    xmlns:mrd="https://schemas.isotc211.org/19115/-1/mrd/1.3"
    xmlns:mri="https://schemas.isotc211.org/19115/-1/mri/1.3"
    xmlns:mrl="https://schemas.isotc211.org/19115/-1/mrl/1.3"
    xmlns:mrs="https://schemas.isotc211.org/19115/-1/mrs/1.3"
    xmlns:msr="https://schemas.isotc211.org/19115/-1/msr/1.3"
    xmlns:srv="https://schemas.isotc211.org/19115/-1/srv/1.3"
    xmlns:mac="https://schemas.isotc211.org/19115/-2/mac/2.2"
    xmlns:cat="https://schemas.isotc211.org/19115/-3/cat/1.0"
    xmlns:gco="https://schemas.isotc211.org/19103/-/gco/1.2"
    xmlns:gcx="https://schemas.isotc211.org/19103/-/gcx/1.2"
    xmlns:gfc="https://schemas.isotc211.org/19110/-/gfc/2.2"
    xmlns:fcc="https://schemas.isotc211.org/19110/-/fcc/2.2"
    xmlns:mdq="https://schemas.isotc211.org/19157/-/mdq/1.2"
    xmlns:gwm="https://schemas.isotc211.org/19136/-/gwm/1.1"
    xmlns:gml="https://www.opengis.net/gml/3.2"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
    exclude-result-prefixes="#all">
    
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
        <xd:desc>
            <xd:p>
                <xd:b>Created on:</xd:b>November 11, 2020 </xd:p>
            <xd:p>Translates from ISO 19115-3 V.1.0 for ISO 19115-1 and ISO 19115-2 to ISO 19115-1 V.1.3 and ISO 19115 V.2.1 and ISO 19103 v.1.1</xd:p>
            <xd:p>
                <xd:b>Version November 20, 2020</xd:b>
                <xd:ul>
                    <xd:li>Converged the 19115-3 transform into 19115-1 and ISO 19115-2
                        <xd:ul>
                            <xd:li>reorder elements inline with ISO 19115-2:2019 Ed2 data dictionaries</xd:li>
                        </xd:ul>
                    </xd:li>
                </xd:ul>
            </xd:p>
            <xd:p><xd:b>Author 1:</xd:b>BARLOW Melanie - melanie.barlow@ardc.edu.au</xd:p>
            <xd:p><xd:b>Author 2:</xd:b>BLEYS Evert - ejbleys@gmail.com</xd:p>
            <xd:p><xd:b>Responsibility:</xd:b>BLEYS Evert - ejbleys@gmail.com</xd:p>
        </xd:desc>
    </xd:doc>
    
    
    
    <xsl:output method="xml" version="1.1" indent="yes" omit-xml-declaration="no" undeclare-prefixes="yes"/>
    
    <xsl:strip-space elements="*"/>
    
    <xsl:variable name="stylesheetVersion" select="'0.1'"/>
    
    
    <!-- MI_Acquisition --> 
    <xsl:template name="MI_AcquisitionInformation">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:scope" mode="reorder"/>
            <xsl:apply-templates select="mac:acqisitionPlan" mode="reorder"/>
            <xsl:apply-templates select="mac:acquisitionRequirement" mode="reorder"/>
            <xsl:apply-templates select="mac:environmentalConditions" mode="reorder"/>
            <xsl:apply-templates select="mac:instrument" mode="reorder"/>
            <xsl:apply-templates select="mac:objective" mode="reorder"/>
            <xsl:apply-templates select="mac:operation" mode="reorder"/>
            <xsl:apply-templates select="mac:platform" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:scope" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:acqisitionPlan" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Plan" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:acquisitionRequirement" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Requirement" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:environmentalConditions" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_EnvironmentalRecord" mode="reorder"/>
        </xsl:copy>
    </xsl:template>    
    <xsl:template match="mac:instrument" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:objective" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Objective" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:operation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Operation" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:platform" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Platform" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <!-- MI_EnvironmentalRecord -->
    <xsl:template match="MI_EnvironmentalRecord" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:averageAirTemperature" mode="reorder"/>
            <xsl:apply-templates select="mac:maxRelativeHumidity" mode="reorder"/>
            <xsl:apply-templates select="mac:maxAltitude" mode="reorder"/>
            <xsl:apply-templates select="mac:meteorologicalConditions" mode="reorder"/>
            <xsl:apply-templates select="mac:solarAzimuth" mode="reorder"/>
            <xsl:apply-templates select="mac:solarElevation" mode="reorder"/>
        </xsl:copy>
    </xsl:template>   
    <xsl:template match="mac:averageAirTemperature" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:maxRelativeHumidity" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template> 
    <xsl:template match="mac:maxAltitude" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:meteorologicalConditions" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:solarAzimuth" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:solarElevation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <!-- END MI_EnvironmentalRecord -->
    <!-- MI_Instrument -->
    <xsl:template match="mac:MI_Instrument" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:type" mode="reorder"/>
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:otherProperty" mode="reorder"/>
            <xsl:apply-templates select="mac:otherPropertyType" mode="reorder"/>
            <xsl:apply-templates select="mac:mountedOn" mode="reorder"/>
            <xsl:apply-templates select="mac:sensor" mode="reorder"/>
            <xsl:apply-templates select="mac:history" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:mountedOn" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Platform" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:sensor">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:history" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_InstrumentationEventList" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_Instrument -->
    <!-- MI_Sensor -->
    <xsl:template match="mac:MI_Sensor" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:hosted" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:hosted" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <!-- End MI_Sensor -->
    <!-- MI_Objective -->
    <xsl:template match="mac:MI_Objective" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:priority" mode="reorder"/>
            <xsl:apply-templates select="mac:type" mode="reorder"/>
            <xsl:apply-templates select="mac:function" mode="reorder"/>
            <xsl:apply-templates select="mac:extent" mode="reorder"/>
            <xsl:apply-templates select="mac:objectiveOccurance" mode="reorder"/>
            <xsl:apply-templates select="mac:pass" mode="reorder"/>
            <xsl:apply-templates select="mac:sensingInstrument" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:function" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:objectiveOccurance" mode="reorder">
        <xsl:apply-templates select="mac:MI_Event" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:pass" mode="reorder">
        <xsl:apply-templates select="mac:MI_PlatformPass" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:sensingInstrument" mode="reorder">
        <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Objective -->
    <!-- MI_Operation -->
        <xsl:template match="mac:MI_Operation" mode="reorder">
        <xsl:element name="mac:MI_Operation">
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:status" mode="reorder"/>
            <xsl:apply-templates select="mac:type" mode="reorder"/>
            <xsl:apply-templates select="mac:otherProperty" mode="reorder"/>
            <xsl:apply-templates select="mac:otherPropertyType" mode="reorder"/>
            <xsl:apply-templates select="mac:childOperation" mode="reorder"/>
            <xsl:apply-templates select="mac:objective" mode="reorder"/>
            <xsl:apply-templates select="mac:parentOperation" mode="reorder"/>
            <xsl:apply-templates select="mac:plan" mode="reorder"/>
            <xsl:apply-templates select="mac:platform" mode="reorder"/>
            <xsl:apply-templates select="mac:significantEvent" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="mac:childOperation" mode="reorder">
        <xsl:apply-templates select="mac:MI_Operation" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:objective" mode="reorder">
        <xsl:apply-templates select="mac:MI_Objective" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:parentOperation" mode="reorder">
        <xsl:apply-templates select="mac:MI_Operation" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:plan" mode="reorder">
        <xsl:apply-templates select="mac:MI_Plan" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:platform" mode="reorder">
        <xsl:apply-templates select="mac:MI_Platform" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:significantEvent" mode="reorder">
        <xsl:apply-templates select="mac:MI_Event" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Operation -->
    <!-- MI_Plan -->
    <xsl:template match="mac:MI_Plan" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:type" mode="reorder"/>
            <xsl:apply-templates select="mac:status" mode="reorder"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:operation" mode="reorder"/>
            <xsl:apply-templates select="mac:satisfiedRequirement" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:status" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:operation" mode="reorder">
        <xsl:apply-templates select="mac:MI_Operation" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mac:satisfiedRequirement" mode="reorder">
        <xsl:apply-templates select="mac:MI_Requirement" mode="reorder"/>
    </xsl:template>
    <!-- End MI_Plan -->
    <!-- MI_Event -->
    <xsl:template match="mac:MI_Event" mode="reorder">
        <xsl:element name="mac:MI_Event">
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:trigger" mode="reorder"/>
            <xsl:apply-templates select="mac:content" mode="reorder"/>
            <xsl:apply-templates select="mac:sequence" mode="reorder"/>
            <xsl:apply-templates select="mac:time" mode="reorder"/>
            <xsl:apply-templates select="mac:expectedObjective" mode="reorder"/>
            <xsl:apply-templates select="mac:relatedPass" mode="reorder"/>
            <xsl:apply-templates select="mac:relatedInstrument" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="mac:trigger" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:content" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:sequence" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:time" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:apply-templates select="@*|node()"/>
            </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:expectedObjective">
        <xsl:apply-templates select="mac:MI_Objective" mode="reorder"/>
    </xsl:template>
    <xsl:template match="mac:relatedPass">
        <xsl:apply-templates select="mac:MI_PlatformPass" mode="reorder"/>
    </xsl:template>
    <xsl:template match="mac:relatedSensor">
        <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Event -->
    <!-- MI_Platform -->
    <xsl:template match="mac:MI_Platform" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:sponsor" mode="reorder"/>
            <xsl:apply-templates select="mac:otherProperty" mode="reorder"/>
            <xsl:apply-templates select="mac:otherPropertyType" mode="reorder"/>
            <xsl:apply-templates select="mac:instrument" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:sponsor" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:otherProperty" mode="reorder">
        <xsl:copy-of select="."/>
    </xsl:template>
        <xsl:template match="mac:otherPropertyType" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:instrument" mode="reorder">
        <xsl:apply-templates select="mac:MI_Instrument" mode="reorder"/>
    </xsl:template>
        <!-- END MI_Platform -->
    <!-- MI_PlatformPass -->
    <xsl:template match="mac:MI_PlatformPass" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:extent" mode="reorder"/>
            <xsl:apply-templates select="mac:relatedEvent" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:relatedEvent">
        <xsl:apply-templates select="mac:MI_Event" mode="reorder"/>
    </xsl:template>
    <!-- END MI_PlatformPass -->
    <!-- MI_RequestedDate -->
    <xsl:template match="mac:MI_RequestedDate" mode="reorder">
        <xsl:element name="mac:MI_RequestedDate">
            <xsl:apply-templates select="mac:requestedDateOfCollection" mode="reorder"/>
            <xsl:apply-templates select="mac:latestAcceptableDate" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="mac:requestedDateOfCollection" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:latestAcceptableDate" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_RequestedDate -->
    <!-- MI_Requirement -->
    <xsl:template match="mac:MI_Requirement" mode="reorder">
        <xsl:element name="mac:MI_Requirement">
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:identifier" mode="reorder"/>
            <xsl:apply-templates select="mac:requestor" mode="reorder"/>
            <xsl:apply-templates select="mac:recipient" mode="reorder"/>
            <xsl:apply-templates select="mac:priority" mode="reorder"/>
            <xsl:apply-templates select="mac:requestedDate" mode="reorder"/>
            <xsl:apply-templates select="mac:expiryDate" mode="reorder"/>
            <xsl:apply-templates select="mac:satisfiedPlan" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="mac:identifier" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:requestor" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:recipient" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:priority" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:requestedDate" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:expiryDate" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:satisfiedPlan" mode="reorder">
        <xsl:apply-templates select="mac:MI_Plan" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Requirement -->
    <!-- MI_InstrumentEventList -->
    <xsl:template match="mac:MI_InstrumentEventList" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:locale" mode="reorder"/>
            <xsl:apply-templates select="mac:constraints" mode="reorder"/>
            <xsl:apply-templates select="mac:instrumentationEvent" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:locale">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:constraints" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:instrumentationEvent" mode="reorder">
        <xsl:apply-templates select="mac:MI_InstrumentatonEvent" mode="reorder"/>
    </xsl:template>
    <!-- END MI_InstrumentEventList -->
    <!-- MI_InstrumentationEvent -->
    <xsl:template match="mac:MI_InstrumentationEvent" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:extent" mode="reorder"/>
            <xsl:apply-templates select="mac:type" mode="reorder"/>
            <xsl:apply-templates select="mac:revisionHistory" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:extent">
        <xsl:apply-templates select="gex:EX_Extent" mode="reorder"/>
    </xsl:template>
    <xsl:template match="mac:type">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mac:revisionHistory">
        <xsl:apply-templates select="mac:MI_Revision" mode="reorder"/>
    </xsl:template>
    <!-- END MI_InstrumentationEvent -->
    <!-- MI_Revision -->
    <xsl:template match="mac:MI_Revision" mode="reorder">
        <xsl:element name="mac:MI_Revision">
            <xsl:apply-templates select="mac:description" mode="reorder"/>
            <xsl:apply-templates select="mac:responsibleParty" mode="reorder"/>
            <xsl:apply-templates select="mac:dateInfo" mode="reorder"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="mac:responsibleParty">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:dateInfo" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_Revision -->
    <!-- END MI_AcquisitionInformation -->
    <!-- LE_Algorithum -->
    <xsl:template match="mac:LE_Algorithum" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:citation" mode="reorder"/>
            <xsl:apply-templates select="mac:description" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:citation" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:description" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END LE_Algorithum -->
    <!-- LE_NominalResolution -->
    <xsl:template match="mac:LE_NominalResolution" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mac:scanningResolution" mode="reorder"/>
            <xsl:apply-templates select="mac:groundResolution" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:scanningResolution" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mac:groundResolution" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END LE_NominalResolution -->
    <!-- LE_Processing -->
    <xsl:template match="mrl:LE_Processing">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrl:identifier" mode="reorder"/>
            <xsl:apply-templates select="mrl:softwareReference" mode="reorder"/>
            <xsl:apply-templates select="mrl:procedureDescription" mode="reorder"/>
            <xsl:apply-templates select="mrl:documentation" mode="reorder"/>
            <xsl:apply-templates select="mrl:runTimeParameters" mode="reorder"/>
            <xsl:apply-templates select="mrl:otherProperty" mode="reorder"/>
            <xsl:apply-templates select="mrl:otherPropertyType" mode="reorder"/>
            <xsl:apply-templates select="mrl:alogrithum" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:identifier" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:softwareReference" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:procedureDescription" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:documentation" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:runTimeParameters" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:otherProperty" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:otherPropertyType" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:alogrithum">
        <xsl:apply-templates select="mrl:LE_Algorithum" mode="reorder"/>
    </xsl:template>
    <!-- END LE_Processing -->
    <!-- LE_ProcessParameter -->
    <xsl:template match="mrl:LE_ProcessParameter" mode="reorder">
        <xsl:element name="mrl:LE_ProcessParameter">
            <xsl:apply-templates select="mrl:direction" mode="reorder"/>
            <xsl:apply-templates select="mrl:description" mode="reorder"/>
            <xsl:apply-templates select="mrl:optionality" mode="reorder"/>    
            <xsl:apply-templates select="mrl:repeatability" mode="reorder"/>    
            <xsl:apply-templates select="mrl:valueType" mode="reorder"/>    
            <xsl:apply-templates select="value" mode="reorder"/>    
            <xsl:apply-templates select="mrl:resource" mode="reorder"/>    
        </xsl:element>
    </xsl:template>
    <xsl:template match="mrl:direction" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:optionality" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:repeatability" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:valueType" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:value" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrl:resource">
        <xsl:apply-templates select="mrl:LE_Source" mode="reorder"/>
    </xsl:template>
    <!-- END LE_ProcessParameter -->
    <!-- LE_ProcessStep -->
    <xsl:template match="mrl:LE_ProcessStep" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrl:output" mode="reorder"/>
            <xsl:apply-templates select="mrl:processingInformation" mode="reorder"/>
            <xsl:apply-templates select="mrl:report" mode="reorder"/>    
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:output" mode="reorder">
        <xsl:apply-templates select="mrl:LE_Source" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mrl:processingInformation" mode="reorder">
        <xsl:apply-templates select="mrl:LE_Processing" mode="reorder"/>
    </xsl:template>
        <xsl:template match="mrl:report" mode="reorder">
        <xsl:apply-templates select="mrl:LE_ProcessStepReport" mode="reorder"/>
    </xsl:template>
    <!-- END LE_ProcessStep -->
    <!-- LE_ProcessStepReport -->
    <xsl:template match="mrl:LE_ProcessStepReport" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrl:name" mode="reorder"/>
            <xsl:apply-templates select="mrl:description" mode="reorder"/>
            <xsl:apply-templates select="mrl:fileType" mode="reorder"/>            
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:name" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:description" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:fileType" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END LE_ProcessStepReport -->
    <!-- LE_Source -->
    <xsl:template match="mrl:LE_Source" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrl:processLevel" mode="reorder"/>
            <xsl:apply-templates select="mrl:resolution" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:processLevel" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="mrl:resolution" mode="reorder">
        <xsl:apply-templates select="mrl:LE_NominalResolution" mode="reorder"/>
    </xsl:template>
    <!-- END LE_Source -->
    
    
    <!-- MI_Georectified -->
    <xsl:template match="msr:MI_Georectified" mode="reorder">
        <xsl:element name="msr:MI_Georectified">
            <xsl:apply-templates select="msr:checkPoint" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="msr:checkPoint" mode="reorder">
        <xsl:apply-templates select="msr:MI_GCP" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Georectified -->
    <!-- MI_Georeferenceable -->
    <xsl:template match="msr:MI_Georeferenceable" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="msr:geolocationInformation" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
        <xsl:template match="msr:geolocationInformation" mode="reorder">
        <xsl:apply-templates select="msr:MI_GeolocationInformation" mode="reorder"/>
    </xsl:template>
    <!-- END MI_Georeferenceable -->
    <!-- MI_GeolocationInformation -->
    <xsl:template match="msr:MI_GeolocationInformation" mode="reorder">
        <xsl:element name="msr:MI_GeolocationInformation">
            <xsl:apply-templates select="msr:qualityInfo" mode="reorder"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="msr:qualityInfo">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_GeolocationInformation -->
    <!-- MI_GCPCollection -->
    <xsl:template match="msr:MI_GCPCollection" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="msr:collectionIdentifier" mode="reorder"/>
            <xsl:apply-templates select="msr:collectionName" mode="reorder"/>
            <xsl:apply-templates select="msr:coordinateReferenceSystem" mode="reorder"/>
            <xsl:apply-templates select="msr:gcp" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="msr:collectionIdentifier" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="msr:collectionName" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="msr:coordinateReferenceSystem" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="msr:gcp" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="msr:MI_GCP" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_GCPCollection -->
    <!-- MI_GCP -->
    <xsl:template match="msr:MI_GCP" mode="reorder">
        <xsl:element name="msr:MI_GCP">
            <xsl:apply-templates select="msr:geographicCoordinates" mode="reorder"/>
            <xsl:apply-templates select="msr:accuracyReport" mode="reorder"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="msr:geographicCoordinates" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="msr:accuracyReport" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_GCP -->
    <!-- MI_Band -->
    <xsl:template match="mrc:MI_Band" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrc:bandBoundaryDefinition" mode="reorder"/>
            <xsl:apply-templates select="mrc:nominalSpatialResolution" mode="reorder"/>
            <xsl:apply-templates select="mrc:transferFunctionType" mode="reorder"/>
            <xsl:apply-templates select="mrc:transmittedPolarisation" mode="reorder"/>
            <xsl:apply-templates select="mrc:detectedPolarisation" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:bandBoundaryDefinition" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:nominalSpatialResolution" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:transferFunctionType" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:transmittedPolarisation" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:detectedPolarisation" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_Band -->
    <!-- MI_CoverageDescription -->
        <xsl:template match="mrc:MI_CoverageDescription" mode="reorder">
        <xsl:element name="mrc:MI_CoverageDescription">
            <xsl:apply-templates select="mrc:rangeElementDescription" mode="reorder"/>
        </xsl:element>
    </xsl:template>
        <xsl:template match="mrc:rangeElementDescription" mode="reorder">
        <xsl:apply-templates select="mrc:MI_RangeElementDescription" mode="reorder"/>
    </xsl:template>
    <!-- END MI_CoverageDescription -->
    <!-- MI_ImageDescription -->
        <xsl:template match="mrc:MI_ImageDescription" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrc:rangeElementDescription" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
          <!--
              <xsl:template match="mrc:rangeElementDescription">
                <xsl:apply-templates select="mrc:MI_RangeElementDescription" mode="reorder"/>
              </xsl:template>
          -->  
    <!-- END MI_ImageDescription -->
    <!-- MI_RangeElementDescription -->
    <xsl:template match="mrc:MI_RangeElementDescription" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="mrc:name" mode="reorder"/>
            <xsl:apply-templates select="mrc:definition" mode="reorder"/>
            <xsl:apply-templates select="mrc:rangeElement" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:name" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mrc:definition" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>   
    <xsl:template match="mrc:rangeElement" mode="reorder">
                <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END MI_RangeElementDescription -->
</xsl:stylesheet>