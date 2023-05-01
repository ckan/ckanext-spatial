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
    <xsl:import href="./ISO19115-2_Reorder.xsl"/>
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
                            <xd:li>reorder elements inline with ISO 19115-1:2014 plus Amd 1 and Amd 2 data dictionaries</xd:li>
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
    
    
    <!-- MD_Metadata -->
    <xsl:template match="mdb:MD_Metadata" mode="reorder">
<!-- 
     <xsl:element name="mdb:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mdb/1.3" >
            <xsl:namespace name="mdb" select="'https://schemas.isotc211.org/19115/-1/mdb/1.3'"/>
            <xsl:namespace name="xsi" select="'https://www.w3.org/2001/XMLSchema-instance'"/>
            <xsl:namespace name="cit" select="'https://schemas.isotc211.org/19115/-1/cit/1.3'"/>
            <xsl:namespace name="gex" select="'https://schemas.isotc211.org/19115/-1/gex/1.3'"/>
            <xsl:namespace name="lan" select="'https://schemas.isotc211.org/19115/-1/lan/1.3'"/>
            <xsl:namespace name="mas" select="'https://schemas.isotc211.org/19115/-1/mas/1.3'"/>
            <xsl:namespace name="mcc" select="'https://schemas.isotc211.org/19115/-1/mcc/1.3'"/>
            <xsl:namespace name="mco" select="'https://schemas.isotc211.org/19115/-1/mco/1.3'"/>
            <xsl:namespace name="mda" select="'https://schemas.isotc211.org/19115/-1/mda/1.3'"/>
            <xsl:namespace name="mex" select="'https://schemas.isotc211.org/19115/-1/mex/1.3'"/>
            <xsl:namespace name="mmi" select="'https://schemas.isotc211.org/19115/-1/mmi/1.3'"/>
            <xsl:namespace name="mpc" select="'https://schemas.isotc211.org/19115/-1/mpc/1.3'"/>
            <xsl:namespace name="mrc" select="'https://schemas.isotc211.org/19115/-1/mrc/1.3'"/>
            <xsl:namespace name="mrd" select="'https://schemas.isotc211.org/19115/-1/mrd/1.3'"/>
            <xsl:namespace name="mri" select="'https://schemas.isotc211.org/19115/-1/mri/1.3'"/>
            <xsl:namespace name="mrl" select="'https://schemas.isotc211.org/19115/-1/mrl/1.3'"/>
            <xsl:namespace name="mrs" select="'https://schemas.isotc211.org/19115/-1/mrs/1.3'"/>
            <xsl:namespace name="msr" select="'https://schemas.isotc211.org/19115/-1/msr/1.3'"/>
            <xsl:namespace name="srv" select="'https://schemas.isotc211.org/19115/-1/srv/1.3'"/>
            <xsl:namespace name="mac" select="'https://schemas.isotc211.org/19115/-2/mac/2.2'"/>
            <xsl:namespace name="cat" select="'https://schemas.isotc211.org/19139/-/cat/1.2'"/>
            <xsl:namespace name="gco" select="'https://schemas.isotc211.org/19103/-/gco/1.2'"/>
            <xsl:namespace name="gcx" select="'https://schemas.isotc211.org/19103/-/gcx/1.2'"/>
            <xsl:namespace name="gfc" select="'https://schemas.isotc211.org/19110/-/gfc/2.2'"/>
            <xsl:namespace name="fcc" select="'https://schemas.isotc211.org/19110/-/fcc/2.2'"/>
            <xsl:namespace name="mdq" select="'https://schemas.isotc211.org/19157/-/mdq/1.2'"/>
            <xsl:namespace name="gwm" select="'https://schemas.isotc211.org/19136/-/gwm/1.1'"/>
            <xsl:namespace name="gml" select="'https://www.opengis.net/gml/3.2'"/>
            <xsl:namespace name="xlink" select="'http://www.w3.org/1999/xlink'"/>
-->
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="mdb:metadataIdentifier" mode="reorder"/>
            <xsl:apply-templates select="mdb:defaultLocale" mode="reorder"/>
            <xsl:apply-templates select="mdb:parentMetadata" mode="reorder"/>
            <xsl:apply-templates select="mdb:contact" mode="reorder"/>
            <xsl:apply-templates select="mdb:dateInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataStandard" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataProfile" mode="reorder"/>
            <xsl:apply-templates select="mdb:alternativeMetadataReference" mode="reorder"/>
            <xsl:apply-templates select="mdb:otherLocale" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataLinkage" mode="reorder"/>
            <xsl:apply-templates select="mdb:spatialRepresentationInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:referenceSystemInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataExtensionInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:identificationInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:contentInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:distributionInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:dataQualityInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:portrayalCatalogueInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataConstraints" mode="reorder"/>
            <xsl:apply-templates select="mdb:applicationSchemaInfo" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataMaintenance" mode="reorder"/>
            <xsl:apply-templates select="mdb:resourceLineage" mode="reorder"/>
            <xsl:apply-templates select="mdb:metadataScope" mode="reorder"/>
            <xsl:apply-templates select="mdb:acquisitionInfo" mode="reorder"/>
        </xsl:copy>
