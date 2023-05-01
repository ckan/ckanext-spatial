<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.0">
    <!-- 
        This stylesheet sorts ISONamespaceInformation.xml by namespace prefix
    -->
    <xsl:template match="/">
        <xsl:element name="ISOSchema">
            <xsl:for-each select="//namespace">
                <xsl:sort select="prefix"/>
                <xsl:copy-of select="."/>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
</xsl:stylesheet>