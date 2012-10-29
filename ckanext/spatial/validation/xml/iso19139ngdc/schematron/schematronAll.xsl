<?xml version="1.0" encoding="utf-8"?>
<axsl:stylesheet xmlns:axsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:saxon="http://saxon.sf.net/" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:schold="http://www.ascc.net/xml/schematron" xmlns:iso="http://purl.oclc.org/dsdl/schematron" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco"
	xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:gts="http://www.isotc211.org/2005/gts" xmlns:gmi="http://www.isotc211.org/2005/gmi" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gmx="http://www.isotc211.org/2005/gmx" version="2.0">
  
  <!-- Purpose: to run a schematron report as an XSL on ISO metadata. In use at http://www.ngdc.noaa.gov/MetadataTransform/XLinkResolver.jsp -->
  <!-- Nov 28, 2011 Anna Milan - updated gml namespace to 3.2 -->
  <!-- Nov 30, 2011  added CSS stylesheet, removed namespace-uri() from Xpath output-->
	<!--Implementers: please note that overriding process-prolog or process-root is 
    the preferred method for meta-stylesheets to use where possible. -->
	<axsl:param name="archiveDirParameter"/>
	<axsl:param name="archiveNameParameter"/>
	<axsl:param name="fileNameParameter"/>
	<axsl:param name="fileDirParameter"/>
	<axsl:variable name="document-uri">
		<axsl:value-of select="document-uri(/)"/>
	</axsl:variable>
	<!--PHASES-->
	<!--PROLOG-->
	<axsl:output xmlns:svrl="http://purl.oclc.org/dsdl/svrl" method="xml" omit-xml-declaration="no" standalone="yes" indent="yes"/>  
	<!--XSD TYPES FOR XSLT2-->
	<!--KEYS AND FUNCTIONS-->
	<!--DEFAULT RULES-->
	<!--MODE: SCHEMATRON-SELECT-FULL-PATH-->
	<!--This mode can be used to generate an ugly though full XPath for locators-->
	<axsl:template match="*" mode="schematron-select-full-path">	 
		<axsl:apply-templates select="." mode="schematron-get-full-path"/>
	</axsl:template>
	<!--MODE: SCHEMATRON-FULL-PATH-->
	<!--This mode can be used to generate an ugly though full XPath for locators-->
	<axsl:template match="*" mode="schematron-get-full-path">
		<axsl:apply-templates select="parent::*" mode="schematron-get-full-path"/>
		<axsl:text>/</axsl:text>
		<axsl:choose>
			<axsl:when test="namespace-uri()=''">
				<axsl:value-of select="name()"/>
			</axsl:when>
			<axsl:otherwise>
			<!--	<axsl:text>*:</axsl:text>-->
			  <axsl:value-of select="name()"/>
				<!--<axsl:value-of select="local-name()"/>
				<axsl:text>[namespace-uri()='</axsl:text>
				<axsl:value-of select="namespace-uri()"/>
				<axsl:text>']</axsl:text>-->
			</axsl:otherwise>
		</axsl:choose>
		<axsl:variable name="preceding" select="count(preceding-sibling::*[local-name()=local-name(current()) and namespace-uri() = namespace-uri(current())])"/>
		<axsl:text>[</axsl:text>
		<axsl:value-of select="1+ $preceding"/>
		<axsl:text>]</axsl:text>
	</axsl:template>
	<axsl:template match="@*" mode="schematron-get-full-path">
		<axsl:apply-templates select="parent::*" mode="schematron-get-full-path"/>
		<axsl:text>/</axsl:text>
		<axsl:choose>
			<axsl:when test="namespace-uri()=''">@<axsl:value-of select="name()"/>
			</axsl:when>
			<axsl:otherwise>
				<axsl:text>@*[local-name()='</axsl:text>
				<axsl:value-of select="local-name()"/>
				<axsl:text>' and namespace-uri()='</axsl:text>
				<axsl:value-of select="namespace-uri()"/>
				<axsl:text>']</axsl:text>
			</axsl:otherwise>
		</axsl:choose>
	</axsl:template>
	<!--MODE: SCHEMATRON-FULL-PATH-2-->
	<!--This mode can be used to generate prefixed XPath for humans-->
	<axsl:template match="node() | @*" mode="schematron-get-full-path-2">
		<axsl:for-each select="ancestor-or-self::*">
			<axsl:text>/</axsl:text>
			<axsl:value-of select="name(.)"/>
			<axsl:if test="preceding-sibling::*[name(.)=name(current())]">
				<axsl:text>[</axsl:text>
				<axsl:value-of select="count(preceding-sibling::*[name(.)=name(current())])+1"/>
				<axsl:text>]</axsl:text>
			</axsl:if>
		</axsl:for-each>
		<axsl:if test="not(self::*)">
			<axsl:text/>/@<axsl:value-of select="name(.)"/>
		</axsl:if>
	</axsl:template>
	<!--MODE: SCHEMATRON-FULL-PATH-3-->
	<!--This mode can be used to generate prefixed XPath for humans 
	(Top-level element has index)-->
	<axsl:template match="node() | @*" mode="schematron-get-full-path-3">
		<axsl:for-each select="ancestor-or-self::*">
			<axsl:text>/</axsl:text>
			<axsl:value-of select="name(.)"/>
			<axsl:if test="parent::*">
				<axsl:text>[</axsl:text>
				<axsl:value-of select="count(preceding-sibling::*[name(.)=name(current())])+1"/>
				<axsl:text>]</axsl:text>
			</axsl:if>
		</axsl:for-each>
		<axsl:if test="not(self::*)">
			<axsl:text/>/@<axsl:value-of select="name(.)"/>
		</axsl:if>
	</axsl:template>
	<!--MODE: GENERATE-ID-FROM-PATH -->
	<axsl:template match="/" mode="generate-id-from-path"/>
	<axsl:template match="text()" mode="generate-id-from-path">
		<axsl:apply-templates select="parent::*" mode="generate-id-from-path"/>
		<axsl:value-of select="concat('.text-', 1+count(preceding-sibling::text()), '-')"/>
	</axsl:template>
	<axsl:template match="comment()" mode="generate-id-from-path">
		<axsl:apply-templates select="parent::*" mode="generate-id-from-path"/>
		<axsl:value-of select="concat('.comment-', 1+count(preceding-sibling::comment()), '-')"/>
	</axsl:template>
	<axsl:template match="processing-instruction()" mode="generate-id-from-path">
		<axsl:apply-templates select="parent::*" mode="generate-id-from-path"/>
		<axsl:value-of select="concat('.processing-instruction-', 1+count(preceding-sibling::processing-instruction()), '-')"/>
	</axsl:template>
	<axsl:template match="@*" mode="generate-id-from-path">
		<axsl:apply-templates select="parent::*" mode="generate-id-from-path"/>
		<axsl:value-of select="concat('.@', name())"/>
	</axsl:template>
	<axsl:template match="*" mode="generate-id-from-path" priority="-0.5">
		<axsl:apply-templates select="parent::*" mode="generate-id-from-path"/>
		<axsl:text>.</axsl:text>
		<axsl:value-of select="concat('.',name(),'-',1+count(preceding-sibling::*[name()=name(current())]),'-')"/>
	</axsl:template>
	<!--MODE: GENERATE-ID-2 -->
	<axsl:template match="/" mode="generate-id-2">U</axsl:template>
	<axsl:template match="*" mode="generate-id-2" priority="2">
		<axsl:text>U</axsl:text>
		<axsl:number level="multiple" count="*"/>
	</axsl:template>
	<axsl:template match="node()" mode="generate-id-2">
		<axsl:text>U.</axsl:text>
		<axsl:number level="multiple" count="*"/>
		<axsl:text>n</axsl:text>
		<axsl:number count="node()"/>
	</axsl:template>
	<axsl:template match="@*" mode="generate-id-2">
		<axsl:text>U.</axsl:text>
		<axsl:number level="multiple" count="*"/>
		<axsl:text>_</axsl:text>
		<axsl:value-of select="string-length(local-name(.))"/>
		<axsl:text>_</axsl:text>
		<axsl:value-of select="translate(name(),':','.')"/>
	</axsl:template>
	<!--Strip characters-->
	<axsl:template match="text()" priority="-1"/>
	<!--SCHEMA SETUP-->
	<axsl:template match="/">
	  <xsl:processing-instruction name="xml-stylesheet">
	    <xsl:text>type="text/css" </xsl:text>
	    <xsl:text>href="</xsl:text>
	    <xsl:value-of select="'http://www.ngdc.noaa.gov/metadata/published/xsd/schematron/schematronOutput.css'"/>
	    <xsl:text>"</xsl:text>
	  </xsl:processing-instruction>	  
		<svrl:schematron-output xmlns:svrl="http://purl.oclc.org/dsdl/svrl" title="" schemaVersion="ISO19757-3">
			<axsl:comment>
				<axsl:value-of select="$archiveDirParameter"/>   <axsl:value-of select="$archiveNameParameter"/>   <axsl:value-of select="$fileNameParameter"/>   <axsl:value-of select="$fileDirParameter"/>
			</axsl:comment>
			<svrl:ns-prefix-in-attribute-values uri="http://www.isotc211.org/2005/gmd" prefix="gmd"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.isotc211.org/2005/gco" prefix="gco"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.opengis.net/gml/3.2" prefix="gml"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.isotc211.org/2005/gts" prefix="gts"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.isotc211.org/2005/gmi" prefix="gmi"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.w3.org/1999/xlink" prefix="xlink"/>
			<svrl:ns-prefix-in-attribute-values uri="http://www.isotc211.org/2005/gmx" prefix="gmx"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd elements</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M7"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gml elements</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M8"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">//gml:DirectPositionType</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M9"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">CI_ResponsibleParty</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M10"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">other restrictions in MD_LegalConstraints</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M11"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_Band Units</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M12"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">Source description or Source Extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M13"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">Lineage/source and Lineage/processStep</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M14"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">Lineage/source, statement and processStep</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M15"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">LI_Lineage/processStep, statement and source</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M16"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">DQ_DataQuality/DQ_Scope</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M17"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">DQ_Scope</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M18"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_Medium</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M19"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_Distribution</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M20"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:EX_Extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M21"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_DataIdentification Extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M22"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">//gmd:MD_DataIdentification</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M23"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_AggregateInformation</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M24"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:language</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M25"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">//gmd:MD_ExtendedElementInformation</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M26"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_ExtendedElementInformation</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M27"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_ExtendedElementInformation</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M28"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_ExtendedElementInformation</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M29"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">MD_Georectified</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M30"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_DataIdentification/gmd:extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M31"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_DataIdentification/gmd:extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M32"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">gmd:MD_DataIdentification/gmd:extent</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M33"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="id">checkCodeList</axsl:attribute>
				<axsl:attribute name="name">checkCodeList</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M34"/>
			<svrl:active-pattern>
				<axsl:attribute name="document">
					<axsl:value-of select="document-uri(/)"/>
				</axsl:attribute>
				<axsl:attribute name="name">Report weird characters</axsl:attribute>
				<axsl:apply-templates/>
			</svrl:active-pattern>
			<axsl:apply-templates select="/" mode="M35"/>
		</svrl:schematron-output>
	</axsl:template>
	<!--SCHEMATRON PATTERNS-->
	<!--PATTERN gmd elements-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd elements</svrl:text>
	<!--RULE -->
	<axsl:template match="gmd:*|gmi:*" priority="1000" mode="M7">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="gmd:*|gmi:*"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="./gco:CharacterString | ./@gco:nilReason | ./@xlink:href | @uuidref | ./@codeListValue | ./child::node()"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="./gco:CharacterString | ./@gco:nilReason | ./@xlink:href | @uuidref | ./@codeListValue | ./child::node()">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>Element must have content or one of the following attributes: nilReason, xlink:href or uuidref. </svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="contains('missing inapplicable template unknown withheld', ./@gco:nilReason)"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains('missing inapplicable template unknown withheld', ./@gco:nilReason)">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>'<axsl:text/>
						<axsl:value-of select="./@gco:nilReason"/>
						<axsl:text/>' is not an accepted value. gco:nilReason attribute may only contain: missing, inapplicable, template, unknown, or withheld for element: <axsl:text/>
						<axsl:value-of select="name(.)"/>
						<axsl:text/>
					</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M7"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M7"/>
	<axsl:template match="@*|node()" priority="-2" mode="M7">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M7"/>
	</axsl:template>
	<!--PATTERN gml elements-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gml elements</svrl:text>
	<!--RULE -->
	<axsl:template match="gml:*" priority="1000" mode="M8">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="gml:*"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="./@indeterminatePosition | ./child::node()"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="./@indeterminatePosition | ./child::node()">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>The <axsl:text/>
						<axsl:value-of select="name(.)"/>
						<axsl:text/> Element must have content or, if allowed, an indeterminatePosition attribute.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M8"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M8"/>
	<axsl:template match="@*|node()" priority="-2" mode="M8">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M8"/>
	</axsl:template>
	<!--PATTERN //gml:DirectPositionType-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">//gml:DirectPositionType</svrl:text>
	<!--RULE -->
	<axsl:template match="//gml:DirectPositionType" priority="1000" mode="M9">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gml:DirectPositionType"/>-->
		<!--REPORT -->
		<axsl:if test="not(@srsDimension) or @srsName">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(@srsDimension) or @srsName">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>The presence of a dimension attribute implies the presence of the srsName attribute.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="not(@axisLabels) or @srsName">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(@axisLabels) or @srsName">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>The presence of an axisLabels attribute implies the presence of the srsName attribute.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="not(@uomLabels) or @srsName">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(@uomLabels) or @srsName">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>The presence of an uomLabels attribute implies the presence of the srsName attribute.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="(not(@uomLabels) and not(@axisLabels)) or (@uomLabels and @axisLabels)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(not(@uomLabels) and not(@axisLabels)) or (@uomLabels and @axisLabels)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>The presence of an uomLabels attribute implies the presence of the axisLabels attribute and vice versa.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M9"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M9"/>
	<axsl:template match="@*|node()" priority="-2" mode="M9">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M9"/>
	</axsl:template>
	<!--PATTERN CI_ResponsibleParty-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">CI_ResponsibleParty</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:CI_ResponsibleParty" priority="1000" mode="M10">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:CI_ResponsibleParty"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="(count(gmd:individualName) + count(gmd:organisationName) + count(gmd:positionName)) &gt; 0"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(count(gmd:individualName) + count(gmd:organisationName) + count(gmd:positionName)) &gt; 0">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>You must specify one or more of gmd:individualName, gmd:organisationName or gmd:positionName.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M10"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M10"/>
	<axsl:template match="@*|node()" priority="-2" mode="M10">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M10"/>
	</axsl:template>
	<!--PATTERN other restrictions in MD_LegalConstraints-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">other restrictions in MD_LegalConstraints</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_LegalConstraints" priority="1000" mode="M11">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_LegalConstraints"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:accessConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:accessConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:accessConstraints has a gmd:MD_RestrictionCode with a value of 'otherRestrictions' then gmd: otherConstraints must be documented.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="gmd:useConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:useConstraints/gmd:MD_RestrictionCode/@codeListValue='otherRestrictions' and not(gmd:otherConstraints)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:useConstraints has a gmd:MD_RestrictionCode with a value of 'otherRestrictions' then gmd: otherConstraints must be documented.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M11"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M11"/>
	<axsl:template match="@*|node()" priority="-2" mode="M11">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M11"/>
	</axsl:template>
	<!--PATTERN MD_Band Units-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_Band Units</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_Band" priority="1000" mode="M12">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_Band"/>-->
		<!--REPORT -->
		<axsl:if test="(gmd:maxValue or gmd:minValue) and not(gmd:units)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(gmd:maxValue or gmd:minValue) and not(gmd:units)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>gmd:units is mandatory if gmd:maxValue or gmd:minValue are provided.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M12"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M12"/>
	<axsl:template match="@*|node()" priority="-2" mode="M12">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M12"/>
	</axsl:template>
	<!--PATTERN Source description or Source Extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">Source description or Source Extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:LI_Source | //gmi:LE_Source" priority="1000" mode="M13">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:LI_Source | //gmi:LE_Source"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:description or gmd:sourceExtent"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:description or gmd:sourceExtent">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>If gmd:SourcExtent is not documented then gmd:description is mandatory.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M13"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M13"/>
	<axsl:template match="@*|node()" priority="-2" mode="M13">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M13"/>
	</axsl:template>
	<!--PATTERN Lineage/source and Lineage/processStep-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">Lineage/source and Lineage/processStep</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:DQ_DataQuality" priority="1000" mode="M14">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:DQ_DataQuality"/>-->
		<!--REPORT -->
		<axsl:if test="(((count(*/gmd:LI_Lineage/gmd:source) + count(*/gmd:LI_Lineage/gmd:processStep)) = 0) and (gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='series')) and not(gmd:lineage/gmd:LI_Lineage/gmd:statement) and (gmd:lineage)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(((count(*/gmd:LI_Lineage/gmd:source) + count(*/gmd:LI_Lineage/gmd:processStep)) = 0) and (gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='series')) and not(gmd:lineage/gmd:LI_Lineage/gmd:statement) and (gmd:lineage)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:source and gmd:processStep do not exist and gmd:DQ_Dataquality/gmd:scope/gmd:level = 'dataset' or 'series' then gmd:statement is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M14"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M14"/>
	<axsl:template match="@*|node()" priority="-2" mode="M14">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M14"/>
	</axsl:template>
	<!--PATTERN Lineage/source, statement and processStep-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">Lineage/source, statement and processStep</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:LI_Lineage" priority="1000" mode="M15">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:LI_Lineage"/>-->
		<!--REPORT -->
		<axsl:if test="not(gmd:source) and not(gmd:statement) and not(gmd:processStep)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(gmd:source) and not(gmd:statement) and not(gmd:processStep)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:statement and gmd:processStep are not documented under LI_LIneage then gmd:source is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M15"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M15"/>
	<axsl:template match="@*|node()" priority="-2" mode="M15">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M15"/>
	</axsl:template>
	<!--PATTERN LI_Lineage/processStep, statement and source-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">LI_Lineage/processStep, statement and source</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:LI_Lineage" priority="1000" mode="M16">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:LI_Lineage"/>-->
		<!--REPORT -->
		<axsl:if test="not(gmd:processStep) and not(gmd:statement) and not(gmd:source)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(gmd:processStep) and not(gmd:statement) and not(gmd:source)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:statement and gmd:source are not documented under LI_LIneage then gmd:processStep is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M16"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M16"/>
	<axsl:template match="@*|node()" priority="-2" mode="M16">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M16"/>
	</axsl:template>
	<!--PATTERN DQ_DataQuality/DQ_Scope-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">DQ_DataQuality/DQ_Scope</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:DQ_DataQuality" priority="1000" mode="M17">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:DQ_DataQuality"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' and not(gmd:report) and not(gmd:lineage)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:scope/gmd:DQ_Scope/gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' and not(gmd:report) and not(gmd:lineage)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:level/gmd:MD_ScopeCode is = 'dataset' then gmd:report or gmd:lineage is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M17"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M17"/>
	<axsl:template match="@*|node()" priority="-2" mode="M17">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M17"/>
	</axsl:template>
	<!--PATTERN DQ_Scope-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">DQ_Scope</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:DQ_Scope" priority="1000" mode="M18">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:DQ_Scope"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:level/gmd:MD_ScopeCode/@codeListValue='series' or (gmd:levelDescription and ((normalize-space(gmd:levelDescription) != '') or (gmd:levelDescription/gmd:MD_ScopeDescription)))"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:level/gmd:MD_ScopeCode/@codeListValue='dataset' or gmd:level/gmd:MD_ScopeCode/@codeListValue='series' or (gmd:levelDescription and ((normalize-space(gmd:levelDescription) != '') or (gmd:levelDescription/gmd:MD_ScopeDescription)))">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>If gmd:MD_ScopeCode is not equal to 'dataset' or 'series' then gmd:levelDescription is mandatory. </svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M18"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M18"/>
	<axsl:template match="@*|node()" priority="-2" mode="M18">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M18"/>
	</axsl:template>
	<!--PATTERN MD_Medium-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_Medium</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_Medium" priority="1000" mode="M19">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_Medium"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:density and not(gmd:densityUnits)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:density and not(gmd:densityUnits)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:density is provided then gmd:densityUnits is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M19"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M19"/>
	<axsl:template match="@*|node()" priority="-2" mode="M19">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M19"/>
	</axsl:template>
	<!--PATTERN gmd:MD_Distribution-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_Distribution</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_Distribution" priority="1000" mode="M20">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_Distribution"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="count(gmd:distributionFormat)&gt;0 or count(gmd:distributor/gmd:MD_Distributor/gmd:distributorFormat)&gt;0"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="count(gmd:distributionFormat)&gt;0 or count(gmd:distributor/gmd:MD_Distributor/gmd:distributorFormat)&gt;0">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>You must provide either gmd:distributionFormat or gmd:distributorFormat.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M20"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M20"/>
	<axsl:template match="@*|node()" priority="-2" mode="M20">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M20"/>
	</axsl:template>
	<!--PATTERN gmd:EX_Extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:EX_Extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:EX_Extent" priority="1000" mode="M21">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:EX_Extent"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="count(gmd:description)&gt;0 or count(gmd:geographicElement)&gt;0 or count(gmd:temporalElement)&gt;0 or count(gmd:verticalElement)&gt;0"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="count(gmd:description)&gt;0 or count(gmd:geographicElement)&gt;0 or count(gmd:temporalElement)&gt;0 or count(gmd:verticalElement)&gt;0">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>You must document at least one of the following under gmd:EX_Extent: gmd:description, gmd:geographicElement, or gmd:temporalElement.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M21"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M21"/>
	<axsl:template match="@*|node()" priority="-2" mode="M21">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M21"/>
	</axsl:template>
	<!--PATTERN gmd:MD_DataIdentification Extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_DataIdentification Extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_DataIdentification" priority="1000" mode="M22">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_DataIdentification"/>-->
		<!--REPORT -->
		<axsl:if test="(not(gmd:hierarchyLevel) or gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') and (count(//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox) + count (//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicDescription)) =0">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(not(gmd:hierarchyLevel) or gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') and (count(//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox) + count (//gmd:MD_DataIdentification/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicDescription)) =0">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If the metadata gmd:hierarchyLevel code = 'dataset' then you must document gmd:EX_GeographicBoundingBox or gmd:EX_GeographicDescription.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M22"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M22"/>
	<axsl:template match="@*|node()" priority="-2" mode="M22">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M22"/>
	</axsl:template>
	<!--PATTERN //gmd:MD_DataIdentification-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">//gmd:MD_DataIdentification</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_DataIdentification" priority="1000" mode="M23">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_DataIdentification"/>-->
		<!--REPORT -->
		<axsl:if test="(not(../../gmd:hierarchyLevel) or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='series')) and (not(gmd:topicCategory))">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(not(../../gmd:hierarchyLevel) or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='dataset') or (../../gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue='series')) and (not(gmd:topicCategory))">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If the metadata gmd:hierarchyLevel code = 'dataset' or 'series' then gmd:topicCategory is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M23"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M23"/>
	<axsl:template match="@*|node()" priority="-2" mode="M23">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M23"/>
	</axsl:template>
	<!--PATTERN gmd:MD_AggregateInformation-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_AggregateInformation</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_AggregateInformation" priority="1000" mode="M24">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_AggregateInformation"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>Either gmd:aggregateDataSetName or gmd:aggregateDataSetIdentifier must be documented.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M24"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M24"/>
	<axsl:template match="@*|node()" priority="-2" mode="M24">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M24"/>
	</axsl:template>
	<!--PATTERN gmd:language-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:language</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_Metadata|//gmi:MI_Metadata" priority="1000" mode="M25">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_Metadata|//gmi:MI_Metadata"/>-->
		<!--REPORT -->
		<axsl:if test="not(gmd:language) or (gmd:language/@gco:nilReason)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="not(gmd:language) or (gmd:language/@gco:nilReason)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>gmd:language is required if it is not defined by encoding.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M25"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M25"/>
	<axsl:template match="@*|node()" priority="-2" mode="M25">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M25"/>
	</axsl:template>
	<!--PATTERN //gmd:MD_ExtendedElementInformation-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">//gmd:MD_ExtendedElementInformation</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_ExtendedElementInformation" priority="1000" mode="M26">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_ExtendedElementInformation"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="(gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelist' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='enumeration' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement') or (gmd:obligation or (gmd:obligation/gmd:MD_ObligationCode) or (gmd:obligation/@gco:nilReason))"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelist' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='enumeration' or gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement') or (gmd:obligation or (gmd:obligation/gmd:MD_ObligationCode) or (gmd:obligation/@gco:nilReason))">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>If gmd:dataType notEqual 'codelist', 'enumeration' or 'codelistElement' then gmd:obligation is mandatory.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M26"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M26"/>
	<axsl:template match="@*|node()" priority="-2" mode="M26">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M26"/>
	</axsl:template>
	<!--PATTERN MD_ExtendedElementInformation-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_ExtendedElementInformation</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_ExtendedElementInformation" priority="1000" mode="M27">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_ExtendedElementInformation"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:obligation/gmd:MD_ObligationCode='conditional' and not(gmd:condition)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:obligation/gmd:MD_ObligationCode='conditional' and not(gmd:condition)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:obligation = 'conditional' then gmd:condition is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M27"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M27"/>
	<axsl:template match="@*|node()" priority="-2" mode="M27">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M27"/>
	</axsl:template>
	<!--PATTERN MD_ExtendedElementInformation-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_ExtendedElementInformation</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_ExtendedElementInformation" priority="1000" mode="M28">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_ExtendedElementInformation"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement' and not(gmd:domainCode)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue='codelistElement' and not(gmd:domainCode)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:dataType = 'codelistElement' then gmd:domainCode is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M28"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M28"/>
	<axsl:template match="@*|node()" priority="-2" mode="M28">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M28"/>
	</axsl:template>
	<!--PATTERN MD_ExtendedElementInformation-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_ExtendedElementInformation</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_ExtendedElementInformation" priority="1000" mode="M29">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_ExtendedElementInformation"/>-->
		<!--REPORT -->
		<axsl:if test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue!='codelistElement' and not(gmd:shortName)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:dataType/gmd:MD_DatatypeCode/@codeListValue!='codelistElement' and not(gmd:shortName)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:dataType is not equal to 'codelistElement' then gmd:shortName is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M29"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M29"/>
	<axsl:template match="@*|node()" priority="-2" mode="M29">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M29"/>
	</axsl:template>
	<!--PATTERN MD_Georectified-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">MD_Georectified</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_Georectified" priority="1000" mode="M30">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_Georectified"/>-->
		<!--REPORT -->
		<axsl:if test="(gmd:checkPointAvailability/gco:Boolean='1' or gmd:checkPointAvailability/gco:Boolean='true') and not(gmd:checkPointDescription)">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="(gmd:checkPointAvailability/gco:Boolean='1' or gmd:checkPointAvailability/gco:Boolean='true') and not(gmd:checkPointDescription)">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>If gmd:checkPointAvailability = '1' or 'true' then gmd:checkPointDescription is mandatory.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M30"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M30"/>
	<axsl:template match="@*|node()" priority="-2" mode="M30">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M30"/>
	</axsl:template>
	<!--PATTERN gmd:MD_DataIdentification/gmd:extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_DataIdentification/gmd:extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_DataIdentification/gmd:extent" priority="1000" mode="M31">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_DataIdentification/gmd:extent"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:EX_Extent/@id='boundingExtent'"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:EX_Extent/@id='boundingExtent'">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>One of the gmd:EX_Extent elements should have an attribute id = 'boundingExtent'.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M31"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M31"/>
	<axsl:template match="@*|node()" priority="-2" mode="M31">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M31"/>
	</axsl:template>
	<!--PATTERN gmd:MD_DataIdentification/gmd:extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_DataIdentification/gmd:extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_DataIdentification/gmd:extent" priority="1000" mode="M32">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_DataIdentification/gmd:extent"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/@id='boundingGeographicBoundingBox'"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/@id='boundingGeographicBoundingBox'">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>One of the gmd:EX_GeographicBoundingBox elements should have an attribute id = 'boundingGeographicBoundingBox'.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M32"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M32"/>
	<axsl:template match="@*|node()" priority="-2" mode="M32">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M32"/>
	</axsl:template>
	<!--PATTERN gmd:MD_DataIdentification/gmd:extent-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">gmd:MD_DataIdentification/gmd:extent</svrl:text>
	<!--RULE -->
	<axsl:template match="//gmd:MD_DataIdentification/gmd:extent" priority="1000" mode="M33">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//gmd:MD_DataIdentification/gmd:extent"/>-->
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/@id='boundingTemporalExtent'"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/@id='boundingTemporalExtent'">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>One of the gmd:EX_TemporalExtent elements should have an attribute id = 'boundingTemporalExtent'.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M33"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M33"/>
	<axsl:template match="@*|node()" priority="-2" mode="M33">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M33"/>
	</axsl:template>
	<!--PATTERN checkCodeList-->
	<!--RULE -->
	<axsl:template match="//*[@codeList]" priority="1000" mode="M34">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="//*[@codeList]"/>-->
		<axsl:variable name="codeListDoc" select="document(substring-before(@codeList,'#'))//gmx:CodeListDictionary[@gml:id = substring-after(current()/@codeList,'#')]"/>
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="$codeListDoc"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="$codeListDoc">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>Unable to find the specified codeList document or CodeListDictionary node. (Model after this example: codeList="http://www.ngdc.noaa.gov/metadata/published/xsd/schema/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode")</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<!--ASSERT -->
		<axsl:choose>
			<axsl:when test="@codeListValue = $codeListDoc/gmx:codeEntry/gmx:CodeDefinition/gml:identifier"/>
			<axsl:otherwise>
				<svrl:failed-assert xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="@codeListValue = $codeListDoc/gmx:codeEntry/gmx:CodeDefinition/gml:identifier">
					<axsl:attribute name="location">
						<axsl:apply-templates select="." mode="schematron-select-full-path"/>
					</axsl:attribute>
					<svrl:text>'<axsl:text/>
						<axsl:value-of select="@codeListValue"/>
						<axsl:text/>' codeListValue is not in the specified codeList.</svrl:text>
				</svrl:failed-assert>
			</axsl:otherwise>
		</axsl:choose>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M34"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M34"/>
	<axsl:template match="@*|node()" priority="-2" mode="M34">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M34"/>
	</axsl:template>
	<!--PATTERN Report weird characters-->
	<svrl:text xmlns:svrl="http://purl.oclc.org/dsdl/svrl">Report weird characters</svrl:text>
	<!--RULE -->
	<axsl:template match="gco:*|gmd:LocalisedCharacterString" priority="1000" mode="M35">
		<!--<svrl:fired-rule xmlns:svrl="http://purl.oclc.org/dsdl/svrl" context="gco:*|gmd:LocalisedCharacterString"/>-->
		<!--REPORT -->
		<axsl:if test="contains(.,'“')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'“')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the “ smart quotes.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'”')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'”')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the ” smart quotes.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'‘')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'‘')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the ‘ smart quote.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'’')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'’')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the ’ smart quote.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'–')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'–')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the – dash.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'—')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'—')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the — em dash entity.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'®')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'®')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the ® registred trademark symbol.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'°')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'°')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the ° degree symbol.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<!--REPORT -->
		<axsl:if test="contains(.,'©')">
			<svrl:successful-report xmlns:svrl="http://purl.oclc.org/dsdl/svrl" test="contains(.,'©')">
				<axsl:attribute name="location">
					<axsl:apply-templates select="." mode="schematron-select-full-path"/>
				</axsl:attribute>
				<svrl:text>[1]Replace the © symbol.</svrl:text>
			</svrl:successful-report>
		</axsl:if>
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M35"/>
	</axsl:template>
	<axsl:template match="text()" priority="-1" mode="M35"/>
	<axsl:template match="@*|node()" priority="-2" mode="M35">
		<axsl:apply-templates select="*|comment()|processing-instruction()" mode="M35"/>
	</axsl:template>
</axsl:stylesheet>
