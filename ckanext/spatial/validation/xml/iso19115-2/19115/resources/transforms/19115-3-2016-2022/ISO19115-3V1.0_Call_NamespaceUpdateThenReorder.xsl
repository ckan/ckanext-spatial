<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:mdb="https://schemas.isotc211.org/19115/-1/mdb/1.3"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <xsl:import href="ISO19115-1-2_Reorder.xsl"/>
    <xsl:import href="ISO19115-3V1.0_NamespaceUpdate.xsl"/>
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
        <xd:desc>
            <xd:p>
                <xd:b>Created on:</xd:b>November 11, 2020 </xd:p>
            <xd:p>Translates from ISO 19115-3 V.1.0 for ISO 19115-1 and ISO 19115-2 to ISO 19115-1 V.1.3 and ISO 19115 V.2.1 and ISO 19103 v.1.1</xd:p>
            <xd:p>
                <xd:b>Version November 20, 2020</xd:b>
                <xd:ul>
                    <xd:li>Process for the 19115-3 transform into 19115-1 and ISO 19115-2 
                    <xd:ul>
                        <xd:li>update namespace URIs</xd:li>
                        <xd:li>reorder elements inline with relevant data dictionaries</xd:li>
                    </xd:ul></xd:li>
                </xd:ul>
            </xd:p>
            <xd:p><xd:b>Author 1:</xd:b>BARLOW Melanie - melanie.barlow@ardc.edu.au</xd:p>
            <xd:p><xd:b>Responsibility:</xd:b>BLEYS Evert - ejbleys@gmail.com</xd:p>
        </xd:desc>
    </xd:doc>
    
    <xsl:template match="/">
        <xsl:variable name="allOutputXML" as="node()*">
            <xsl:copy>
                <xsl:apply-templates select="node()|@*"/>
            </xsl:copy>
        </xsl:variable>
        <xsl:apply-templates select="$allOutputXML//mdb:MD_Metadata" mode="reorder"/>
    </xsl:template>
    
</xsl:stylesheet>