<!--
        </xsl:element>
-->
    </xsl:template>
    <xsl:template match="mdb:metadataIdentifier" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:defaultLocale" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:parentMetadata" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:contact" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:dateInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataStandard" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataProfile" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:alternativeMetadataReference" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:otherLocale" mode="reorder">
        <xsl:copy-of select="."/>
    </xsl:template>
    <xsl:template match="mdb:metadataLinkage" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:spatialRepresentationInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:referenceSystemInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataExtensionInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:identificationInfo" mode="reorder">
            <xsl:copy copy-namespaces="no">
                <xsl:copy-of select="./@*"/>
                <xsl:apply-templates select="mri:MD_DataIdentification" mode="reorder"/>
                <xsl:apply-templates select="srv:SV_ServiceIdentification" mode="reorder"/>
            </xsl:copy>
        
        
 
    </xsl:template>
    <xsl:template match="mdb:contentInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:distributionInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:dataQualityInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:portrayalCatalogueInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataConstraints" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:applicationSchemaInfo" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataMaintenance" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:resourceLineage" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:metadataScope" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mdb:acquisitionInfo" mode="reorder">
        <xsl:call-template name="MI_AcquisitionInformation"/>
    </xsl:template>
    <!-- END MD_Metadata -->
    <!-- MD_Identification -->
    <xsl:template name="MD_IdentificationInfo">
        <xsl:apply-templates select="mri:citation" mode="reorder"/>
        <xsl:apply-templates select="mri:abstract" mode="reorder"/>
        <xsl:apply-templates select="mri:purpose" mode="reorder"/>
        <xsl:apply-templates select="mri:credit" mode="reorder"/>
        <xsl:apply-templates select="mri:status" mode="reorder"/>
        <xsl:apply-templates select="mri:pointOfContact" mode="reorder"/>
        <xsl:apply-templates select="mri:spatialRepresentationType" mode="reorder"/>
        <xsl:apply-templates select="mri:spatialResolution" mode="reorder"/>
        <xsl:apply-templates select="mri:temporalResolution" mode="reorder"/>
        <xsl:apply-templates select="mri:topicCategory" mode="reorder"/>
        <xsl:apply-templates select="mri:extent" mode="reorder"/>
        <xsl:apply-templates select="mri:additionalDocumentation" mode="reorder"/>
        <xsl:apply-templates select="mri:processLevel" mode="reorder"/>
        <xsl:apply-templates select="mri:resourceMaintanance" mode="reorder"/>
        <xsl:apply-templates select="mri:graphicOverview" mode="reorder"/>
        <xsl:apply-templates select="mri:resourceFormat" mode="reorder"/>
        <xsl:apply-templates select="mri:descriptiveKeywords" mode="reorder"/>
        <xsl:apply-templates select="mri:resourceSpecificUsage" mode="reorder"/>
        <xsl:apply-templates select="mri:resourceConstraints" mode="reorder"/>
        <xsl:apply-templates select="mri:associatedResource" mode="reorder"/>
    </xsl:template>
    <xsl:template match="mri:citation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:abstract" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:purpose" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:credit" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:status" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:pointOfContact" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:spatialRepresentationType" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:spatialResolution" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:temporalResolution" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:topicCategory" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:extent" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="gex:EX_Extent" mode="reorder"/>
        </xsl:copy>
     </xsl:template>
    <xsl:template match="mri:additionalDocumentation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:processLevel" mode="reorder">
        <xsl:copy-of select="."/>
    </xsl:template>
    <xsl:template match="mri:resourceMaintanance" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:graphicOverview" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:resourceFormat" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:descriptiveKeywords" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:resourceSpecificUsage" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:resourceConstraints" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:associatedResource" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
<!-- END MD_Identification -->
<!-- MD_DataIdentification -->
    <xsl:template match="mri:MD_DataIdentification" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
                <xsl:call-template name="MD_IdentificationInfo"/>
                <xsl:call-template name="MD_DataIdentification"/>
            </xsl:copy>
    </xsl:template>
    <xsl:template name="MD_DataIdentification">
        
            <xsl:apply-templates select="mri:otherLocale" mode="reorder"/>
        <xsl:apply-templates select="mri:otherLocale" mode="reorder"/>
        <xsl:apply-templates select="mri:environmentalDescription" mode="reorder"/>
        <xsl:apply-templates select="mri:supplementalInformation" mode="reorder"/> 
    </xsl:template>
    <xsl:template match="mri:defaultLocale" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:otherLocale" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:environmentalDescription" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="mri:supplementalInformation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
