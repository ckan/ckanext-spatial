<?xml version="1.0" encoding="utf-8" ?>

<!-- ========================================================================================== -->
<!-- Schematron Schema for the MEDIN Disovery Metadata Profile                                  -->
<!-- ========================================================================================== -->

<!-- 
     James Rapaport                                
     SeaZone Solutions Limited                                                  
     2009-10-20                                                            

     This Schematron schema has been developed for the Marine Environmental Data and Information 
     Network (MEDIN) by SeaZone Solutions Limited (SeaZone).  It is designed to validate the 
     constraints introduced by the MEDIN Discovery Metadata Profile. The schema is provided 
     "as is," without warranty of any kind, express or implied.  Under no circumstances shall 
     MEDIN, SeaZone or any contributing parties be held liable for any damages arising in any 
     way from the use of this schema.  Further copyright and legal information is contained in 
     the schema manual. 
     
     The schema has been developed for XSLT Version 1.0 and tested with the ISO 19757-3 Schematron
     XML Stylesheets issued on 2009-03-18 at http://www.schematron.com/tmp/iso-schematron-xslt1.zip 
     
     The schema tests constraints on ISO / TS 19139 encoded metadata. The rules expressed in this 
     schema apply in addition to validation by the ISO / TS 19139 XML schemas.
     
     The schema is designed to test ISO 19139 encoded metadata incorporating ISO 19136 (GML Version
     3.2.1) elements where necessary. Note that GML elements must be mapped to the Version 3.2.1 
     GML namespace - http://www.opengis.net/gml/3.2
     
     Document History:
     
     2009-04-16 - Version 0.1
     First draft. Element 26 OAI Harvesting is not complete - awaiting confirmation on 
     encoding.
     
     2009-04-20 - Version 0.2
     Responsible party tests changed. Data and Originator points of contact are both encoded at 
     /*/gmd:identificationInfo/*/gmd:pointOfContact. Data point of contact has role = 'pointOfContact'. 
     Originator point of contact has role = 'originator'.
     
     2009-04-27 - Version 0.3
     GcoTypeTestPattern changed to test for uom attributes on the Length, Distance, Angle and Scale
     type. Original intention to add ISO / TC 19139 Table A.1 constraint tests to this schema dropped
     and alternatively creating tests for these constraints in a separate schema.
     
     2009-05-18 - Version 0.4
     Compliance with MEDIN Profile Version 2.3. Release for UAT.
     
     Element 10 - test for INSPIRE service type values implemented.
     Element 11 - Test for NERC Data Grid OAI Harvesting value implemented.
     Element 26 - OAI Harvesting place holder removed. Subsequent elements renumbered.
     LanguagePattern edited to allow for gmd:LanguageCode element.
     Element 12 and 13 - there can be srv:extent and gmd:extent. Tests changed to accommodate these
     namespaces.
     
     2009-10-18 - Version 1.0
     Compliance with MEDIN Profile Version 2.3.2. Release as Version 1.0.
     
     Element 13 - Extent is now optional
     Element 16.1 - Temporal Extent is now mandatory
     Element 16.2 - Date of publication is now mandatory
     Element 16.3 - Date of last revision is now optional
     Element 16.4 - Date of creation is now optional
     Element 17 - Lineage was originally coded as Mandatory but it should be conditional
     Element 18 - Spatial Resolution was originally coded as Mandatory but it should be conditional
                - More than one occurrence of spatial resolution allowed
     Element 22 - Roles of Responsible Party are now originator, custodian and distributor
     Element 22.2 - Changed from data point of contact to custodian
     Element 22.3 - Changed to Distributor point of contact
     Element 26 - Metadata date (name change from date of update of metadata
     
     2009-11-09 - Version 1.1
     Minor corrections
     
     Element 16 - Removed tests for publication date and temporal extent
     Element 16.1 - Change assertion text to describe faults where no temporal extent is provided
     Element 16.2 - Change assertion to test for one publication date
     
     2009-11-10 - Version 1.2
     
     Element 11 - Test for count of Keywords was failing. A metadata record could be created with only OAI 
                  Harvesting keyword and pass the test.
     Element 22 - Test for count of metadata contact. Changed text of assert so that it is clear that only
                  one metadata contact must be provided. This assert fails if 2+ metadata contacts are
                  provided but it would not have been clear to the user why the test was failing.
                  
     2009-12-07 - Version 1.3
     
     Changed version number in root element
     Remove spurious medin and mdmp namespace declarations
     
     2009-12-14 - Version 1.4
     
     Changed LanguagePattern so that the language code can be either in gmd:LanguageCode/@codeListValue
     or in gco:CharacterString. 
     
     2010-01-11 - Version 1.5
     
     Element 16   - Searching @codeListValue now not the element value
     Element 16.2 - Searching @codeListValue now not the element value
     Element 16.3 - Searching @codeListValue now not the element value
     Element 16.4 - Searching @codeListValue now not the element value
     
     2010-02-01 - Version 1.6
     All sch:report elements removed from the schema. These elements cause svrl:successful-report
     elements to be output in SVRL. oXygen 10.x interprets these elements as warnings while 11.1
     interprets them as errors. The intention in the context of this schema was that svrl:successful-report
     would be interpretted as information.
     
     Changes to bring the schema in to line with the MEDIN profile documentation - version 2.3.3 (2010-01-27)
     
     2010-02-16 - Version 1.7
     
     Changes following tests by Hannah Freeman:
     
     Element 13: Extent is optional but must be provided with controlled vocabulary details
     Element 22: Test for email address does not work if gmd:contactInfo is omitted
-->

<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt" schemaVersion="1.7">

  <sch:title>MEDIN Discovery Metadata Profile</sch:title>

  <sch:p>
    This Schematron schema is based on MEDIN_Schema_Documentation_2_3.doc. The text describing
    each metadata element has been extracted from this document. Reference has also been made to
    the INSPIRE Metadata Implementing Rules: Technical Guidelines based on EN ISO 19115 and EN ISO 19139
    which is available at:
  </sch:p>
  <sch:p>
    http://inspire.jrc.ec.europa.eu/reports/ImplementingRules/metadata/MD_IR_and_ISO_20090218.pdf
  </sch:p>

  <!-- Namespaces from ISO 19139 Metadata encoding -->
  <sch:ns prefix="gml" uri="http://www.opengis.net/gml/3.2" />
  <sch:ns prefix="gmd" uri="http://www.isotc211.org/2005/gmd"/>
  <sch:ns prefix="gco" uri="http://www.isotc211.org/2005/gco"/>
  <sch:ns prefix="gmx" uri="http://www.isotc211.org/2005/gmx"/>
  <sch:ns prefix="xlink" uri="http://www.w3.org/1999/xlink"/>

  <!-- Namespace for ISO 19119 - Metadata Describing Services -->
  <sch:ns prefix="srv" uri="http://www.isotc211.org/2005/srv"/>

  <!-- ========================================================================================== -->
  <!-- Concrete Patterns                                                                          -->
  <!-- ========================================================================================== -->

  <!-- ========================================================================================== -->
  <!-- Element 1 - Resource Title (M)                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResourceTitle">
    <sch:title>Element 1 - Resource Title (M)</sch:title>
    <sch:p>Mandatory element. Only one resource title allowed. Free text.</sch:p>
    <sch:p>
      The title is used to provide a brief and precise description of the dataset.
      The following format is recommended:
    </sch:p>
    <sch:p>
      'Date' 'Originating organization/programme' 'Location' 'Type of survey'.
      It is advised that acronyms and abbreviations are reproduced in full.
      Example: Centre for Environment, Fisheries and Aquaculture Science (Cefas).
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> 1992 Centre for Environment, Fisheries and Aquaculture Science (Cefas)
      North Sea 2m beam trawl survey.
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> 1980-2000 Marine Life Information Network UK
      (MarLIN) Sealife Survey records.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:citation/*/gmd:title) = 1">
        Resource Title is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinResourceTitleGcoTypeTest">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:citation/*/gmd:title"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 2 - Alternative Resource Title (O)                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinAlternativeResourceTitle">
    <sch:title>Element 2 - Alternative Resource Title (O)</sch:title>
    <sch:p>
      Optional element.  Multiple alternative resource titles allowed.  Free text.
    </sch:p>
    <sch:p>
      The alternative title is used to add the names by which a dataset may be known and may
      include short name, other name, acronym or alternative language title.
    </sch:p>
    <sch:p>Example</sch:p>
    <sch:p>
      1980-2000 MarLIN Volunteer Sighting records.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinAlternativeResourceTitleInnerText">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:citation/*//gmd:alternateTitle"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 3 - Resource Abstract (M)                                                          -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResourceAbstract">
    <sch:title>Element 3 - Resource Abstract (M)</sch:title>
    <sch:p>Mandatory element.  Only one resource abstract allowed.  Free text.</sch:p>
    <sch:p>
      The abstract should provide a clear and brief statement of the content of the resource.
      Include what has been recorded, what form the data takes, what purpose it was collected for,
      and any limiting information, i.e. limits or caveats on the use and interpretation of
      the data.  Background methodology and quality information should be entered into the
      Lineage element (element 10).  It is recommended that acronyms and abbreviations are
      reproduced in full. e.g. Centre for Environment, Fisheries and Aquaculture Science (Cefas).
    </sch:p>
    <sch:p>Examples</sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> Benthic marine species abundance data from an assessment
      of the cumulative impacts of aggregate extraction on seabed macro-invertebrate communities.
      The purpose of this study was to determine whether there was any evidence of a large-scale
      cumulative impact on benthic macro-invertebrate communities as a result of the multiple
      sites of aggregate extraction located off Great Yarmouth in the southern North Sea.
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> As part of the UK Department of Trade and Industry's (DTI's)
      ongoing sectorial Strategic Environmental Assessment (SEA) programme, a seabed survey
      programme (SEA2) was undertaken in May/June 2001 for areas in the central and southern
      North Sea UKCS.  This report summarizes the sediment total hydrocarbon and aromatic data
      generated from the analyses of selected samples from three main study areas:
    </sch:p>
    <sch:p>
      Area 1: the major sandbanks off the coast of Norfolk and Lincolnshire in the Southern North Sea (SNS);
    </sch:p>
    <sch:p>
      Area 2: the Dogger Bank in the SNS; and
    </sch:p>
    <sch:p>
      Area 3: the pockmarks in the Fladen Ground vicinity of the central North Sea (CNS).
    </sch:p>
    <sch:p>
      <sch:emph>Example 3:</sch:emph> Survey dataset giving port soundings in Great Yarmouth.
    </sch:p>
    <sch:p>
      <sch:emph>Example 4:</sch:emph> Conductivity, Temperature, Depth (CTD) grid survey in
      the Irish Sea undertaken in August 1981.  Only temperature profiles due to conductivity
      sensor malfunction.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:abstract) = 1">
        Resource Abstract is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinResourceAbstractGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:abstract"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 4 - Resource Type (M)                                                              -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResourceType">
    <sch:title>Element 4 - Resource Type (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurrence allowed.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      Identify the type of resource e.g. a dataset using the controlled vocabulary,
      MD_ScopeCode from ISO 19115.  (See Annex 2 for codelist).
      In order to comply with INSPIRE the resource type must be a dataset,
      a series (collection of datasets with a common specification) or a service.
    </sch:p>
    <sch:p>
      Example
    </sch:p>
    <sch:p>
      series
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:hierarchyLevel) = 1">
        Resource Type is mandatory. One occurrence is allowed.
      </sch:assert>
      <sch:assert test="contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'service')">
        Value of Resource Type must be dataset, series or service.
        Value of Resource Type is '<sch:value-of select="gmd:hierarchyLevel/*/@codeListValue"/>'
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 5 Resource Locator (C)                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResourceLocator">
    <sch:title>Element 5 - Resource Locator (C)</sch:title>
    <sch:p>Conditional element.  Multiple resource locators are allowed.  Free text.</sch:p>
    <sch:p>
      Formerly named online resource. If the resource is available online you must provide a
      web address (URL) that links to the resource.
    </sch:p>
    <sch:p>
      Schematron note: The condition cannot be tested with Schematron.
    </sch:p>
    <sch:p>Element 5.1 - Resource locator url (C)</sch:p>
    <sch:p>Conditional element.  Free text.</sch:p>
    <sch:p>The URL (web address).</sch:p>
    <sch:p>Element 5.2 - Resource locator name (O)</sch:p>
    <sch:p>Optional element.  Free text.</sch:p>
    <sch:p>The name of the web resource.</sch:p>
    <sch:p>Example</sch:p>
    <sch:p>
      Resource locator url:
      http://www.defra.gov.uk/marine/science/monitoring/merman.htm
      Resource locator name: The Marine Environment National Monitoring and Assessment Database
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:linkage) = 0 or 
                  (starts-with(gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:linkage/*, 'http://')  or 
                  starts-with(gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:linkage/*, 'https://') or 
                  starts-with(gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:linkage/*, 'ftp://'))">
        The value of resource locator does not appear to be a valid URL. It has a value of 
        '<sch:value-of select="gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:linkage/*"/>'
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinResouceLocatorGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:distributionInfo/*/gmd:transferOptions/*/gmd:onLine/*/gmd:name"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 6 Unique Resource Identifier (M)                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinUniqueResourceIdentifier">
    <sch:title>Element 6 - Unique Resource Identifier (M)</sch:title>
    <sch:p>
      Mandatory element (for datasets and series of datasets).  One occurrence allowed.  Free text.
    </sch:p>
    <sch:p>
      Provide a code uniquely identifying the resource. You may also specify a code space.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(gmd:identificationInfo/*/gmd:citation/*/gmd:identifier) = 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        If the Resource Type is dataset or series one Unique Resource Identifier must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Ensure that Unique Resource Identifier has a value -->
  <sch:pattern is-a="GcoTypeTestPattern" id="MedinUniqueResourceIdentifierGcoTypePattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:citation/*/gmd:identifier/*/gmd:code"/>
  </sch:pattern>

  <!-- Ensure that a code space value is provided if the element is encoded -->
  <sch:pattern is-a="GcoTypeTestPattern" id="MedinUniqueResourceIdentifierCodeSpaceGcoTypePattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:citation/*/gmd:identifier/*/gmd:codeSpace"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 7 Coupled Resource (C)                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinCoupledResource">
    <sch:title>Element 7 - Coupled Resource (C)</sch:title>
    <sch:p>
      Conditional element.  Mandatory if the datasets a service operates on are available.
      Multiple coupled resource occurrences allowed.
    </sch:p>
    <sch:p>
      An INSPIRE element referring to data services such as a data download or mapping
      web services.  It identifies the data resource(s) used by the service if these are
      available separately from the service.  You should supply the Unique resource identifiers
      of the relevent datasets (See element 6).
    </sch:p>
    <sch:p>Example</sch:p>
    <sch:p>MRMLN0000345</sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 8 Resource Language (C)                                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResourceLanguage">
    <sch:title>Element 8 - Resource Language (C)</sch:title>
    <sch:p>
      Conditional element.  Mandatory when the described resource contains textual information.
      Multiple resource languages allowed.  This element is not required if a service is being
      described rather than a dataset or series of datasets.  Controlled vocabulary, ISO 639-2.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(/*/gmd:identificationInfo/*/gmd:language) >= 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        If the Resource Type is dataset or series, Resource Language must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="LanguagePattern" id="MedinResourceLanguageLanguagePattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:language"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 9 Topic Category (C)                                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinTopicCategoryCode">
    <sch:title>Element 9 - Topic Category (C)</sch:title>
    <sch:p>
      Conditional element.  Mandatory for datasets and series of datasets.  Multiple topic
      categories are allowed.  This element is not required if a service is being described.
      Controlled vocabulary.
    </sch:p>
    <sch:p>
      This element is mandatory for INSPIRE and must be included, however, MEDIN will use the
      Keywords as these are more valuable to allow users to search for datasets.  This indicates
      the main theme(s) of the data resource.  It is required for INSPIRE compliance.  The relevant
      topic category should be selected from the ISO MD_TopicCategory list.  The full list can be
      found in Annex 4. Within MEDIN the parameter group keywords from the controlled vocabulary 
      P021 (BODC Parameter Discovery Vocabulary) available at
      http://vocab.ndg.nerc.ac.uk/client/vocabServer.jsp (included in element 11) 
      are mapped to the ISO Topic Categories so it is possible to generate the topic categories 
      automatically once the keywords from P021 have been selected.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(/*/gmd:identificationInfo/*/gmd:topicCategory) >= 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        If the Resource Type is dataset or series, one or more Topic Categories must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="MedinTopicCategoryCodeInnerText">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:topicCategory"/>
    <sch:param name="element" value="gmd:MD_TopicCategoryCode"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 10 Spatial Data Service Type (C)                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinSpatialDataServiceType">
    <sch:title>Element 10 - Spatial Data Service Type (C)</sch:title>
    <sch:p>
      Conditional element.  Mandatory if the described resource is a service.  One occurrence allowed.
    </sch:p>
    <sch:p>
      An element required by INSPIRE for metadata about data services e.g. web services1.  If a
      service is being described (from Element 4) it must be assigned a service type from the
      INSPIRE Service type codelist.  See Annex 5 for list.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'service')) and 
                  count(/*/gmd:identificationInfo/*/srv:serviceType) = 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series'))">
        If the Resource Type is service, one Spatial Data Service Type must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinSpatialDataServiceTypeGcoTypePattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/srv:serviceType"/>
  </sch:pattern>

  <sch:pattern fpi="MedinSpatialDataServiceTypeInspireList">
    <sch:rule context="/*/gmd:identificationInfo/*/srv:serviceType">
      <sch:assert test="contains(., 'discovery') or
                  contains(., 'view') or
                  contains(., 'download') or
                  contains(., 'transformation') or
                  contains(., 'invoke') or
                  contains(., 'other')">
        Service type must be one of 'discovery', 'view', 'download', 'transformation', 'invoke'
        or 'other' following INSPIRE generic names.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 11 Keywords (M)                                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinKeywords">
    <sch:title>Element 11 - Keywords (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple keywords allowed.  Controlled vocabularies.
    </sch:p>
    <sch:p>
      The entry should consist of two sub-elements the keywords and reference to the controlled
      vocabulary used as shown in the sub elements below.  To allow searching of the dataset 
      keywords should be chosen from at least one of 3 codelists.
    </sch:p>
    <sch:p>
      INSPIRE Keywords - A list of the INSPIRE theme keywords is available in Annex 9. 
      This list is also available at http://www.eionet.europa.eu/gemet/inspire_themes 
      At least one INSPIRE theme keyword is required for INSPIRE compliance.
    </sch:p>
    <sch:p>
      MEDIN Keywords - MEDIN mandates the use of the SeaDataNet Parameter Discovery Vocabulary 
      P021 to provide further ability to search by terms that are more related to the marine domain. 
      This list are available at http://vocab.ndg.nerc.ac.uk/client/vocabServer.jsp In particular 
      the parameter groups and codes that are used may be searched through a more user friendly 
      interface which has been built as part of the European funded SeaDataNet project at 
      http://seadatanet.maris2.nl/v_bodc_vocab/vocabrelations.aspx
    </sch:p>
    <sch:p>
      MEDIN also uses the SeaDataNet Parameter Discovery Vocabulary to provide further ability to search
      by terms that are more related to the marine domain.  This is available at:
      http://vocab.ndg.nerc.ac.uk/clients/getList?recordKeys=http://vocab.ndg.nerc.ac.uk/list/P021/current&amp;earliestRecord=&amp;submit=submit
    </sch:p>
    <sch:p>
      Vertical Extent Keywords - A mandatory vocabulary of keywords is available to describe 
      the vertical extent of the resource (e.g. data set). The vocabulary can be downloaded 
      as L131 at http://vocab.ndg.nerc.ac.uk/client/vocabServer.jsp and can also be seen in 
      Annex 9: This list is also available at: These lists are also available through a more 
      user friendly interface at http://seadatanet.maris2.nl/v_bodc_vocab/welcome.aspx/
    </sch:p>
    <sch:p>
      A mandatory vocabulary of keywords is available to describe the vertical extent of 
      the resource (e.g. data set). The vocabulary can be downloaded as L131 (Vertical Co-ordinate Coverages) at 
      http://vocab.ndg.nerc.ac.uk/client/vocabServer.jsp and can also be seen in Annex 9: 
      This list is also available at: These lists are also available through a more user 
      friendly interface at http://seadatanet.maris2.nl/v_bodc_vocab/welcome.aspx/
    </sch:p>
    <sch:p>
      Other vocabularies may be used as required as long as they follow the format specified in 11.1 – 11.2.3
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:descriptiveKeywords) - count(*/gmd:descriptiveKeywords/*/gmd:keyword[*='NDGO0001']) &gt;= 1">
        Keywords are mandatory.
      </sch:assert>
      <sch:assert test="count(*/gmd:descriptiveKeywords/*/gmd:thesaurusName) = 
                  count(*/gmd:descriptiveKeywords) - count(*/gmd:descriptiveKeywords/*/gmd:keyword[*='NDGO0001'])">
        Thesaurus Name is mandatory.
      </sch:assert>
      <sch:assert test="count(*/gmd:descriptiveKeywords/*/gmd:keyword[*='NDGO0001']) = 1">
        The NERC Data Grid OAI Harvesting keyword 'NGDO0001' must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 12 - Geographical Bounding Box (M)                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinGeographicBoundingBox">
    <sch:title>Element 12 - Geographical Bounding Box (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurrence of each sub-element allowed.  Numeric and controlled vocabulary.
    </sch:p>
    <sch:p>
      These four sub-elements represent the geographical bounding box of the resource's extent
      and should be kept as small as possible.  The co-ordinates of this bounding box should be
      expressed as decimal degrees longitude and latitude.  A minimum of two and a maximum of four
      decimal places should be provided.
    </sch:p>
    <sch:p>
      Latitudes between 0 and 90N, and longitudes between 0 and 180E should be expressed as positive
      numbers, and latitudes between 0 and 90S, and longitudes between 0 and 180W should be expressed
      as negative numbers.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="((contains(../gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(../gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(*/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox) = 1) or
                  contains(../gmd:hierarchyLevel/*/@codeListValue, 'service')">
        Geographic bounding box is mandatory. One shall be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GeographicBoundingBoxPattern" id="MedinGeographicBoundingBoxPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
               /*/gmd:identificationInfo/*/gmd:extent/*/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox'] |
               /*/gmd:identificationInfo/*/srv:extent/*/gmd:geographicElement/gmd:EX_GeographicBoundingBox |
               /*/gmd:identificationInfo/*/srv:extent/*/gmd:geographicElement/*[@gco:isoType='gmd:EX_GeographicBoundingBox']"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 13 Extent (O)                                                                      -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinExtent">
    <sch:title>Element 13 - Extent (O)</sch:title>
    <sch:p>
      Optional element.  Multiple occurrences of extents allowed.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      Keywords selected from controlled vocabularies to describe the spatial extent of the resource.  
      MEDIN strongly recommends the use of the SeaVox Sea Areas 
      (http://www.bodc.ac.uk/data/codes_and_formats/seavox/ 
      or e-mail enquiries@oceannet.org for further details) which is a managed vocabulary and has a 
      worldwide distribution. Other vocabularies available including ICES areas and rectangles 
      www.ices.dk , or Charting Progress 2 regions. may be used as long as they follow the format 
      specified in 13.1 – 13.2.3.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo/*/*/*/gmd:geographicElement/*/gmd:geographicIdentifier">
      <sch:assert test="count(*/gmd:authority) = 1">
        Extent vocabulary name is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinExtentCodeGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/*/*/gmd:geographicElement/*/gmd:geographicIdentifier/*/gmd:code"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinExtentAuthorityGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/*/*/gmd:geographicElement/*/gmd:geographicIdentifier/*/gmd:authority/*/gmd:title"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 14 - Vertical Extent Information (O)                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinVerticalExtentInformation">
    <sch:title>Element 14 - Vertical Extent Information (O)</sch:title>
    <sch:p>
      Optional element.  The vertical extent information should be filled in where the vertical
      co-ordinates are significant to the resource.  One occurrence allowed.  Numeric free text
      and controlled vocabulary.
    </sch:p>
    <sch:p>
      The vertical extent element has four sub-elements; the minimum vertical extent value, the
      maximum vertical extent value, the units and the coordinate reference system.  Depth
      below sea water surface should be a negative number.  Depth taken in the intertidal zone
      above the sea level should be positive.  If the dataset covers from the intertidal to the
      subtidal zone then the 14.1 should be used to record the highest intertidal point and 14.2
      the deepest subtidal depth.  Although the element itself is optional if it is filled in then
      its sub-elements are either mandatory or conditional.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinVerticalExtentInformationGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:extent/*/gmd:verticalElement/*/gmd:minimumValue |
               /*/gmd:identificationInfo/*/gmd:extent/*/gmd:verticalElement/*/gmd:maximumValue"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 15 - Spatial Reference System (M)                                                  -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinSpatialReferenceSystem">
    <sch:title>Element 15 - Spatial Reference System (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurrence allowed.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      Describes the system of spatial referencing (typically a coordinate reference system) used
      in the resource.  This should be derived from a controlled vocabulary.  The SeaDataNet list
      http://vocab.ndg.nerc.ac.uk/clients/getList?recordKeys=http://vocab.ndg.nerc.ac.uk/list/L101/current&amp;earliestRecord=&amp;submit=submit
      is recommended.  Please contact MEDIN if updates to this list are required.
      Do not guess if not known.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> WGS84
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> National Grid of Great Britain
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:referenceSystemInfo) = 1">
        Coordinate reference system information must be supplied.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinSpatialReferenceSystemGcoTypeTypePatternTest">
    <sch:param name="context" value="/*/gmd:referenceSystemInfo/*/gmd:referenceSystemIdentifier/*/gmd:code"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 16 - Temporal Reference (M)                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinTemporalReference">
    <sch:title>Element 16 - Temporal Reference (M)</sch:title>
    <sch:p>
      Mandatory element.  At least one of the sub-elements must be included.  One occurrence
      allowed of each sub element.  Date/Time format.
    </sch:p>
    <sch:p>
      It is recommended that all known temporal references of the resource are included. 
      The temporal extent of the resource (e.g. the period overwhich a data set covers) 
      and the date of publication (i.e. the date at which it was made publically available) 
      are mandatory.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:citation/*/gmd:date/*/gmd:dateType/*[@codeListValue='revision']) &lt;= 1">
        Only one revision date allowed.
      </sch:assert>
      <sch:assert test="count(*/gmd:citation/*/gmd:date/*/gmd:dateType/*[@codeListValue='creation']) &lt;= 1">
        Only one creation date allowed.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinTemporalReferenceGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:citation/*/gmd:date/*/gmd:date"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 16.1 - Temporal Extent (M)                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinTemporalExtent">
    <sch:title>Element 16.1 - Temporal Extent (M)</sch:title>
    <sch:p>
      Mandatory Element. One occurrence allowed. Date or Date/Time format.
    </sch:p>
    <sch:p>
      This describes the start and end date of the resource e.g. survey, and should be included
      where known.  You should include both a start and end date.  It is recommended that a full
      date including year, month and day is added, but it is accepted that for some historical
      resources only vague dates (year only, year and month only) are available.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="((contains(../gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(../gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(*/gmd:extent/*/gmd:temporalElement) = 1) or
                  contains(../gmd:hierarchyLevel/*/@codeListValue, 'service')">
        Temporal extent is mandatory for datasets and series. One must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 16.2 - Date of Publication (M)                                                     -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDateOfPublication">
    <sch:title>Element 16.2 - Date of Publication (M)</sch:title>
    <sch:p>
      Mandatory element.  Complete if known.  One occurrence allowed.  Date/Time format.
    </sch:p>
    <sch:p>
      This describes the publication date of the resource and should be included where known.
      If the resource is previously unpublished please use the date that the resource was made
      publically available via the MEDIN network.  It is recommended that a full date including
      year, month and day is added, but it is accepted that for some historical resources only
      vague dates (year only, year and month only) are available.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:citation/*/gmd:date/*/gmd:dateType[*/@codeListValue='publication']) = 1">
        Publication date is mandatory. One must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 16.3 - Date of Last Revision (O)                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDateOfLastRevision">
    <sch:title>Element 16.3 - Date of Last Revision (O)</sch:title>
    <sch:p>
      Optional element.  Complete if known.  One occurrence allowed.  Date/Time format.
    </sch:p>
    <sch:p>
      This describes the most recent date that the resource was revised.  It is recommended that a
      full date including year, month and day is added.
    </sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 16.4 - Date of Creation (O)                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDateOfCreation">
    <sch:title>Element 16.4 - Date of Creation (O)</sch:title>
    <sch:p>
      Optional element.  Complete if known.  One occurrence allowed.  Date/Time format.
    </sch:p>
    <sch:p>
      This describes the most recent date that the resource was created.  It is recommended that
      a full date including year, month and day is added.
    </sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 17 - Lineage (C)                                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinLineage">
    <sch:title>Element 17 - Lineage (C)</sch:title>
    <sch:p>
      Mandatory element for datasets or series of datasets.  One occurrence allowed.  This Element
      is not required if a service is being described.  Free text.
    </sch:p>
    <sch:p>
      Lineage includes the background information, history of the sources of data used and can
      include data quality statements.  The lineage element can include information about: source
      material; data collection methods used; data processing methods used; quality control
      processes.  Please indicate any data collection standards used.  Additional information
      source to record relevant references to the data e.g reports, articles, website.
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> This dataset was collected by the Fisheries Research Services and
      provided to the British Oceanographic Data Centre for long term archive and management.
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> (no protocols or standards used)- Forty 0.1m2 Hamon grab samples were collected
      from across the region, both within and beyond the extraction area, and analyzed for macrofauna
      and sediment particle size distribution in order to produce a regional description of the status
      of the seabed environment.  Samples were sieved over a 1mm mesh sieve.  In addition, the data
      were analyzed in relation to the area of seabed impacted by dredging over the period 1993-1998.
      Areas subject to 'direct' impacts were determined through reference to annual electronic records of
      dredging activity and this information was then used to model the likely extent of areas potentially
      subject to 'indirect' ecological and geophysical impact.
    </sch:p>
    <sch:p>
      <sch:emph>Example 3:</sch:emph> (collected using protocols and standards) - Data was collected
      using the NMMP data collection, processing and Quality Assurance SOPs and complies to MEDIN
      data standards.
    </sch:p>
    <sch:p>
      <sch:emph>Example 4:</sch:emph> Survey data from MNCR lagoon surveys were used to create a
      GIS layer of the extent of saline lagoons in the UK that was ground-truthed using 2006-2008
      aerial coastal photography obtained from the Environment Agency and site visits to selected
      locations.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(gmd:dataQualityInfo/*/gmd:lineage/*/gmd:statement) = 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        Lineage is mandatory for datasets and series of datasets.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinLineageGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:lineage/*/gmd:statement"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 18 - Spatial Resolution (C)                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinSpatialResolution">
    <sch:title>Element 18 - Spatial Resolution (C)</sch:title>
    <sch:p>
      Mandatory element for datasets and series of datasets.  Multiple occurrences allowed. 
      Numeric (positive whole number) and free text.
    </sch:p>
    <sch:p>
      Provides an indication of the spatial resolution of the data; i.e. how accurate 
      the spatial positions are likely to be.  An approximate value may be given.
    </sch:p>
    <sch:p>
      Spatial resolution may be presented as a distance measurement, in which case 
      the units must be provided, or an equivalent scale. The equivalent scale is 
      presented as a positive integer and only the denominator is encoded (e.g. 
      1:50,000 is encoded as 50000).
    </sch:p>
    <sch:p>
      GEMINI2 mandates the use of a distance measurement to express the spatial 
      resolution. MEDIN is in discussions with GEMINI and ISO to allow the use 
      of scale for this element.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="((contains(gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(gmd:identificationInfo/*/gmd:spatialResolution) &gt;= 1) or 
                  (contains(gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        Spatial resolution is mandatory for datasets and series of datasets.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDistanceGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:spatialResolution/*/gmd:distance"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinEquivalentScaleGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:spatialResolution/*/gmd:equivalentScale/*/gmd:denominator"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 19 - Additional Information Source (O)                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinAdditionalInformationSource">
    <sch:title>Element 19 - Additional Information Source (O)</sch:title>
    <sch:p>
      Optional element.  Multiple occurrences allowed.  Free text.
    </sch:p>
    <sch:p>
      Any references to external information that are considered useful, e.g. project website,
      report, journal article may be recorded.  It should not be used to record additional
      information about the resource.
    </sch:p>
    <sch:p>
      Example
    </sch:p>
    <sch:p>
      Malthus, T.J., Harries, D.B., Karpouzli, E., Moore, C.G., Lyndon, A.R., Mair, J.M.,
      Foster-Smith, B.,Sotheran, I. and Foster-Smith, D. (2006). Biotope mapping of the
      Sound of Harris, Scotland. Scottish Natural Heritage Commissioned Report No. 212
      (ROAME No. F01AC401/2).
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinAdditionalInformationSourceGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:supplementalInformation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 20 - Limitations on Public Access (M)                                              -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinLimitationsOnPublicAccess">
    <sch:title>Element 20 - Limitations on Public Access (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple occurrences allowed.  Controlled vocabulary and free text.
    </sch:p>
    <sch:p>
      This element describes any restrictions imposed on the resource for security and other
      reasons using the controlled ISO vocabulary RestrictionCode (See Annex 6).  If restricted
      or otherRestrictions is chosen please provide information on any limitations to access of
      resource and the reasons for them.  If there are no limitations on public access, this must
      be indicated.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> accessConstraints:
    </sch:p>
    <sch:p>
      otherRestrictions: No restrictions to public access
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> accessConstraints:
    </sch:p>
    <sch:p>
      otherRestrictions: Restricted public access, only available at 10km resolution.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:resourceConstraints/*/gmd:accessConstraints) +
                  count(*/gmd:resourceConstraints/*/gmd:otherConstraints) +
                  count(*/gmd:classification/*/gmd:resourceConstraints/*/gmd:classification) &gt;= 1">
        Limitations on Public Access is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinOtherConstraintsInnerTextPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:resourceConstraints/*/gmd:otherConstraints"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 21 - Conditions for Access and Use Constraints (M)                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinConditionsForAccessAndUseConstraints">
    <sch:title>Element 21 - Conditions for Access and Use Constraints (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple occurrences allowed.  Free text.
    </sch:p>
    <sch:p>
      This element describes any restrictions and legal restraints on using the data.  
      Any known constraints such as fees should be identified.  If no conditions 
      apply, then “no conditions apply” should be recorded.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> Data is freely available for research or commercial use
      providing that the originators are acknowledged in any publications produced.
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> Data is freely available for use in teaching and conservation
      but permission must be sought for use if the data will be reproduced in full or part or if
      used in any analyses.
    </sch:p>
    <sch:p>
      <sch:emph>Example 3:</sch:emph> Not suitable for use in navigation.
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:resourceConstraints/*/gmd:useLimitation) &gt;= 1">
        Conditions for Access and Use Constraints is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinConditionsForAccessAndUseConstraintsGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:resourceConstraints/*/gmd:useLimitation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 22 - Responsible Party (M)                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinResponsibleParty">
    <sch:title>Element 22 - Responsible Party (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple occurrences are allowed for some responsible party roles.
      Must include minimum of person/organization name and email address.  Free text and
      controlled vocabulary.
    </sch:p>
    <sch:p>
      Provides a description of an organization or person who has a role for the dataset 
      or resource. A full list of roles is available in Annex 7. MEDIN mandates that 
      the roles of 'Originator' and 'Custodian' (data holder) and the role of 'Distributor' 
      should be entered if different to the Custodian. The ‘Metadata point of contact’ 
      is also mandatory. Other types of responsible party may be specified from the 
      controlled vocabulary (see Annex 7 for codelist) if desired.
    </sch:p>
    <sch:p>
      If the data has been lodged with a MEDIN apprroved Data Archive Centre then 
      the DAC should be specified as the Custodian.
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:contact) = 1">
        Metadata point of contact is a mandatory element. Only one must be provided 
        while <sch:value-of select="count(gmd:contact)"/> elements are provided.
      </sch:assert>
    </sch:rule>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="count(*/gmd:pointOfContact) &gt;= 1">
        Point of Contact is a mandatory element.
      </sch:assert>
      <sch:assert test="count(*/gmd:pointOfContact/*/gmd:role/*[@codeListValue = 'originator']) &gt;= 1">
        Originator point of contact is a mandatory element. At least one must be provided.
      </sch:assert>
      <sch:assert test="count(*/gmd:pointOfContact/*/gmd:role/*[@codeListValue = 'custodian']) &gt;= 1">
        Custodian point of contact is a mandatory element. At least one must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 22.1 - Originator Point of Contact (M)                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinOriginatorPointOfContact">
    <sch:title>Element 22.1 - Originator Point of Contact (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple occurrences of originators allowed.  Must include
      minimum of person/organization name and email address.
    </sch:p>
    <sch:p>
      Person(s) or organization(s) who created the resource.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="MedinOriginatorPointOfContactResponsiblePartyPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:pointOfContact[*/gmd:role/*/@codeListValue = 'originator']"/>
    <sch:param name="countTest" value="count(*/gmd:contactInfo/*/gmd:address/*/gmd:electronicMailAddress) &gt;= 1"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 22.2 - Custodian Point of Contact (M)                                                   -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinCustodianPointOfContact">
    <sch:title>Element 22.2 - Custodian Point of Contact (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple occurrences of custodians allowed.  Must include 
      minimum of person/organization name and email address.
    </sch:p>
    <sch:p>
      Person(s) or organization(s) that accept responsibility for the data and 
      ensures appropriate case and maintenance. If the datset has been lodged 
      with a Data Archive Centres then this should be entered.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="MedinCustodianPointOfContactResponsiblePartyPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:pointOfContact[*/gmd:role/*/@codeListValue = 'custodian']"/>
    <sch:param name="countTest" value="count(*/gmd:contactInfo/*/gmd:address/*/gmd:electronicMailAddress) &gt;= 1"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 22.3 - Distributor Point of Contact (C)                                            -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDistributorPointOfContact">
    <sch:title>Element 22.3 - Distributor Point of Contact (C)</sch:title>
    <sch:p>
      Conditional element.  Multiple occurrences of originators allowed.  Must include minimum 
      of person/organization name and email address.
    </sch:p>
    <sch:p>
      Person(s) or organization(s) that distributes the resource.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="MedinDistributorPointOfContactResponsiblePartyPattern">
    <sch:param name="context" value="/*/gmd:distributionInfo/*/gmd:distributor/*/gmd:distributorContact[*/gmd:role/*/@codeListValue = 'distributor']"/>
    <sch:param name="countTest" value="count(*/gmd:contactInfo/*/gmd:address/*/gmd:electronicMailAddress) &gt;= 1"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 22.4 - Metadata Point of Contact (M)                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinMetadataPointOfContact">
    <sch:title>Element 22.3 - Metadata Point of Contact (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurence allowed.  Must include minimum of
      person/organization name and email address.
    </sch:p>
    <sch:p>
      Person or organization with responsibility for the maintenance of the metadata for the resource.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="ResponsiblePartyPattern" id="MedinMetadataPointOfContactResponsiblePartyPattern">
    <sch:param name="context" value="/*/gmd:contact"/>
    <sch:param name="countTest" value="count(*/gmd:contactInfo/*/gmd:address/*/gmd:electronicMailAddress) &gt;= 1"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 23 - Data Format (O)                                                               -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDataFormat">
    <sch:title>Element 23 - Data Format (O)</sch:title>
    <sch:p>
      Optional element.  Multiple data formats are allowed.  Free text.
    </sch:p>
    <sch:p>
      Indicate the formats in which digital data can be provided for transfer.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      ESRI Shapefiles
    </sch:p>
    <sch:p>
      Comma Separated Value (.csv) file
    </sch:p>
    <sch:p>
      Tiff image files
    </sch:p>
    <sch:p>
      MPEG video files
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDataFormatNameGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:resourceFormat/*/gmd:name"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDataFormatVersionGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:resourceFormat/*/gmd:version"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 24 - Frequency of Update (C)                                                       -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinFrequencyOfUpdate">
    <sch:title>Element 24 - Frequency of Update (C)</sch:title>
    <sch:p>
      Mandatory for datasets and series of datasets, Conditional for services.  
      One occurrence allowed.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      This describes the frequency that the resource (data set) is modified 
      or updated and should be included if known.  For example if the data 
      set is from a monitoring programme which samples once per year then 
      the frequency is annually. Select one option from ISO frequency of 
      update codelist (MD_FrequencyOfUpdate codelist).  The full code list 
      is presented in Annex 8.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> monthly
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> annually
    </sch:p>
    <sch:rule context="/*/gmd:identificationInfo">
      <sch:assert test="((contains(../gmd:hierarchyLevel/*/@codeListValue, 'dataset') or 
                  contains(../gmd:hierarchyLevel/*/@codeListValue, 'series')) and 
                  count(*/gmd:resourceMaintenance/*/gmd:maintenanceAndUpdateFrequency) = 1) or 
                  (contains(../gmd:hierarchyLevel/*/@codeListValue, 'service'))">
        Frequency of update is mandatory for datasets and series. One must be provided.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="MedinFrequencyOfUpdateInnerTextPattern">
    <sch:param name="context" value="/*/gmd:identificationInfo/*/gmd:resourceMaintenance/*/gmd:maintenanceAndUpdateFrequency"/>
    <sch:param name="element" value="*/@codeListValue"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 25 - INSPIRE Conformity (C)                                                        -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinInspireConformity">
    <sch:title>Element 25 - INSPIRE Conformity (C)</sch:title>
    <sch:p>
      Conditional element.  Multiple occurrences allowed.  Required if the resource provider
      is claiming conformance to INSPIRE.
    </sch:p>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 25.1 - Degree of Conformity (C)                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinDegreeOfConformity">
    <sch:title>Element 25.1 - INSPIRE Degree of Conformity (C)</sch:title>
    <sch:p>
      Conditional element.  Multiple occurrences allowed.  Required if the resource provider
      is claiming conformance to INSPIRE.
    </sch:p>
    <sch:p>
      This element relates to the INSPIRE Directive 1 and indicates whether a resource conforms to
      a product specification or other INSPIRE thematic specification.  The values are as followed.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDegreeOfConformityGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:report/*/gmd:result/*/gmd:pass"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDegreeOfConformityExplanationGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:report/*/gmd:result/*/gmd:explanation"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 25.2 - Specification (C)                                                           -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinSpecification">
    <sch:title>Element 25.2 - INSPIRE Specification (C)</sch:title>
    <sch:p>
      Conditional element.  Multiple occurrences allowed.  Required if the resource provider is
      claiming conformance to INSPIRE.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      If the resource is intended to conform to the INSPIRE thematic data specification, cite the
      data or thematic specifications that it conforms to using this element.
    </sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinSpecificationTitleGcoTypeTest">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:report/*/gmd:result/*/gmd:specification/*/gmd:title"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinSpecificationDateGcoTypeTest">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:report/*/gmd:result/*/gmd:specification/*/gmd:date/*/gmd:date"/>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="MedinSpecificationDateTypeInnerTextTest">
    <sch:param name="context" value="/*/gmd:dataQualityInfo/*/gmd:report/*/gmd:result/*/gmd:specification/*/gmd:date/*/gmd:dateType"/>
    <sch:param name="element" value="*/@codeListValue"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 26 - Metadata Date (M)                                                             -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinMetadataDate">
    <sch:title>Element 26 - Date of Update of Metadata (M)</sch:title>
    <sch:p>Mandatory element.  One occurence allowed.  Date format.</sch:p>
    <sch:p>
      This describes the last date the metadata was updated on. If the metadata has 
      not been updated it should give the date on which it was created. This should 
      be provided as a date in the format:
    </sch:p>
    <sch:p>Example</sch:p>
    <sch:p>2008-05-12</sch:p>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinDateOfUpdateOfMetadataGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:dateStamp"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 27 - Metadata Standard Name (M)                                                    -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinMetadataStandardName">
    <sch:title>Element 27 - Metadata Standard Name (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurence allowed.
    </sch:p>
    <sch:p>
      Identify the metadata standard used to create the metadata.
    </sch:p>
    <sch:p>
      Example
    </sch:p>
    <sch:p>
      MEDIN Metadata Specification
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:metadataStandardName) = 1">
        Metadata standard name is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="MedinMetadataStandardNameInnerText">
    <sch:param name="context" value="/*/gmd:metadataStandardName"/>
    <sch:param name="element" value="gco:CharacterString"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 28 - Metadata Standard Version (M)                                                 -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinMetadataStandardVersion">
    <sch:title>Element 28 - Metadata Standard Version (M)</sch:title>
    <sch:p>
      Mandatory element.  One occurence allowed.
    </sch:p>
    <sch:p>
      Identify the version of the metadata standard used to create the metadata.
    </sch:p>
    <sch:p>
      Example
    </sch:p>
    <sch:p>
      Version 1.0
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:metadataStandardVersion) = 1">
        Metadata standard version is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="InnerTextPattern" id="MedinMetadataStandardVersionInnerText">
    <sch:param name="context" value="/*/gmd:metadataStandardVersion"/>
    <sch:param name="element" value="gco:CharacterString"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Element 29 - Metadata Language (M)                                                         -->
  <!-- ========================================================================================== -->
  <sch:pattern fpi="MedinMetadataLanguage">
    <sch:title>Element 29 - Metadata Language (M)</sch:title>
    <sch:p>
      Mandatory element.  Multiple metadata languages allowed.  Controlled vocabulary.
    </sch:p>
    <sch:p>
      Describes the language(s) elements of the metadata.
    </sch:p>
    <sch:p>
      Select the relevant 3-letter code(s) from the ISO 639-2 code list of languages.
      Additional languages may be added to this list if required.  A full list of UK
      language codes is listed in Annex 3 and a list of recognized languages is available
      online http://www.loc.gov/standards/iso639-2.
    </sch:p>
    <sch:p>
      Examples
    </sch:p>
    <sch:p>
      <sch:emph>Example 1:</sch:emph> eng (English)
    </sch:p>
    <sch:p>
      <sch:emph>Example 2:</sch:emph> cym (Welsh)
    </sch:p>
    <sch:rule context="/*">
      <sch:assert test="count(gmd:language) = 1">
        Metadata Language is mandatory.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <sch:pattern is-a="LanguagePattern" id="MedinMetadataLanguageLanguagePattern">
    <sch:param name="context" value="/*/gmd:language"/>
  </sch:pattern>

  <sch:pattern is-a="GcoTypeTestPattern" id="MedinMetadataLanguageGcoTypeTestPattern">
    <sch:param name="context" value="/*/gmd:language"/>
  </sch:pattern>

  <!-- ========================================================================================== -->
  <!-- Abstract Patterns                                                                          -->
  <!-- ========================================================================================== -->

  <!-- Test that a gco element has a value or has a valid nilReason value -->
  <sch:pattern abstract="true" id="GcoTypeTestPattern">
    <sch:rule context="$context">
      <sch:assert test="(string-length(.) &gt; 0) or 
                  (@gco:nilReason = 'inapplicable' or
                  @gco:nilReason = 'missing' or 
                  @gco:nilReason = 'template' or
                  @gco:nilReason = 'unknown' or
                  @gco:nilReason = 'withheld')">
        The <sch:name/> element must have a value or a Nil Reason.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test that an element has a value and is not empty string -->
  <sch:pattern abstract="true" id="InnerTextPattern">
    <sch:rule context="$context">
      <sch:assert test="string-length($element) &gt; 0">
        The <sch:name/> element should have a value.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test the language values (Metadata and Resource) -->
  <sch:pattern abstract="true" id="LanguagePattern">
    <sch:rule context="$context">
      <sch:assert test="(./gco:CharacterString = 'eng' or ./gco:CharacterString = 'cym' or ./gco:CharacterString = 'gle' or ./gco:CharacterString = 'gla' or ./gco:CharacterString = 'cor') or 
                  (./gmd:LanguageCode/@codeListValue='eng' or ./gmd:LanguageCode/@codeListValue='cym' or ./gmd:LanguageCode/@codeListValue='gle' or ./gmd:LanguageCode/@codeListValue='gla' or ./gmd:LanguageCode/@codeListValue='cor')">
        <sch:name/> must be one of eng, cym, gle, gla or cor.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test for the responsible party information -->
  <sch:pattern abstract="true" id="ResponsiblePartyPattern">
    <!-- Count of Organisation Name and Individual Name >= 1 -->
    <sch:rule context="$context">
      <sch:assert test="count(*/gmd:organisationName) + count(*/gmd:individualName) &gt;= 1">
        At least organisation name or individual name must be provided.
      </sch:assert>
      <sch:assert test="$countTest">
        One or more email addresses must be supplied.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

  <!-- Test for gmd:MD_GeographicBoundingBox values -->
  <sch:pattern abstract="true" id="GeographicBoundingBoxPattern">
    <sch:rule context="$context">
      <!-- West Bound Longitude -->
      <sch:assert test="gmd:westBoundLongitude &gt;= -180.0 and gmd:westBoundLongitude &lt;= 180.0">
        westBoundLongitude has a value of <sch:value-of select="gmd:westBoundLongitude"/> which is outside bounds.
      </sch:assert>
      <!-- East Bound Longitude -->
      <sch:assert test="gmd:eastBoundLongitude &gt;= -180.0 and gmd:eastBoundLongitude &lt;= 180.0">
        eastBoundLongitude has a value of <sch:value-of select="gmd:eastBoundLongitude"/> which is outside bounds.
      </sch:assert>
      <!-- South Bound Latitude -->
      <sch:assert test="gmd:southBoundLatitude &gt;= -90.0 and gmd:southBoundLatitude &lt;= gmd:northBoundLatitude">
        southBoundLatitude has a value of <sch:value-of select="gmd:southBoundLatitude"/> which is outside bounds.
      </sch:assert>
      <!-- North Bound Latitude -->
      <sch:assert test="gmd:northBoundLatitude &lt;= 90.0 and gmd:northBoundLatitude &gt;= gmd:southBoundLatitude">
        northBoundLatitude has a value of <sch:value-of select="gmd:northBoundLatitude"/> which is outside bounds.
      </sch:assert>
    </sch:rule>
  </sch:pattern>

</sch:schema>