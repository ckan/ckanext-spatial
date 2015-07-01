<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/1999/xhtml" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:srv="http://www.isotc211.org/2005/srv" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml" xmlns:gml32="http://www.opengis.net/gml/3.2" exclude-result-prefixes="gmd gco srv xlink gml gml32">
	<xsl:output method="html" encoding="iso-8859-1" indent="yes" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>
	<!--
		<meta name="DC.creator" content="Peter Parslow"/>
		<meta name="DCTERMS.created" scheme="DCTERMS.W3CDTF" content="2011-05-12"/>
		<meta name="DC.description" content="This stylesheet transforms an ISO 19139 encoded metadata record into xHTML for human viewing. Specifically, it extracts the GEMINI 2.1 elements from the XML"/>
		<meta name="DC.publisher" content="Ordnance Survey GB"/>
		<meta name="DC.title" content="GEMINI viewing stylesheet"/>
		<meta name="eGMS.copyright" content="Crown copyright http://www.opsi.gov.uk/advice/crown-copyright/index.htm"/>
		<meta name="DC.rights" content="Open Government Licence http://www.nationalarchives.gov.uk/doc/open-government-licence/"/>
		<meta name="eGMS.status" content="draft 1.0b" />

Note 'double' GML namespace, so that this stylesheet works with whichever is in the input XML file
doesn't - at present - look values up in the various codelists: simply outputs the @codeListValue attribute, which is 'reasonably English'
doesn't deal with gco:nilReason
1.0b - James Gardner pointed out that Resource locator was missing; refactored a template for CI_OnlineResource based on what was there for Responsible Party's web address
-->
	<xsl:template match="/">
		<!-- HTML head/body, with standard metadata -->
		<html>
			<head>
				<title>GEMINI record about <xsl:value-of select="gmd:MD_Metadata/gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"/>
				</title>
				<meta name="DC.source">
					<xsl:attribute name="content">GEMINI metadata record with GUID: <xsl:value-of select="gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString"/></xsl:attribute>
				</meta>
				<meta name="DC.publisher">
					<xsl:attribute name="content"><xsl:value-of select="gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString"/></xsl:attribute>
				</meta>
				<meta name="DC.subject" scheme="eGMS.IPSV" content="metadata"/>
				<meta name="DC.language" scheme="DCTERMS.ISO639-2">
					<xsl:attribute name="content"><xsl:value-of select="gmd:MD_Metadata/gmd:language/gmd:LanguageCode/@codeListValue"/></xsl:attribute>
				</meta>
				<!-- insert the required CSS stylesheet in here -->
				<!-- e.g. http://intranet.ordsvy.gov.uk/intranet/css/style.css; http://www.ordnancesurvey.co.uk/oswebsite/a/css/global/screen.css; http://location.defra.gov.uk/wp-content/themes/uklocation2/style.css; http://data.gov.uk/sites/default/files/css/css_523a702a5fae8f07ad6cce1f9cf4efce.css -->
				<!-- of these, data.gov.uk worked the best, because the h1 was distinct - but the site has now changed. It would be better to have the h2,h3,h4,h5 as left aligned, with the p to the right & on the same line - perhaps divs? with a few classes? perhaps (dare I say it?) as tables, with the element name in the left column, value in the right? -->
		<!--Removed, as link is broken & css lost		<link rel="stylesheet" href="/css/css_523a702a5fae8f07ad6cce1f9cf4efce.css" type="text/css" media="screen"/> -->
			</head>
			<body>
				<xsl:apply-templates select="gmd:MD_Metadata"/>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="gmd:MD_Metadata">
		<!-- the meat of the ISO 19139 / GEMINI transformation -->
		<!-- the idea is to use few HTML tags: h1 through h5, p, a - so that CSS can be applied -->
		<h1>Identification</h1>
		<h2 title="INSPIRE Resource title">Title</h2>
		<p title="Title">
			<xsl:value-of select="gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"/>
		</p>
		<xsl:if test="gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:alternateTitle">
			<h2 title="not in INSPIRE">Alternative title(s)</h2>
			<xsl:for-each select="gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:alternateTitle">
				<p title="Alternative title">
					<xsl:value-of select="gco:CharacterString"/>
				</p>
			</xsl:for-each>
		</xsl:if>
		<h2 title="INSPIRE Resource abstract">Abstract</h2>
		<p title="Abstract">
			<xsl:value-of select="gmd:identificationInfo/*/gmd:abstract/gco:CharacterString"/>
		</p>
		<h2 title="INSPIRE Resource type">Resource type</h2>
		<p title="Resource type">
			<xsl:value-of select="gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue"/>
		</p>
		<!-- new in 1.0b -->
		<h2 title="INSPIRE Resource locator">Resource locator</h2>
		<p title="Resource locator">
			<xsl:apply-templates select="gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:onLine/gmd:CI_OnlineResource"/>
		</p>
		<!-- end of addition -->
		<h2 title="INSPIRE Unique resource identifier">Unique resource identifier</h2>
		<h3 title="INSPIRE code">code</h3>
		<p title="Unique resource identifier: code">
			<xsl:value-of select="gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:identifier/*/gmd:code/gco:CharacterString"/>
		</p>
		<h3 title="INSPIRE namespace">codeSpace</h3>
		<p title="Unique resource identifier: namespace">
			<xsl:value-of select="gmd:identificationInfo/*/ gmd:citation/gmd:CI_Citation/gmd:identifier/*/gmd:codeSpace/gco:CharacterString"/>
		</p>
		<xsl:if test="gmd:identificationInfo/srv:SV_ServiceIdentification">
			<h2 title="INSPIRE Coupled resource">Coupled resource</h2>
			<xsl:for-each select="gmd:identificationInfo/srv:SV_ServiceIdentification/srv:operatesOn">
				<p title="Coupled resource">
					<xsl:value-of select="@xlink:href"/>
				</p>
			</xsl:for-each>
		</xsl:if>
		<h2 title="INSPIRE Resource language">Dataset language</h2>
		<p title="Dataset language">
			<xsl:value-of select="gmd:identificationInfo/*/gmd:language/gmd:LanguageCode/@codeListValue"/>
		</p>
		<h2 title="not in INSPIRE">Spatial reference system</h2>
		<xsl:if test="gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace">
			<h3 title="not in INSPIRE">authority code</h3>
			<p title="Spatial reference system: authority code">
				<xsl:value-of select="gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString"/>
			</p>
		</xsl:if>
		<h3 title="not in INSPIRE">code identifying the spatial reference system</h3>
		<p title="Spatial reference system: code identifying the spatial reference system">
			<xsl:value-of select="gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/gmd:code/gco:CharacterString"/>
		</p>
		<xsl:if test="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:supplementalInformation">
			<h2 title="not in INSPIRE">Additional information source</h2>
			<p title="Additional information source">
				<xsl:value-of select="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:supplementalInformation/gco:CharacterString"/>
			</p>
		</xsl:if>
		<!-- section break -->
		<h1>Classification of spatial data and services</h1>
		<h2 title="INSPIRE Topic category">Topic category</h2>
		<xsl:for-each select="gmd:identificationInfo/*/gmd:topicCategory">
			<p title="Topic category">
				<xsl:value-of select="gmd:MD_TopicCategoryCode"/>
			</p>
		</xsl:for-each>
		<xsl:if test="gmd:identificationInfo/srv:SV_ServiceIdentification">
			<h2 title="INSPIRE Spatial data service type">Spatial data service type</h2>
			<p title="Spatial data service type">
				<xsl:value-of select="gmd:identificationInfo/srv:SV_ServiceIdentification/srv:serviceType/gco:LocalName"/>
			</p>
		</xsl:if>
		<!-- section break -->
		<h1>Keywords</h1>
		<xsl:for-each select="gmd:identificationInfo/*/*/gmd:MD_Keywords">
			<h2>Keyword set</h2>
			<h3 title="INSPIRE Keyword value">keyword value</h3>
			<xsl:for-each select="gmd:keyword">
				<p title="keyword value">
					<xsl:value-of select="gco:CharacterString"/>
				</p>
			</xsl:for-each>
			<xsl:if test="gmd:thesaurusName">
				<h3 title="INSPIRE Originating controlled vocabulary">originating controlled vocabulary</h3>
				<xsl:apply-templates select="gmd:thesaurusName/gmd:CI_Citation"/>
			</xsl:if>
		</xsl:for-each>
		<!-- section break -->
		<h1>Geographic location</h1>
		<h2 title="INSPIRE Geographic bounding box"/>
		<h3>West bounding longitude</h3>
		<p title="West bounding longitude">
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/ gmd:westBoundLongitude/gco:Decimal"/>
		</p>
		<h3>East bounding longitude</h3>
		<p title="East bounding longitude">
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/ gmd:eastBoundLongitude/gco:Decimal"/>
		</p>
		<h3>North bounding latitude</h3>
		<p title="North bounding latitude">
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/ gmd:northBoundLatitude/gco:Decimal"/>
		</p>
		<h3>South bounding latitude</h3>
		<p title="South bounding latitude">
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicBoundingBox/ gmd:southBoundLatitude/gco:Decimal"/>
		</p>
		<xsl:if test="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicDescription">
			<h2 title="Not in INSPIRE">Extent</h2>
			<xsl:for-each select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:geographicElement/gmd:EX_GeographicDescription">
				<h3>Extent group</h3>
				<h4>authority code</h4>
				<p title="Extent: authority">
					<xsl:apply-templates select="gmd:geographicIdentifier/gmd:MD_Identifier/gmd:authority/gmd:CI_Citation"/>
				</p>
				<h4>code identifying the extent</h4>
				<p title="Extent: code">
					<xsl:value-of select="gmd:geographicIdentifier/gmd:MD_Identifier/gmd:code/gco:CharacterString"/>
				</p>
			</xsl:for-each>
		</xsl:if>
		<xsl:if test="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent">
			<h2 title="Not in INSPIRE">Vertical extent information</h2>
			<h3>Minimum value</h3>
			<p title="Vertical extent: minimum value">
				<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:minimumValue/gco:Real"/>
			</p>
			<h3>Maximum value</h3>
			<p title="Vertical extent: maximum value">
				<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:maximumValue/gco:Real"/>
			</p>
			<h3>Coordinate reference system</h3>
			<!-- this doesn't handle much of an in-line CRS, but then although described in the Encoding Guide, they seem to go beyond GEMINI -->
			<h4>authority code</h4>
			<p title="Vertical extent: CRS authority">
				<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRS/gml:VerticalCRS/gml:identifier/@codeSpace|gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRS/gml32:VerticalCRS/gml32:identifier/@codeSpace"/>
			</p>
			<h4>code identifying the coordinate reference system</h4>
			<p title="Vertical extent: CRS authority">
				<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRS/@xlink:href|*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRS/gml:verticalCRS/gml:identifier|*/*/gmd:EX_Extent/gmd:verticalElement/gmd:EX_VerticalExtent/gmd:verticalCRS/gml32:verticalCRS/gml32:identifier"/>
			</p>
		</xsl:if>
		<!-- section break -->
		<h1>Temporal reference</h1>
		<h2 title="INSPIRE Temporal extent">Temporal extent</h2>
		<h3>Begin position</h3>
		<p>
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition|gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:beginPosition"/>
		</p>
		<h3>End position</h3>
		<p>
			<xsl:value-of select="gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition|gmd:identificationInfo/*/*/gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml32:TimePeriod/gml32:endPosition"/>
		</p>
		<h2 title="INSPIRE Date of publication/last revision/creation">Dataset reference date</h2>
		<xsl:apply-templates select="gmd:identificationInfo/*/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date"/>
		<h2 title="not in INSPIRE">Frequency of update</h2>
		<p title="Frequency of update">
			<xsl:value-of select="gmd:identificationInfo/*/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode/@codeListValue"/>
		</p>
		<!-- section break -->
		<xsl:if test="gmd:identificationInfo/gmd:MD_DataIdentification">
			<!-- these elements are not available for services -->
			<h1>Quality and validity</h1>
			<h2 title="INSPIRE Lineage">Lineage</h2>
			<p title="Lineage">
				<xsl:value-of select="gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:lineage/gmd:LI_Lineage/gmd:statement/gco:CharacterString"/>
			</p>
			<xsl:if test="*/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance">
				<h2 title="INSPIRE Spatial resolution">Spatial resolution</h2>
				<p title="Spatial resolution (in metres)">
					<xsl:value-of select="*/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance"/> metres</p>
			</xsl:if>
			<xsl:if test="*/gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale">
				<h2 title="INSPIRE Spatial resolution">Equivalent scale</h2>
				<p title="Equivalent scale">1:<xsl:value-of select="*/gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer"/>
				</p>
			</xsl:if>
		</xsl:if>
		<!-- section break -->
		<h1>Conformity</h1>
		<xsl:for-each select="gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult">
			<h2>Conformity report</h2>
			<h3 title="INSPIRE Specification">specification</h3>
			<p title="Conformity: specification">
				<xsl:apply-templates select="gmd:specification/gmd:CI_Citation"/>
			</p>
			<h3 title="INSPIRE Degree">degree</h3>
			<p title="Conformity: degree">
				<xsl:value-of select="gmd:pass/gco:Boolean"/>
			</p>
			<h3 title="not in INSPIRE">explanation</h3>
			<p title="Conformity: explanation">
				<xsl:value-of select="gmd:explanation/gco:CharacterString"/>
			</p>
		</xsl:for-each>
		<h2 title="not in INSPIRE">Data format</h2>
		<h3>name of format</h3>
		<p title="Data format: name">
			<xsl:value-of select="gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:name/gco:CharacterString"/>
		</p>
		<h3>version of format</h3>
		<p title="Data format: version">
			<xsl:value-of select="gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/gmd:MD_Format/gmd:version/gco:CharacterString"/>
		</p>
		<!-- section break -->
		<h1>Constraints related to access and use</h1>
		<xsl:for-each select="gmd:identificationInfo/*/gmd:resourceConstraints">
			<h2>Constraint set</h2>
			<xsl:if test="*/gmd:useLimitation">
				<h3 title="INSPIRE conditions applying to access and use">Use constraints</h3>
				<p title="Use constraints">
					<xsl:value-of select="*/gmd:useLimitation/gco:CharacterString"/>
				</p>
			</xsl:if>
			<xsl:if test="*/gmd:otherConstraints">
				<h3 title="INSPIRE Limitations on public access">Limitations on public access</h3>
				<p title="Limitations on public access">
					<xsl:value-of select="*/gmd:otherConstraints/gco:CharacterString "/>
				</p>
			</xsl:if>
		</xsl:for-each>
		<!-- section break -->
		<h1>Responsible organisations</h1>
		<xsl:for-each select="gmd:identificationInfo/*/gmd:pointOfContact">
			<h2 title="INSPIRE Responsible party and Responsible party role">Responsible party</h2>
			<xsl:apply-templates select="gmd:CI_ResponsibleParty"/>
		</xsl:for-each>
		<!-- section break -->
		<h1>Metadata on metadata</h1>
		<h2 title="INSPIRE Metadata point of contact">Metadata point of contact</h2>
		<p title="Metadata point of contact">
			<xsl:apply-templates select="gmd:contact/gmd:CI_ResponsibleParty"/>
		</p>
		<h2 title="INSPIRE Metadata date">Metadata date</h2>
		<p title="Metadata date">
			<xsl:value-of select="gmd:dateStamp/gco:Date|gmd:dateStamp/gco:DateTime"/>
		</p>
		<h2 title="INSPIRE Metadata language">Metadata language</h2>
		<xsl:value-of select="gmd:language/gmd:LanguageCode/@codeListValue"/>
	</xsl:template>
	<!-- templates used from multiple places -->
	<xsl:template match="gmd:CI_Citation">
		<!-- not for the main citation of the dataset, which is handled in rather more detail -->
		<h4 title="INSPIRE title">title</h4>
		<xsl:value-of select="gmd:title/gco:CharacterString"/>
		<h4 title="INSPIRE reference date">reference date</h4>
		<xsl:apply-templates select="gmd:date/gmd:CI_Date"/>
	</xsl:template>
	<xsl:template match="gmd:CI_Date">
		<!-- citation dates in general, including the main citation date of the dataset -->
		<h5>date type</h5>
		<p title="date type">
			<xsl:value-of select="gmd:dateType/gmd:CI_DateTypeCode/@codeListValue"/>
		</p>
		<h5>effective date</h5>
		<p title="effective date">
			<xsl:value-of select="gmd:date/gco:Date|gmd:date/gco:DateTime"/>
		</p>
	</xsl:template>
	<!-- 1.0b change; refactored from being specific to Responsible Party Contact info -->
	<xsl:template match="gmd:CI_OnlineResource">
		<xsl:variable name="URL" select="gmd:linkage/gmd:URL"/>
		<p>
			<a>
				<xsl:attribute name="href"><xsl:value-of select="$URL"/></xsl:attribute>
				<xsl:value-of select="$URL"/>
			</a>
		</p>
		<!-- additional at 1.0b -->
		<xsl:if test="gmd:protocol">
			<p title="Online resource: protocol">protocol: <xsl:apply-templates select="gmd:protocol"/>
			</p>
		</xsl:if>
		<xsl:if test="gmd:applicationProfile">
			<p title="Online resource: applicationProfile">applicationProfile: <xsl:apply-templates select="gmd:applicationProfile"/>
			</p>
		</xsl:if>
		<xsl:if test="gmd:name">
			<p title="Online resource: name">name: <xsl:apply-templates select="gmd:name"/>
			</p>
		</xsl:if>
		<xsl:if test="gmd:description">
			<p title="Online resource: description">description: <xsl:apply-templates select="gmd:description"/>
			</p>
		</xsl:if>
		<xsl:if test="gmd:function">
			<p title="Online resource: function">function: <xsl:apply-templates select="gmd:function"/>
			</p>
		</xsl:if>
	</xsl:template>
	<xsl:template match="gmd:CI_OnLineFunctionCode">
		<xsl:value-of select="@codeListValue"/>
	</xsl:template>
	<!-- end of 1.0b change -->
	<xsl:template match="gmd:CI_ResponsibleParty">
		<!-- used for the Responsible Party and the Metadata Point of Contact -->
		<xsl:if test="gmd:positionName">
			<h5>contact position</h5>
			<p>
				<xsl:value-of select="gmd:positionName/gco:CharacterString"/>
			</p>
		</xsl:if>
		<h5>organisation name</h5>
		<p>
			<xsl:value-of select="gmd:organisationName/gco:CharacterString"/>
		</p>
		<xsl:if test="gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:city">
			<!-- difficult to decide which element is indicative, given that email address is in there too, and mandatory -->
			<h5>full postal address</h5>
			<xsl:apply-templates select="gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address"/>
		</xsl:if>
		<xsl:if test="gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice">
			<h5>telephone number</h5>
			<p>
				<xsl:value-of select="gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString"/>
			</p>
		</xsl:if>
		<xsl:if test="gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile">
			<h5>facsimile number</h5>
			<p>
				<xsl:value-of select="gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile/gco:CharacterString"/>
			</p>
		</xsl:if>
		<h5>email address</h5>
		<xsl:variable name="email" select="gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString"/>
		<p>
			<a>
				<xsl:attribute name="href">mailto:<xsl:value-of select="$email"/></xsl:attribute>
				<xsl:value-of select="$email"/>
			</a>
		</p>
		<xsl:if test="gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource">
			<h5>web address</h5>
			<!-- 1.0b change - part of the contents of this template used to be in line here -->
			<xsl:apply-templates select="gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource"/>
			<!-- end of 1.0b change -->
		</xsl:if>
		<h5>responsible party role</h5>
		<p>
			<xsl:value-of select="gmd:role/gmd:CI_RoleCode/@codeListValue"/>
		</p>
	</xsl:template>
	<!-- two templates used from CI_ResponsibleParty, above -->
	<xsl:template match="gmd:CI_Address">
		<!-- just to ensure that the email address doesn't go out in the postal address block -->
		<xsl:apply-templates select="gmd:deliveryPoint|gmd:city|gmd:AdministrativeArea|gmd:postalCode|gmd:country"/>
	</xsl:template>
	<xsl:template match="gmd:deliveryPoint|gmd:city|gmd:AdministrativeArea|gmd:postalCode|gmd:country">
		<p>
			<xsl:value-of select="gco:CharacterString"/>
		</p>
	</xsl:template>
</xsl:stylesheet>