<!-- END MD_DataIdentification -->
<!-- SV_ServiceIdentification -->
    <xsl:template match="srv:SV_ServiceIdentification" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:call-template name="MD_IdentificationInfo"/>
            <xsl:call-template name="SV_ServiceIdentification"/>
        </xsl:copy>
    </xsl:template>
   <xsl:template name="SV_ServiceIdentification">
    <xsl:apply-templates select="srv:serviceType" mode="reorder"/>
    <xsl:apply-templates select="srv:serviceTypeVersion" mode="reorder"/>
    <xsl:apply-templates select="srv:accessProperties" mode="reorder"/>
    <xsl:apply-templates select="srv:couplingType" mode="reorder"/>
    <xsl:apply-templates select="srv:coupledResource" mode="reorder"/>
    <xsl:apply-templates select="operatedDataset" mode="reorder"/>
    <xsl:apply-templates select="srv:profile" mode="reorder"/>
    <xsl:apply-templates select="srv:serviceStandard" mode="reorder"/>
    <xsl:apply-templates select="srv:containsOperations" mode="reorder"/>
    <xsl:apply-templates select="srv:operatesOn" mode="reorder"/>
    <xsl:apply-templates select="srv:containsChain" mode="reorder"/>
</xsl:template>
    <xsl:template match="srv:serviceType" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:serviceTypeVersion" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:accessProperties" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:couplingType" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:coupledResource" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="srv:SV_CoupledResource" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    
   <xsl:template match="srv:operatedDataset" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:profile" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:serviceStandard" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:containsOperations" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:operatesOn" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:containsChain" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!-- END SV_ServiceIdentification -->
    <!-- SV_CoupledResource -->
    <xsl:template match="srv:SV_CoupledResource" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
            <xsl:apply-templates select="srv:scopedName" mode="reorder"/>
            <xsl:apply-templates select="srv:resourceReference" mode="reorder"/>
            <xsl:apply-templates select="srv:resource" mode="reorder"/>
            <xsl:apply-templates select="srv:operation" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:scopedName" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:resourceReference" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:resource" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="srv:operation" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template> 
    <!-- END SV_CoupledResource -->
    <!-- EX_Extent -->
    <xsl:template match="gex:EX_Extent" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:copy-of select="./@*"/>
                 <xsl:apply-templates select="gex:description" mode="reorder"/>
                <xsl:apply-templates select="gex:geogrpahicElement" mode="reorder"/>
                <xsl:apply-templates select="gex:temporalElement" mode="reorder"/>
                <xsl:apply-templates select="gex:verticalElement" mode="reorder"/>
        </xsl:copy>
    </xsl:template>
 
    <xsl:template match="gex:description" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:geogrpahicElement" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:temporalElement" mode="reorder">
        <xsl:element name="gex:temporalElement">
        <xsl:copy-of select="@*"/>
        <xsl:apply-templates select="gex:EX_TemporalExtent" mode="reorder"/>
        <xsl:apply-templates select="gex:EX_SpatialTemporalExtent" mode="reorder"/>
        </xsl:element>
        </xsl:template>
    <xsl:template match="gex:verticalElement" mode="reorder">
        <xsl:element name="gex:verticalElement">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates select="gex:EX_VerticalExtent" mode="reorder"/>
        </xsl:element>
    </xsl:template> 
    <!-- EX_Extent//EX_SpatialTemporalExtent -->
    <xsl:template match="gex:EX_TemporalExtent" mode="reorder">
        <xsl:copy-of select="."/>
    </xsl:template>
    <xsl:template match="gex:EX_SpatialTemporalExtent" mode="reorder">
        <xsl:element name="gex:EX_SpatialTemporalExtent">
            <xsl:apply-templates select="gex:extent" mode="reorder"/>
            <xsl:apply-templates select="gex:verticalExtent" mode="reorder"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="gex:extent" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:verticalExtent" mode="reorder">
        <xsl:element name="gex:verticalExtent">
        <xsl:apply-templates select="gex:EX_VerticalExtent" mode="reorder"/>
        </xsl:element>
    </xsl:template> 
    <!-- END EX_Extent//EX_SpatialTemporalExtent -->
    <!-- EX_Extent//EX_VerticalExtent -->
    <xsl:template match="gex:EX_VerticalExtent" mode="reorder">
        <xsl:element name="gex:EX_VerticalExtent">
            <xsl:copy-of select="@*"/>
            <xsl:apply-templates select="gex:minimumValue" mode="reorder"/>
            <xsl:apply-templates select="gex:maximumValue" mode="reorder"/>
            <xsl:apply-templates select="gex:verticalCRS" mode="reorder"/>
            <xsl:apply-templates select="gex:verticalCRSId" mode="reorder"/>
        </xsl:element>
    </xsl:template>
    <xsl:template match="gex:minimumValue" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:maximumValue" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:verticalCRS" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="gex:verticalCRSId" mode="reorder">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template> 
    <!-- END EX_Extent//EX_VerticalExtent -->
    <!-- END EX_Extent -->
</xsl:stylesheet>