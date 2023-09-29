<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
    <sch:ns prefix="mdb" uri="https://schemas.isotc211.org/19115/-1/mdb/1.3"/>
    <sch:ns prefix="mri" uri="https://schemas.isotc211.org/19115/-1/mri/1.3"/>
    <sch:ns prefix="cit" uri="https://schemas.isotc211.org/19115/-1/cit/1.3"/>
    <sch:ns prefix="mcc" uri="https://schemas.isotc211.org/19115/-1/mcc/1.3"/>
    <sch:ns prefix="lan" uri="https://schemas.isotc211.org/19115/-1/lan/1.3"/>
    <sch:ns prefix="gco" uri="https://schemas.isotc211.org/19115/-1/gco/1.3"/>
    <sch:ns prefix="gcx" uri="https://schemas.isotc211.org/19115/-1/gcx/1.3"/>
    <sch:ns prefix="srv" uri="https://schemas.isotc211.org/19115/-1/srv/1.3"/>
    <sch:ns prefix="gex" uri="https://schemas.isotc211.org/19115/-1/gex/1.3"/>
    <sch:ns prefix="mrc" uri="https://schemas.isotc211.org/19115/-1/mrc/1.3"/>
    <sch:ns prefix="mac" uri="https://schemas.isotc211.org/19115/-2/mac/2.2"/>
    <sch:ns prefix="mco" uri="https://schemas.isotc211.org/19115/-1/mco/1.3"/>
    <sch:ns prefix="mex" uri="https://schemas.isotc211.org/19115/-1/mex/1.3"/>
    <sch:ns prefix="mmi" uri="https://schemas.isotc211.org/19115/-1/mmi/1.3"/>
    <sch:ns prefix="mrc" uri="https://schemas.isotc211.org/19115/-1/mrc/1.3"/>
    <sch:ns prefix="mrd" uri="https://schemas.isotc211.org/19115/-1/mrd/1.3"/>
    <sch:ns prefix="mrl" uri="https://schemas.isotc211.org/19115/-1/mrl/1.3"/>
    <sch:ns prefix="mrs" uri="https://schemas.isotc211.org/19115/-1/mrs/1.3"/>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 10, Figure 5
  -->
    
    <!-- 
    Rule: Check root element. 
    Ref: N/A
  -->
    
    <sch:diagnostics>
        <sch:diagnostic 
            id="rule.mdb.root-element-failure-en"
            xml:lang="en">There MUST be a MD_Metadata.</sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.root-element-failure-fr"
            xml:lang="fr">Il DOIT y avoir un MD_Metadata.</sch:diagnostic>
        
        <sch:diagnostic 
            id="rule.mdb.root-element-success-en"
            xml:lang="en">Element MD_Metadata found.</sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.root-element-success-fr"
            xml:lang="fr">Élément MD_Metadata défini.</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mdb.root-element">
        <sch:title xml:lang="en">MD_Metadata element documented</sch:title>
        <sch:title xml:lang="fr">Élément MD_Metadata documenté</sch:title>
        
        <sch:p xml:lang="en">A metadata instance document conforming to 
            this specification SHALL have a MD_Metadata element 
            defined in the http://standards.iso.org/iso/19115/-1/mdb/1.3 namespace.</sch:p>
        <sch:p xml:lang="fr">Une fiche de métadonnées conforme au standard
            ISO19115-1 DOIT avoir un élément MD_Metadata (défini dans l'espace
            de nommage http://standards.iso.org/iso/19115/-1/mdb/1.3).</sch:p>
        <sch:rule context="/">
            <sch:let name="hasMD_MetadataElement" 
                value="count(.//mdb:MD_Metadata) >= 1"/>
            
            <sch:assert test="$hasMD_MetadataElement"
                diagnostics="rule.mdb.root-element-failure-en 
                rule.mdb.root-element-failure-fr"/>
            
            <sch:report test="$hasMD_MetadataElement"
                diagnostics="rule.mdb.root-element-success-en 
                rule.mdb.root-element-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    
    <!-- 
    Rule:  
    Ref: {defaultLocale documented if not defined by the encoding}
    This can't be validated because the encoding is part of the default locale ? TODO-QUESTION
    
    Ref: {defaultLocale.PT_Locale.characterEncoding default value is UTF-8}
    Check that encoding is not empty.
  -->
    
    <sch:diagnostics>
        <sch:diagnostic 
            id="rule.mdb.defaultlocale-failure-en" 
            xml:lang="en">The default locale character encoding is "UTF-8". Current value is
            "<sch:value-of select="$encoding"/>".</sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.defaultlocale-failure-fr" 
            xml:lang="fr">L'encodage ne doit pas être vide. La valeur par défaut est 
            "UTF-8". La valeur actuelle est "<sch:value-of select="$encoding"/>".</sch:diagnostic>
        
        
        <sch:diagnostic 
            id="rule.mdb.defaultlocale-success-en" 
            xml:lang="en">The characeter encoding is "<sch:value-of select="$encoding"/>.
        </sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.defaultlocale-success-fr" 
            xml:lang="fr">L'encodage est "<sch:value-of select="$encoding"/>.
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mdb.defaultlocale">
        <sch:title xml:lang="en">Default locale</sch:title>
        <sch:title xml:lang="fr">Langue du document</sch:title>
        
        <sch:p xml:lang="en">The default locale MUST be documented if
            not defined by the encoding. The default value for the character
            encoding is "UTF-8".</sch:p>
        <sch:p xml:lang="fr">La langue doit être documentée
            si non définie par l'encodage. L'encodage par défaut doit être "UTF-8".</sch:p>
        
        <sch:rule context="/mdb:MD_Metadata/mdb:defaultLocale|
            /mdb:MD_Metadata/mdb:identificationInfo/*/mri:defaultLocale">
            
            <sch:let name="encoding" 
                value="string(lan:PT_Locale/lan:characterEncoding/
                lan:MD_CharacterSetCode/@codeListValue)"/>
            
            <sch:let name="hasEncoding" 
                value="normalize-space($encoding) != ''"/>
            
            
            <sch:assert test="$hasEncoding"
                diagnostics="rule.mdb.defaultlocale-failure-en
                rule.mdb.defaultlocale-failure-fr"/>
            
            <sch:report test="$hasEncoding"
                diagnostics="rule.mdb.defaultlocale-success-en
                rule.mdb.defaultlocale-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    <!-- 
    Rule: 
    Ref: {count(MD_Metadata.parentMetadata) > 0 when there is an higher 
    level object}
    Comment: Can't be validated using schematron AFA the existence
    of an higher level object can't be checked. TODO-QUESTION
  -->
    
    
    <!--
    Rule:  
    Ref: {count(MD_Metadata.metadataScope) > 0 if 
    MD_Metadata.metadataScope.MD_MetadataScope.resourceScope
    not equal to "dataset"}
    
    Ref: {name is mandatory if resourceScope not equal to "dataset"}
  -->
    <sch:diagnostics>
        <sch:diagnostic 
            id="rule.mdb.scope-name-failure-en" 
            xml:lang="en">Specify a name for the metadata scope 
            (required if the scope code is not "dataset", in that case
            "<sch:value-of select="$scopeCode"/>").</sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.scope-name-failure-fr" 
            xml:lang="fr">Préciser la description du domaine d'application 
            (car le document décrit une ressource qui n'est pas un "jeu de données",
            la ressource est de type "<sch:value-of select="$scopeCode"/>").</sch:diagnostic>
        
        
        <sch:diagnostic 
            id="rule.mdb.scope-name-success-en" 
            xml:lang="en">Scope name 
            "<sch:value-of select="$scopeCodeName"/><sch:value-of select="$nilReason"/>"
            is defined for resource with type "<sch:value-of select="$scopeCode"/>".
        </sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.scope-name-success-fr" 
            xml:lang="fr">La description du domaine d'application 
            "<sch:value-of select="$scopeCodeName"/><sch:value-of select="$nilReason"/>"
            est renseignée pour la ressource de type "<sch:value-of select="$scopeCode"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mdb.scope-name">
        <sch:title xml:lang="en">Metadata scope Name</sch:title>
        <sch:title xml:lang="fr">Description du domaine d'application</sch:title>
        
        <sch:p xml:lang="en">If a MD_MetadataScope element is present, 
            the name property MUST have a value if resourceScope is not equal to "dataset"</sch:p>
        <sch:p xml:lang="fr">Si un élément domaine d'application (MD_MetadataScope)
            est défini, sa description (name) DOIT avoir une valeur
            si ce domaine n'est pas "jeu de données" (ie. "dataset").</sch:p>
        
        <sch:rule context="/mdb:MD_Metadata/mdb:metadataScope/
            mdb:MD_MetadataScope[not(mdb:resourceScope/
            mcc:MD_ScopeCode/@codeListValue = 'dataset')]">
            
            <sch:let name="scopeCode" 
                value="mdb:resourceScope/mcc:MD_ScopeCode/@codeListValue"/>
            
            <sch:let name="scopeCodeName" 
                value="normalize-space(mdb:name)"/>
            <sch:let name="hasScopeCodeName" 
                value="normalize-space($scopeCodeName) != ''"/>
            
            <sch:let name="nilReason" 
                value="mdb:name/@gco:nilReason"/>
            <sch:let name="hasNilReason" 
                value="$nilReason != ''"/>
            
            <sch:assert test="$hasScopeCodeName or $hasNilReason"
                diagnostics="rule.mdb.scope-name-failure-en
                rule.mdb.scope-name-failure-fr"/>
            
            <sch:report test="$hasScopeCodeName or $hasNilReason"
                diagnostics="rule.mdb.scope-name-success-en
                rule.mdb.scope-name-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    <!-- 
    Rule: At least one creation date
    Ref: {count(MD _Metadata.dateInfo.CI_Date.dateType.CI_DateTypeCode= "creation") > 0}
  -->
    <sch:diagnostics>
        <sch:diagnostic 
            id="rule.mdb.create-date-failure-en"
            xml:lang="en">Specify a creation date for the metadata record 
            in the metadata section.</sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.create-date-failure-fr"
            xml:lang="fr">Définir une date de création pour le document
            dans la section sur les métadonnées.</sch:diagnostic>
        
        <sch:diagnostic 
            id="rule.mdb.create-date-success-en" 
            xml:lang="en">
            Metadata creation date: <sch:value-of select="$creationDates"/>.
        </sch:diagnostic>
        <sch:diagnostic 
            id="rule.mdb.create-date-success-fr" 
            xml:lang="fr">
            Date de création du document : <sch:value-of select="$creationDates"/>.
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mdb.create-date">
        <sch:title xml:lang="en">Metadata create date</sch:title>
        <sch:title xml:lang="fr">Date de création du document</sch:title>
        
        <sch:p xml:lang="en">A dateInfo property value with data type = "creation" 
            MUST be present in every MD_Metadata instance.</sch:p>
        <sch:p xml:lang="fr">Tout document DOIT avoir une date de création 
            définie (en utilisant un élément dateInfo avec un type de date "creation").</sch:p>
        
        <sch:rule context="mdb:MD_Metadata">
            <sch:let name="creationDates"
                value="./mdb:dateInfo/cit:CI_Date[
                normalize-space(cit:date/gco:DateTime) != '' and 
                cit:dateType/cit:CI_DateTypeCode/@codeListValue = 'creation']/
                cit:date/gco:DateTime"/>
            
            <!-- Check at least one non empty creation date element is defined. -->
            <sch:let name="hasAtLeastOneCreationDate"
                value="count(./mdb:dateInfo/cit:CI_Date[
                normalize-space(cit:date/gco:DateTime) != '' and 
                cit:dateType/cit:CI_DateTypeCode/@codeListValue = 'creation']
                ) &gt; 0"/>
            
            <sch:assert test="$hasAtLeastOneCreationDate"
                diagnostics="rule.mdb.create-date-failure-en
                rule.mdb.create-date-failure-fr"/>
            <sch:report test="$hasAtLeastOneCreationDate"
                diagnostics="rule.mdb.create-date-success-en
                rule.mdb.create-date-success-fr"/>
        </sch:rule>
    </sch:pattern>
  <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 11, Figure 6
  -->
  
  <!-- 
    Rule: MD_Identification
    Ref: {(MD_Metadata.metadataScope.MD_MetadataScope.resourceScope)=’dataset’
    implies count(
    extent.geographicElement.EX_GeographicBoundingBox +
    extent.geographicElement.EX_GeographicDescription) >= 1}
    -->
  
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.datasetextent-failure-en"
      xml:lang="en">The dataset MUST provide a 
      geographic description or a bounding box.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.datasetextent-failure-fr"
      xml:lang="fr">Le jeu de données DOIT être décrit par
      une description géographique ou une emprise.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.datasetextentdesc-success-en"
      xml:lang="en">The dataset geographic description is:
      "<sch:value-of select="normalize-space($geodescription)"/>".</sch:diagnostic>
    <sch:diagnostic id="rule.mri.datasetextentdesc-success-fr"
      xml:lang="fr">La description géographique du jeu de données est
      "<sch:value-of select="normalize-space($geodescription)"/>".</sch:diagnostic>
    
    
    <sch:diagnostic id="rule.mri.datasetextentbox-success-en"
      xml:lang="en">The dataset geographic bounding box is:
      [W:<sch:value-of select="$geobox/gex:westBoundLongitude/*/text()"/>,
      S:<sch:value-of select="$geobox/gex:southBoundLatitude/*/text()"/>],
      [E:<sch:value-of select="$geobox/gex:eastBoundLongitude/*/text()"/>,
      N:<sch:value-of select="$geobox/gex:northBoundLatitude/*/text()"/>],
      .</sch:diagnostic>
    <sch:diagnostic id="rule.mri.datasetextentbox-success-fr"
      xml:lang="fr">L'emprise géographique du jeu de données est
      [W:<sch:value-of select="$geobox/gex:westBoundLongitude/*/text()"/>,
      S:<sch:value-of select="$geobox/gex:southBoundLatitude/*/text()"/>],
      [E:<sch:value-of select="$geobox/gex:eastBoundLongitude/*/text()"/>,
      N:<sch:value-of select="$geobox/gex:northBoundLatitude/*/text()"/>]
      .</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.mri.datasetextent">
    <sch:title xml:lang="en">Dataset extent</sch:title>
    <sch:title xml:lang="fr">Emprise du jeu de données</sch:title>
    
    <sch:rule context="/mdb:MD_Metadata[mdb:metadataScope/
                          mdb:MD_MetadataScope/mdb:resourceScope/
                          mcc:MD_ScopeCode/@codeListValue = 'dataset']/
                          mdb:identificationInfo/mri:MD_DataIdentification">
      
      
      <sch:let name="geodescription" 
        value="mri:extent/gex:EX_Extent/gex:geographicElement/
                  gex:EX_GeographicDescription/gex:geographicIdentifier[
                  normalize-space(mcc:MD_Identifier/mcc:code/*/text()) != ''
                  ]"/>
      <sch:let name="geobox" 
        value="mri:extent/gex:EX_Extent/gex:geographicElement/
                  gex:EX_GeographicBoundingBox[
                  normalize-space(gex:westBoundLongitude/gco:Decimal) != '' and
                  normalize-space(gex:eastBoundLongitude/gco:Decimal) != '' and
                  normalize-space(gex:southBoundLatitude/gco:Decimal) != '' and
                  normalize-space(gex:northBoundLatitude/gco:Decimal) != ''
                  ]"/>

      <sch:let name="hasGeoextent" 
               value="count($geodescription) + count($geobox) > 0"/>
      
      
      <sch:assert test="$hasGeoextent"
        diagnostics="rule.mri.datasetextent-failure-en 
                     rule.mri.datasetextent-failure-fr"/>
      
      <!-- TODO: Improve reporting when having multiple elements -->
      <sch:report test="count($geodescription) > 0"
        diagnostics="rule.mri.datasetextentdesc-success-en 
                     rule.mri.datasetextentdesc-success-fr"/>
      <sch:report test="count($geobox) > 0"
        diagnostics="rule.mri.datasetextentbox-success-en 
                     rule.mri.datasetextentbox-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  <!--
    Ref: {(MD_Metadata.metadataScope.MD_Scope.resourceScope) = 
            (’dataset’ or ‘series’)
          implies topicCategory is mandatory}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.topicategoryfordsandseries-failure-en"
      xml:lang="en">A topic category MUST be specified for 
      dataset or series.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.topicategoryfordsandseries-failure-fr"
      xml:lang="fr">Un thème principal (ISO) DOIT être défini quand
      la ressource est un jeu de donnée ou une série.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.topicategoryfordsandseries-success-en"
      xml:lang="en">Number of topic category identified: 
      <sch:value-of select="count($topics)"/>.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.topicategoryfordsandseries-success-fr"
      xml:lang="fr">Nombre de thèmes : 
      <sch:value-of select="count($topics)"/>.</sch:diagnostic>
  </sch:diagnostics>
  
  
  <sch:pattern id="rule.mri.topicategoryfordsandseries">
    <sch:title xml:lang="en">Topic category for dataset and series</sch:title>
    <sch:title xml:lang="fr">Thème principal d'un jeu de données ou d'une série</sch:title>
    
    <sch:rule context="/mdb:MD_Metadata[mdb:metadataScope/
                         mdb:MD_MetadataScope/mdb:resourceScope/
                         mcc:MD_ScopeCode/@codeListValue = 'dataset' or 
                         mdb:metadataScope/
                         mdb:MD_MetadataScope/mdb:resourceScope/
                         mcc:MD_ScopeCode/@codeListValue = 'series']/
                         mdb:identificationInfo/mri:MD_DataIdentification">
      
      <!-- The topic category is the enumeration value and
      not the human readable one. -->
      <sch:let name="topics" 
               value="mri:topicCategory/mri:MD_TopicCategoryCode"/>
      <sch:let name="hasTopics"
               value="count($topics) > 0"/>
      
      <sch:assert test="$hasTopics"
        diagnostics="rule.mri.topicategoryfordsandseries-failure-en 
                     rule.mri.topicategoryfordsandseries-failure-fr"/>
      
      <sch:report test="$hasTopics"
        diagnostics="rule.mri.topicategoryfordsandseries-success-en 
                     rule.mri.topicategoryfordsandseries-success-fr"/>
      
    </sch:rule>
  </sch:pattern>


  <!--
    Rule: MD_AssociatedResource
    Ref: {count(name + metadataReference) > 0}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.associatedresource-failure-en"
      xml:lang="en">When a resource is associated, a name or a metadata
      reference MUST be specified.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.associatedresource-failure-fr"
      xml:lang="fr">Lorsqu'une resource est associée, un nom ou une 
      référence à une fiche DOIT être défini.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.associatedresource-success-en"
      xml:lang="en">The resource "<sch:value-of select="$resourceRef"/>"
      is associated.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.associatedresource-success-fr"
      xml:lang="fr">La ressource "<sch:value-of select="$resourceRef"/>" 
      est associée.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.mri.associatedresource">
    <sch:title xml:lang="en">Associated resource name</sch:title>
    <sch:title xml:lang="fr">Nom ou référence à une ressource associée</sch:title>
    
    <sch:rule context="//mri:MD_DataIdentification/mri:associatedResource/*|
                       //srv:SV_ServiceIdentification/mri:associatedResource/*">
      
      <!-- May be a CharacterString or LocalisedCharacterString -->
      <sch:let name="nameTitle" 
               value="normalize-space(mri:name/*/cit:title)"/>
      <sch:let name="nameRef" 
               value="mri:name/@uuidref"/>
      <sch:let name="mdRefTitle" 
               value="normalize-space(mri:metadataReference/*/cit:title)"/>
      <sch:let name="mdRefRef" 
               value="mri:metadataReference/@uuidref"/>
      
      <sch:let name="hasName" value="$nameTitle != '' or $nameRef != ''"/>
      <sch:let name="hasMdRef" value="$mdRefTitle != '' or $mdRefRef != ''"/>
      
      <!-- Concat ref assuming there is not both name and metadataReference -->
      <sch:let name="resourceRef" 
               value="concat($nameTitle, $nameRef, 
                             $mdRefRef, $mdRefTitle)"/>
    
      <sch:assert test="$hasName or $hasMdRef"
         diagnostics="rule.mri.associatedresource-failure-en 
                      rule.mri.associatedresource-failure-fr"/>
      
      <sch:report test="$hasName or $hasMdRef"
        diagnostics="rule.mri.associatedresource-success-en 
                     rule.mri.associatedresource-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  <!--    
    Rule: MD_DataIdentification
    Ref: {defaultLocale documented if resource includes textual information}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext-failure-en"
      xml:lang="en">Resource language MUST be defined when the resource
      includes textual information.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext-failure-fr"
      xml:lang="fr">La langue de la resource DOIT être renseignée
      lorsque la ressource contient des informations textuelles.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext-success-en"
      xml:lang="en">Number of resource language: 
      <sch:value-of select="count($resourceLanguages)"/>.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext-success-fr"
      xml:lang="fr">Nombre de langues de la ressource :
      <sch:value-of select="count($resourceLanguages)"/>.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.mri.defaultlocalewhenhastext">
    <!-- 
     Here the context define that the rule applies to DataIdentification
    having FeatureCatalog siblings.
    -->
    <sch:title xml:lang="en">Resource language in relation to Content</sch:title>
    <sch:title xml:lang="fr">Langue de la ressource en relation avec le contenu</sch:title>
    
     <sch:rule context="//mri:MD_DataIdentification[
      ../../mdb:contentInfo/mrc:MD_FeatureCatalogue or
      ../../mdb:contentInfo/mrc:MD_FeatureCatalogueDescription]">
      
      <sch:let name="resourceLanguages" 
        value="mri:defaultLocale/lan:PT_Locale/
                lan:language/lan:LanguageCode/@codeListValue[. != '']"/>
      <sch:let name="hasAtLeastOneLanguage" 
        value="count($resourceLanguages) > 0"/>
      
      <sch:assert test="$hasAtLeastOneLanguage"
        diagnostics="rule.mri.defaultlocalewhenhastext-failure-en 
        rule.mri.defaultlocalewhenhastext-failure-fr"/>
      
      <sch:report test="$hasAtLeastOneLanguage"
        diagnostics="rule.mri.defaultlocalewhenhastext-success-en 
        rule.mri.defaultlocalewhenhastext-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext2-failure-en"
      xml:lang="en">Resource language MUST be defined when the resource
      includes textual information.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext2-failure-fr"
      xml:lang="fr">La langue de la resource DOIT être renseignée
      lorsque la ressource contient des informations textuelles.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext2-success-en"
      xml:lang="en">Number of resource language: 
      <sch:value-of select="count($resourceLanguages2)"/>.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.defaultlocalewhenhastext2-success-fr"
      xml:lang="fr">Nombre de langues de la ressource :
      <sch:value-of select="count($resourceLanguages2)"/>.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.mri.defaultlocalewhenhasPresFormtext">
    <sch:title xml:lang="en">Resource language in relation to Presentation Format</sch:title>
    <sch:title xml:lang="fr">Langue de la ressource en relation avec le format de présentation</sch:title>
    
    <!-- 
     Here the context define that the rule applies to DataIdentification
    having FeatureCatalog siblings.
    -->
    <sch:rule context="//mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:presentationForm/cit:CI_PresentationFormCode/@codeListValue[
      substring(.,1,8) = 'document' or 
      substring (.,1,5) = 'table' or
      substring (.,1,3) = 'map'  
      ]">
      
      <sch:let name="resourceLanguages2" 
        value="mri:defaultLocale/lan:PT_Locale/
        lan:language/lan:LanguageCode/@codeListValue[. != '']"/>
      <sch:let name="hasAtLeastOneLanguage2" 
        value="count($resourceLanguages2) > 0"/>
      
      <sch:assert test="$hasAtLeastOneLanguage2"
        diagnostics="rule.mri.defaultlocalewhenhastext2-failure-en 
        rule.mri.defaultlocalewhenhastext2-failure-fr"/>
      
      <sch:report test="$hasAtLeastOneLanguage2"
        diagnostics="rule.mri.defaultlocalewhenhastext2-success-en 
        rule.mri.defaultlocalewhenhastext2-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  <!--
    Ref: {defaultLocale.PT_Locale.characterEncoding default value is UTF-8}
    
    See Implemented in rule.mdb.defaultlocale.
    
    TODO: A better implementation would have been to make an Abstract
    test and use it in both places to not mix mdb and mri testsuites.
    -->
  
  
  
  <!--
    Rule: MD_Keywords
    Ref: {When the resource described is a service, 
    one instance of MD_Keyword shall refer to the service taxonomy 
    defined in ISO19119}
    
    QUESTION-TODO: This rules defined should move to srv.sch ?
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mri.servicetaxonomy-failure-en"
      xml:lang="en">A service metadata SHALL refer to the service
      taxonomy defined in ISO19119 defining one or more value in the
      keyword section.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.servicetaxonomy-failure-fr"
      xml:lang="fr">Une métadonnée de service DEVRAIT référencer
      un type de service tel que défini dans l'ISO19119 dans la
      section mot clé.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mri.servicetaxonomy-success-en"
      xml:lang="en">Number of service taxonomy specified: 
      <sch:value-of select="count($serviceTaxonomies)"/>.</sch:diagnostic>
    <sch:diagnostic id="rule.mri.servicetaxonomy-success-fr"
      xml:lang="fr">Nombre de types de service :
      <sch:value-of select="count($serviceTaxonomies)"/>.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.servicetaxonomy">
    <sch:title xml:lang="en">Service taxonomy</sch:title>
    <sch:title xml:lang="fr">Taxonomie des services</sch:title>
    
    <!-- 
    QUESTION-TODO: Is this the list to check against ?
      The list is not multilingual ?
    -->
    <sch:rule context="//srv:SV_ServiceIdentification">
      <sch:let name="listOfTaxonomy" 
               value="'Geographic human interaction services, 
                       Geographic model/information management services, 
                       Geographic workflow/task management services, 
                       Geographic processing services, 
                       Geographic processing services — spatial,
                       Geographic processing services — thematic,
                       Geographic processing services — temporal, 
                       Geographic processing services — metadata, 
                       Geographic communication services'"/>
      <sch:let name="serviceTaxonomies" 
        value="mri:descriptiveKeywords/mri:MD_Keywords/mri:keyword[
        contains($listOfTaxonomy, */text())]"/>
      <sch:let name="hasAtLeastOneTaxonomy" 
        value="count($serviceTaxonomies) > 0"/>
      
      <!-- SHALL <sch:assert test="$hasAtLeastOneTaxonomy"
        diagnostics="rule.mri.servicetaxonomy-failure-en 
                     rule.mri.servicetaxonomy-failure-fr"/> -->
      
      <sch:report test="$hasAtLeastOneTaxonomy"
        diagnostics="rule.mri.servicetaxonomy-success-en 
                     rule.mri.servicetaxonomy-success-fr"/>
    </sch:rule>
  </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 25, Figure 20 Citation and responsible party information classes
  -->
    
    <!-- 
    Rule: CI_Individual
    Ref: {count(name + positionName) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.cit.individualnameandposition-failure-en"
            xml:lang="en">The individual does not have a name or a position.</sch:diagnostic>
        <sch:diagnostic id="rule.cit.individualnameandposition-failure-fr"
            xml:lang="fr">Une personne n'a pas de nom ou de fonction.</sch:diagnostic>
        
        <sch:diagnostic id="rule.cit.individualnameandposition-success-en"
            xml:lang="en">Individual name is  
            "<sch:value-of select="normalize-space($name)"/>"
            and position
            "<sch:value-of select="normalize-space($position)"/>"
            .</sch:diagnostic>
        <sch:diagnostic id="rule.cit.individualnameandposition-success-fr"
            xml:lang="fr">Le nom de la personne est  
            "<sch:value-of select="normalize-space($name)"/>"
            ,sa fonction 
            "<sch:value-of select="normalize-space($position)"/>"
            .</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.cit.individualnameandposition">
        <sch:title xml:lang="en">Individual MUST have a name or a position</sch:title>
        <sch:title xml:lang="fr">Une personne DOIT avoir un nom ou une fonction</sch:title>
        
        <sch:rule context="//cit:CI_Individual">
            
            <sch:let name="name" value="cit:name"/>
            <sch:let name="position" value="cit:positionName"/>
            <sch:let name="hasName" 
                value="normalize-space($name) != ''"/>
            <sch:let name="hasPosition" 
                value="normalize-space($position) != ''"/>
            
            <sch:assert test="$hasName or $hasPosition"
                diagnostics="rule.cit.individualnameandposition-failure-en 
                rule.cit.individualnameandposition-failure-fr"/>
            
            <sch:report test="$hasName or $hasPosition"
                diagnostics="rule.cit.individualnameandposition-success-en 
                rule.cit.individualnameandposition-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    
    
    <!-- 
    Rule: CI_Organisation
    Ref: {count(name + logo) > 0}
  -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.cit.organisationnameandlogo-failure-en"
            xml:lang="en">The organisation does not have a name or a logo.</sch:diagnostic>
        <sch:diagnostic id="rule.cit.organisationnameandlogo-failure-fr"
            xml:lang="fr">Une organisation n'a pas de nom ou de logo.</sch:diagnostic>
        
        <sch:diagnostic id="rule.cit.organisationnameandlogo-success-en"
            xml:lang="en">Organisation name is  
            "<sch:value-of select="normalize-space($name)"/>"
            and logo filename is 
            "<sch:value-of select="normalize-space($logo)"/>"
            .</sch:diagnostic>
        <sch:diagnostic id="rule.cit.organisationnameandlogo-success-fr"
            xml:lang="fr">Le nom de l'organisation est  
            "<sch:value-of select="normalize-space($name)"/>"
            , son logo
            "<sch:value-of select="normalize-space($logo)"/>"
            .</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.cit.organisationnameandlogo">
        <sch:title xml:lang="en">Organisation MUST have a name or a logo</sch:title>
        <sch:title xml:lang="fr">Une organisation DOIT avoir un nom ou un logo</sch:title>
        
        <sch:rule context="//cit:CI_Organisation">
            
            <sch:let name="name" value="cit:name"/>
            <sch:let name="logo" value="cit:logo/mcc:MD_BrowseGraphic/mcc:fileName"/>
            <sch:let name="hasName" 
                value="normalize-space($name) != ''"/>
            <sch:let name="hasLogo" 
                value="normalize-space($logo) != ''"/>
            
            <sch:assert test="$hasName or $hasLogo"
                diagnostics="rule.cit.organisationnameandlogo-failure-en 
                rule.cit.organisationnameandlogo-failure-fr"/>
            
            <sch:report test="$hasName or $hasLogo"
                diagnostics="rule.cit.organisationnameandlogo-success-en 
                rule.cit.organisationnameandlogo-success-fr"/>
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 24, Figure 19 Extent information classes
  -->
    
    <!-- 
    Rule: EX_Extent
    Ref: {count(description + 
                geographicElement + 
                temporalElement + 
                verticalElement) >0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.gex.extenthasoneelement-failure-en"
            xml:lang="en">The extent does not contain a description nor one or more of (geographicElement or temporalElement or verticalElement).</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-failure-fr"
            xml:lang="fr">L'étendue ne contient pas de description ni un ou plusieurs de (GeographicElement ou temporalElement ou verticalElement)</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-desc-success-en"
            xml:lang="en">The extent contains a description.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-desc-success-fr"
            xml:lang="fr">L'étendue contient une description.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-id-success-en"
            xml:lang="en">The extent contains a geographic identifier.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-id-success-fr"
            xml:lang="fr">L'étendue contient un identifiant géographique.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-box-success-en"
            xml:lang="en">The extent contains a bounding box element.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-box-success-fr"
            xml:lang="fr">L'étendue contient une emprise géographique.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-poly-success-en"
            xml:lang="en">The extent contains a bounding polygon.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-poly-success-fr"
            xml:lang="fr">L'étendue contient un polygone englobant.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-vertical-success-en"
            xml:lang="en">The extent contains a vertical element.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-vertical-success-fr"
            xml:lang="fr">L'étendue contient une étendue verticale.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.extenthasoneelement-temporal-success-en"
            xml:lang="en">The extent contains a temporal element.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.extenthasoneelement-temporal-success-fr"
            xml:lang="fr">L'étendue contient une étendue temporelle.</sch:diagnostic>
        
    </sch:diagnostics>
    
    <sch:pattern id="rule.gex.extenthasoneelement">
        <sch:title xml:lang="en">Extent MUST have a description or one or more geographic, temporal or vertical element</sch:title>
        <sch:title xml:lang="fr">L'étendue DOIT avoir une description ou un ou plusieurs éléments géographiques, temporels ou verticaux</sch:title>
        
        <sch:rule context="//gex:EX_Extent">
            
            <!-- Check that element exist and is not empty ones.
      TODO improve nonEmpty checks -->
            <sch:let name="description" 
                value="gex:description[text() != '']"/>
            <sch:let name="geographicId" 
                value="gex:geographicElement/gex:EX_GeographicDescription/
                gex:geographicIdentifier[normalize-space(*) != '']"/>
            <sch:let name="geographicBox" 
                value="gex:geographicElement/
                gex:EX_GeographicBoundingBox[
                normalize-space(gex:westBoundLongitude/gco:Decimal) != '' and
                normalize-space(gex:eastBoundLongitude/gco:Decimal) != '' and
                normalize-space(gex:southBoundLatitude/gco:Decimal) != '' and
                normalize-space(gex:northBoundLatitude/gco:Decimal) != ''
                ]"/>
            <sch:let name="geographicPoly" 
                value="gex:geographicElement/gex:EX_BoundingPolygon[
                normalize-space(gex:polygon) != '']"/>
            <sch:let name="temporal" 
                value="gex:temporalElement/gex:EX_TemporalExtent[
                normalize-space(gex:extent) != '']"/>
            <sch:let name="vertical" 
                value="gex:verticalElement/gex:EX_VerticalExtent[
                normalize-space(gex:minimumValue) != '' and
                normalize-space(gex:maximumValue) != '']"/>
            
            
            <sch:let name="hasAtLeastOneElement" 
                value="count($description) +
                count($geographicId) +
                count($geographicBox) +
                count($geographicPoly) +
                count($temporal) +
                count($vertical) > 0
                "/>
            
            <sch:assert test="$hasAtLeastOneElement"
                diagnostics="rule.gex.extenthasoneelement-failure-en 
                rule.gex.extenthasoneelement-failure-fr"/>
            
            <sch:report test="count($description)"
                diagnostics="rule.gex.extenthasoneelement-desc-success-en 
                rule.gex.extenthasoneelement-desc-success-fr"/>
            <sch:report test="count($geographicId)"
                diagnostics="rule.gex.extenthasoneelement-id-success-en 
                rule.gex.extenthasoneelement-id-success-fr"/>
            <sch:report test="count($geographicBox)"
                diagnostics="rule.gex.extenthasoneelement-box-success-en 
                rule.gex.extenthasoneelement-box-success-fr"/>
            <sch:report test="count($geographicPoly)"
                diagnostics="rule.gex.extenthasoneelement-poly-success-en 
                rule.gex.extenthasoneelement-poly-success-fr"/>
            <sch:report test="count($temporal)"
                diagnostics="rule.gex.extenthasoneelement-temporal-success-en 
                rule.gex.extenthasoneelement-temporal-success-fr"/>
            <sch:report test="count($vertical)"
                diagnostics="rule.gex.extenthasoneelement-vertical-success-en 
                rule.gex.extenthasoneelement-vertical-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    <!-- 
    Rule: EX_VerticalExtent
    Ref: {count(verticalCRS + verticalCRSId) > 0)}
  -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.gex.verticalhascrsorcrsid-failure-en"
            xml:lang="en">The vertical extent contains neither a vertical CRS nor a vertical CRS identifier.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.verticalhascrsorcrsid-failure-fr"
            xml:lang="fr">L'étendue verticale ne contient ni un CRS vertical ni un identifiant CRS vertical.</sch:diagnostic>
        
        <sch:diagnostic id="rule.gex.verticalhascrsorcrsid-success-en"
            xml:lang="en">The vertical extent contains vertical CRS information.</sch:diagnostic>
        <sch:diagnostic id="rule.gex.verticalhascrsorcrsid-success-fr"
            xml:lang="fr">L'étendue verticale contient les informations sur le CRS vertical.</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.gex.verticalhascrsorcrsid">
        <sch:title xml:lang="en">Vertical element MUST contains a vertical CRS or a vertiacl CRS identifier</sch:title>
        <sch:title xml:lang="fr">Une étendue verticale DOIT contenir un CRS vertical ou un identifiant de CRS vertical</sch:title>
        
        <sch:rule context="//gex:EX_VerticalExtent">
            
            <sch:let name="vertCRS" value="gex:verticalCRS"/>
            <sch:let name="vertCRSId" value="gex:verticalCRSId"/>
            <sch:let name="hasVertCrsOrVertCrsId" 
                value="count($vertCRS) + count($vertCRSId) > 0"/>
            
            <sch:assert test="$hasVertCrsOrVertCrsId"
                diagnostics="rule.gex.verticalhascrsorcrsid-failure-en 
                rule.gex.verticalhascrsorcrsid-failure-fr"/>
            
            <sch:report test="$hasVertCrsOrVertCrsId"
                diagnostics="rule.gex.verticalhascrsorcrsid-success-en 
                rule.gex.verticalhascrsorcrsid-success-fr"/>
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-2:2019(E) page 9, Figure 3 Acquisition Details
  -->
    
    <!-- 
    Rule: MI_Operationl
    Ref: {count(otherProperty) = count(otherPropertyType)}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mac.matchOperPropType-failure-en"
            xml:lang="en">Each Operation other property must have a type.</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchOperPropType-failure-fr"
            xml:lang="fr">Chaque opération autre propriété doit avoir un type.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mac.countOperOtherProp-success-en"
            xml:lang="en">Cardinality of other property is  
            "<sch:value-of select="$countOperOtherProp"/>"
            and Cardinality of other property type is
            "<sch:value-of select="$countOperOtherPropType"/>"
            .</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchOperPropType-success-fr"
            xml:lang="fr">La cardinalité des autres biens est  
            "<sch:value-of select="$countOperOtherProp"/>"
            et la cardinalité d'un autre type de propriété est 
            "<sch:value-of select="$countOperOtherPropType"/>"
            .</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mac.matchOperPropType">
        <sch:title xml:lang="en">Operations must have a type for each other property</sch:title>
        <sch:title xml:lang="fr">Les opérations doivent avoir un type pour chaque autre propriété</sch:title>
        
        <sch:rule context="//mac:MI_Operation">
            
            <sch:let name="countOperOtherProp" value="count(mac:otherProperty)"/>
            <sch:let name="countOperOtherPropType" value="count(mac:otherPropertyType)"/>
            
            <sch:assert test="$countOperOtherProp = $countOperOtherPropType"
                diagnostics="rule.mac.matchOperPropType-failure-en 
                rule.mac.matchOperPropType-failure-fr"/>
            
            <sch:report test="$countOperOtherProp = $countOperOtherPropType"
                diagnostics="rule.mac.countOperOtherProp-success-en 
                rule.mac.matchOperPropType-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    <!-- 
    Rule: MI_Platform
    Ref: {count(otherProperty) = count(otherPropertyType)}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mac.matchPlatPropType-failure-en"
            xml:lang="en">Each Platform other property must have a type.</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchPlatPropType-failure-fr"
            xml:lang="fr">Chaque autre propriété Platform doit avoir un type.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mac.countPlatOtherProp-success-en"
            xml:lang="en">Cardinality of other property is  
            "<sch:value-of select="$countPlatOtherProp"/>"
            and Cardinality of other property type is
            "<sch:value-of select="$countPlatOtherPropType"/>"
            .</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchPlatPropType-success-fr"
            xml:lang="fr">La cardinalité des autres biens est  
            "<sch:value-of select="$countPlatOtherProp"/>"
            et la cardinalité d'un autre type de propriété est 
            "<sch:value-of select="$countPlatOtherPropType"/>"
            .</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mac.matchPlatPropType">
        <sch:title xml:lang="en">Platforms must have a type for each other property</sch:title>
        <sch:title xml:lang="fr">Les Platform doivent avoir un type pour chaque autre propriété</sch:title>
        
        <sch:rule context="//mac:MI_Platform">
            
            <sch:let name="countPlatOtherProp" value="count(mac:otherProperty)"/>
            <sch:let name="countPlatOtherPropType" value="count(mac:otherPropertyType)"/>
            
            <sch:assert test="$countPlatOtherProp = $countPlatOtherPropType"
                diagnostics="rule.mac.matchPlatPropType-failure-en 
                rule.mac.matchPlatPropType-failure-fr"/>
            
            <sch:report test="$countPlatOtherProp = $countPlatOtherPropType"
                diagnostics="rule.mac.countPlatOtherProp-success-en 
                rule.mac.matchPlatPropType-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    <!-- 
    Rule: MI_Instrument
    Ref: {count(otherProperty) = count(otherPropertyType)}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mac.matchInstPropType-failure-en"
            xml:lang="en">Each Instrument other property must have a type.</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchInstPropType-failure-fr"
            xml:lang="fr">Chaque autre propriété Instrument doit avoir un type.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mac.countInstOtherProp-success-en"
            xml:lang="en">Cardinality of other property is  
            "<sch:value-of select="$countInstOtherProp"/>"
            and Cardinality of other property type is
            "<sch:value-of select="$countInstOtherPropType"/>"
            .</sch:diagnostic>
        <sch:diagnostic id="rule.mac.matchInstPropType-success-fr"
            xml:lang="fr">La cardinalité des autres biens est  
            "<sch:value-of select="$countInstOtherProp"/>"
            et la cardinalité d'un autre type de propriété est 
            "<sch:value-of select="$countInstOtherPropType"/>"
            .</sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mac.matchInstPropType">
        <sch:title xml:lang="en">Instrument must have a type for each other property</sch:title>
        <sch:title xml:lang="fr">Les Instrument doivent avoir un type pour chaque autre propriété</sch:title>
        
        <sch:rule context="//mac:MI_Instform">
            
            <sch:let name="countInstOtherProp" value="count(mac:otherProperty)"/>
            <sch:let name="countInstOtherPropType" value="count(mac:otherPropertyType)"/>
            
            <sch:assert test="$countInstOtherProp = $countInstOtherPropType"
                diagnostics="rule.mac.matchInstPropType-failure-en 
                rule.mac.matchInstPropType-failure-fr"/>
            
            <sch:report test="$countInstOtherProp = $countInstOtherPropType"
                diagnostics="rule.mac.countInstOtherProp-success-en 
                rule.mac.matchInstPropType-success-fr"/>
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 13, Figure 8 Constraint information classes
  -->
    
    <!-- 
    Rule: MD_Releasability
    Ref: {count(addressee + statement) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mco-releasability-failure-en"
            xml:lang="en">
            The releasabilty defines neither addressee nor statement.</sch:diagnostic>
        <sch:diagnostic id="rule.mco-releasability-failure-fr"
            xml:lang="fr">
            La possibilité de divulgation ne définit ni le destinataire ni la déclaration.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mco-releasability-success-en"
            xml:lang="en">
            The releasability addressee is defined: 
            "<sch:value-of select="normalize-space($addressee)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mco-releasability-success-fr"
            xml:lang="fr">
            Le destinataire dans le cas de possibilité de divulgation 
            est défini "<sch:value-of select="normalize-space($addressee)"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mco-releasability-statement-success-en"
            xml:lang="en">
            The releasability statement is
            "<sch:value-of select="normalize-space($statement)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mco-releasability-statement-success-fr"
            xml:lang="fr">
            L'indication concernant la possibilité de divulgation est 
            "<sch:value-of select="normalize-space($statement)"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mco-releasability">
        <sch:title xml:lang="en">Releasability MUST
            specified an addresse or a statement</sch:title>
        <sch:title xml:lang="fr">La possibilité de divulgation 
            DOIT définir un destinataire ou une indication</sch:title>
        
        <sch:rule context="//mco:MD_Releasability">
            
            <sch:let name="addressee" 
                value="mco:addressee[normalize-space(.) != '']"/>
            
            <sch:let name="statement" 
                value="mco:statement/*[normalize-space(.) != '']"/>
            
            <sch:let name="hasAddresseeOrStatement" 
                value="count($addressee) + 
                count($statement) > 0"/>
            
            <sch:assert test="$hasAddresseeOrStatement"
                diagnostics="rule.mco-releasability-failure-en 
                rule.mco-releasability-failure-fr"/>
            
            <sch:report test="count($addressee)"
                diagnostics="rule.mco-releasability-success-en 
                rule.mco-releasability-success-fr"/>
            
            <sch:report test="count($statement)"
                diagnostics="rule.mco-releasability-statement-success-en 
                rule.mco-releasability-statement-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
    
    
    <!--
    Rule: MD_LegalConstraints
    Ref: {If MD_LegalConstraints used then 
          count of (accessConstraints +
                    useConstraints + 
                    otherConstraints + 
                    useLimitation + 
                    releasability) > 0}
         -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mco-legalconstraintdetails-failure-en"
            xml:lang="en">
            The legal constraint is incomplete.</sch:diagnostic>
        <sch:diagnostic id="rule.mco-legalconstraintdetails-failure-fr"
            xml:lang="fr">
            La contrainte légale est incomplète.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mco-legalconstraintdetails-success-en"
            xml:lang="en">
            The legal constraint is complete.
        </sch:diagnostic>
        <sch:diagnostic id="rule.mco-legalconstraintdetails-success-fr"
            xml:lang="fr">
            La contrainte légale est complète.
        </sch:diagnostic>
        
    </sch:diagnostics>
    
    <sch:pattern id="rule.mco-legalconstraintdetails">
        <sch:title xml:lang="en">Legal constraint MUST specify at least on of - 
            an access constraint, 
            use constraint, 
            other constraint,  
            use limitation, or 
            releasability</sch:title>
        <sch:title xml:lang="fr">La contrainte légale DOIT spécifier au moins l'un des éléments suivants - 
            une contrainte d'accès, 
            une contrainte d'utilisation, 
            une autre contrainte, 
            une limitation d'utilisation ou 
            une possibilité de libération</sch:title>
        
        <sch:rule context="//mco:MD_LegalConstraints">
            
            <sch:let name="accessConstraints" 
                value="mco:accessConstraints[
                normalize-space(.) != '' or
                count(.//@codeListValue[. != '']) > 0]"/>
            
            <sch:let name="useConstraints" 
                value="mco:useConstraints/*[
                normalize-space(.) != '' or
                count(.//@codeListValue[. != '']) > 0]"/>
            
            <sch:let name="otherConstraints" 
                value="mco:otherConstraints/*[
                normalize-space(.) != '']"/>
            
            <sch:let name="useLimitation" 
                value="mco:useLimitation/*[
                normalize-space(.) != '' or
                count(.//@codeListValue[. != '']) > 0]"/>
            
            <sch:let name="releasability" 
                value="mco:releasability/*[
                normalize-space(.) != '' or
                count(.//@codeListValue[. != '']) > 0]"/>
            
            <sch:let name="hasDetails" 
                value="count($accessConstraints) + 
                count($useConstraints) + 
                count($otherConstraints) + 
                count($useLimitation) + 
                count($releasability)
                > 0"/>
            
            <sch:assert test="$hasDetails"
                diagnostics="rule.mco-legalconstraintdetails-failure-en 
                rule.mco-legalconstraintdetails-failure-fr"/>
            
            <sch:report test="$hasDetails"
                diagnostics="rule.mco-legalconstraintdetails-success-en 
                rule.mco-legalconstraintdetails-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
    
    <!--
    Rule: MD_LegalConstraints
    Ref: {otherConstraints: only documented if accessConstraints or
      useConstraints = “otherRestrictions”}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mco-legalconstraint-other-failure-en"
            xml:lang="en">
            The legal constraint - other constraints defines while neither
            access contsraints nor use constraint are set to other restrictions</sch:diagnostic>
        <sch:diagnostic id="rule.mco-legalconstraint-other-failure-fr"
            xml:lang="fr">
            La contrainte légale - les autres contraintes définissent alors que ni
            les contraintes d'accès ni les contraintes d'utilisation ne sont définies sur d'autres restrictions..</sch:diagnostic>
        
        <sch:diagnostic id="rule.mco-legalconstraint-other-success-en"
            xml:lang="en">
            The legal constraint other constraints is 
            "<sch:value-of select="$otherConstraints"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mco-legalconstraint-other-success-fr"
            xml:lang="fr">
            Les autres contraintes de la contrainte légale sont
            "<sch:value-of select="$otherConstraints"/>".
        </sch:diagnostic>
        
    </sch:diagnostics>
    
    <sch:pattern id="rule.mco-legalconstraint-other">
        <sch:title xml:lang="en">Legal constraint defining
            other restrictions for access or use constraint MUST
            specified other constraint.</sch:title>
        <sch:title xml:lang="fr">Une contrainte légale indiquant
            d'autres restrictions d'utilisation ou d'accès DOIT
            préciser ces autres restrictions</sch:title>
        
        <sch:rule context="//mco:MD_LegalConstraints[
            mco:accessConstraints/mco:MD_RestrictionCode/@codeListValue = 'otherRestrictions' or
            mco:useConstraints/mco:MD_RestrictionCode/@codeListValue = 'otherRestrictions'
            ]">
            
            
            <sch:let name="otherConstraints" 
                value="mco:otherConstraints/*[normalize-space(.) != '']"/>
            
            <sch:let name="hasOtherConstraints" 
                value="count($otherConstraints) > 0"/>
            
            <sch:assert test="$hasOtherConstraints"
                diagnostics="rule.mco-legalconstraint-other-failure-en 
                rule.mco-legalconstraint-other-failure-fr"/>
            
            <sch:report test="$hasOtherConstraints"
                diagnostics="rule.mco-legalconstraint-other-success-en 
                rule.mco-legalconstraint-other-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
      <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 21, Figure 16 Metadata extension information classes
  -->
  
  <!-- 
    Rule: MD_ExtendedElementInformation
    Ref: {if dataType notEqual codelist, enumeration, or codelistElement, 
          then
          obligation, maximumOccurence and domainValue are mandatory}
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mex.datatypedetails-maxocc-failure-en"
      xml:lang="en">
      Extended element information "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      does not specified max occurence.</sch:diagnostic>
    <sch:diagnostic id="rule.mex.datatypedetails-maxocc-failure-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      ne précise pas le nombre d'occurences maximum.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mex.datatypedetails-maxocc-success-en"
      xml:lang="en">
      Extended element information "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      has max occurence: "<sch:value-of select="$maximumOccurrence"/>".
    </sch:diagnostic>
    <sch:diagnostic id="rule.mex.datatypedetails-maxocc-success-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      a pour nombre d'occurences maximum : "<sch:value-of select="$maximumOccurrence"/>".
    </sch:diagnostic>
    
    
    
    <sch:diagnostic id="rule.mex.datatypedetails-domain-failure-en"
      xml:lang="en">
      Extended element information "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      does not specified domain value.</sch:diagnostic>
    <sch:diagnostic id="rule.mex.datatypedetails-domain-failure-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      ne précise pas la valeur du domaine.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mex.datatypedetails-domain-success-en"
      xml:lang="en">
      Extended element information "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      has domain value: "<sch:value-of select="$domainValue"/>".
    </sch:diagnostic>
    <sch:diagnostic id="rule.mex.datatypedetails-domain-success-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      a pour valeur du domaine : "<sch:value-of select="$domainValue"/>".
    </sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.mex.datatypedetails">
    <sch:title xml:lang="en">Extended element information 
      which are not codelist, enumeration or codelistElement 
      MUST specified max occurence and domain value</sch:title>
    <sch:title xml:lang="fr">Un élément d'extension qui n'est
      ni une codelist, ni une énumération, ni un élément de codelist
      DOIT préciser le nombre maximum d'occurences 
      ainsi que la valeur du domaine</sch:title>
    
    <sch:rule context="//mex:MD_ExtendedElementInformation[
      mex:dataType/mex:MD_DatatypeCode/@codeListValue != 'codelist' and
      mex:dataType/mex:MD_DatatypeCode/@codeListValue != 'enumeration' and
      mex:dataType/mex:MD_DatatypeCode/@codeListValue != 'codelistElement'
      ]">
      
      <sch:let name="name" 
        value="normalize-space(mex:name/*)"/>
      
      <sch:let name="dataType" 
        value="normalize-space(mex:dataType/mex:MD_DatatypeCode/@codeListValue)"/>
      
      
      <sch:let name="maximumOccurrence" 
        value="normalize-space(mex:maximumOccurrence/*)"/>
      
      <sch:let name="hasMaximumOccurrence" 
        value="$maximumOccurrence != ''"/>
      
      <sch:assert test="$hasMaximumOccurrence"
        diagnostics="rule.mex.datatypedetails-maxocc-failure-en 
                     rule.mex.datatypedetails-maxocc-failure-fr"/>
      
      <sch:report test="$hasMaximumOccurrence"
        diagnostics="rule.mex.datatypedetails-maxocc-success-en 
                     rule.mex.datatypedetails-maxocc-success-fr"/>
      
      
      <sch:let name="domainValue" 
        value="normalize-space(mex:domainValue/*)"/>
      
      <sch:let name="hasDomainValue" 
        value="$domainValue != ''"/>
      
      <sch:assert test="$hasDomainValue"
        diagnostics="rule.mex.datatypedetails-domain-failure-en 
                     rule.mex.datatypedetails-domain-failure-fr"/>
      
      <sch:report test="$hasDomainValue"
        diagnostics="rule.mex.datatypedetails-domain-success-en 
                     rule.mex.datatypedetails-domain-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  <!-- 
    Rule: MD_ExtendedElementInformation
    Ref:  {if obligation = conditional then condition is mandatory}
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mex.conditional-failure-en"
      xml:lang="en">
      The conditional extended element "<sch:value-of select="$name"/>"
      does not specified the condition.</sch:diagnostic>
    <sch:diagnostic id="rule.mex.conditional-failure-fr"
      xml:lang="fr">
      L'élément d'extension conditionnel "<sch:value-of select="$name"/>"
      ne précise pas les termes de la condition.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mex.conditional-success-en"
      xml:lang="en">
      The conditional extended element "<sch:value-of select="$name"/>"
      has for condition: "<sch:value-of select="$condition"/>".
    </sch:diagnostic>
    <sch:diagnostic id="rule.mex.conditional-success-fr"
      xml:lang="fr">
      L'élément d'extension conditionnel "<sch:value-of select="$name"/>"
      a pour condition : "<sch:value-of select="$condition"/>".
    </sch:diagnostic>
    
  </sch:diagnostics>
  
  <sch:pattern id="rule.mex.conditional">
    <sch:title xml:lang="en">Extended element information 
      which are conditional MUST explained the condition</sch:title>
    <sch:title xml:lang="fr">Un élément d'extension conditionnel
      DOIT préciser les termes de la condition</sch:title>
    
    <sch:rule context="//mex:MD_ExtendedElementInformation[
      mex:obligation/mex:MD_ObligationCode = 'conditional'
      ]">
      
      <sch:let name="name" 
        value="normalize-space(mex:name/*)"/>
      
      <sch:let name="condition" 
        value="normalize-space(mex:condition/*)"/>
      
      <sch:let name="hasCondition" 
        value="$condition != ''"/>
      
      <sch:assert test="$hasCondition"
        diagnostics="rule.mex.conditional-failure-en 
                     rule.mex.conditional-failure-fr"/>
      
      <sch:report test="$hasCondition"
        diagnostics="rule.mex.conditional-success-en 
                     rule.mex.conditional-success-fr"/>
      
    </sch:rule>
  </sch:pattern>
  
  
  
  
  
  <!-- 
    Rule: MD_ExtendedElementInformation
    Ref: {if dataType = codelistElement, enumeration, or codelist then code is
        mandatory}
        
    Ref: {if dataType = codelistElement, enumeration, or codelist then
        conceptName is mandatory}
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.mex.mandatorycode-failure-en"
      xml:lang="en">
      The extended element "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      does not specified a code.</sch:diagnostic>
    <sch:diagnostic id="rule.mex.mandatorycode-failure-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      ne précise pas de code.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mex.mandatorycode-success-en"
      xml:lang="en">
      The extended element "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      has for code: "<sch:value-of select="$code"/>".
    </sch:diagnostic>
    <sch:diagnostic id="rule.mex.mandatorycode-success-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      a pour code : "<sch:value-of select="$code"/>".
    </sch:diagnostic>
    
    
    
    
    
    <sch:diagnostic id="rule.mex.mex.mandatoryconceptname-failure-en"
      xml:lang="en">
      The extended element "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      does not specified a concept name.</sch:diagnostic>
    <sch:diagnostic id="rule.mex.mex.mandatoryconceptname-failure-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      ne précise pas de nom de concept.</sch:diagnostic>
    
    <sch:diagnostic id="rule.mex.mex.mandatoryconceptname-success-en"
      xml:lang="en">
      The extended element "<sch:value-of select="$name"/>"
      of type "<sch:value-of select="$dataType"/>"
      has for concept name: "<sch:value-of select="$conceptName"/>".
    </sch:diagnostic>
    <sch:diagnostic id="rule.mex.mex.mandatoryconceptname-success-fr"
      xml:lang="fr">
      L'élément d'extension "<sch:value-of select="$name"/>"
      de type "<sch:value-of select="$dataType"/>"
      a pour nom de concept : "<sch:value-of select="$conceptName"/>".
    </sch:diagnostic>
    
  </sch:diagnostics>
  
  <sch:pattern id="rule.mex.mandatorycode">
    <sch:title xml:lang="en">Extended element information 
      which are codelist, enumeration or codelistElement 
      MUST specified a code and a concept name</sch:title>
    <sch:title xml:lang="fr">Un élément d'extension qui est
      une codelist, une énumération, un élément de codelist
      DOIT préciser un code et un nom de concept</sch:title>
    
    <sch:rule context="//mex:MD_ExtendedElementInformation[
      mex:dataType/mex:MD_DatatypeCode/@codeListValue = 'codelist' or
      mex:dataType/mex:MD_DatatypeCode/@codeListValue = 'enumeration' or
      mex:dataType/mex:MD_DatatypeCode/@codeListValue = 'codelistElement'
      ]">
      
      <sch:let name="name" 
        value="normalize-space(mex:name/*)"/>
      
      <sch:let name="dataType" 
        value="normalize-space(mex:dataType/mex:MD_DatatypeCode/@codeListValue)"/>
      
      <sch:let name="code" 
        value="normalize-space(mex:code/*)"/>
      
      <sch:let name="hasCode" 
        value="$code != ''"/>
      
      <sch:assert test="$hasCode"
        diagnostics="rule.mex.mandatorycode-failure-en 
                     rule.mex.mandatorycode-failure-fr"/>
      
      <sch:report test="$hasCode"
        diagnostics="rule.mex.mandatorycode-success-en 
                     rule.mex.mandatorycode-success-fr"/>
      
      
      
      <sch:let name="conceptName" 
        value="normalize-space(mex:conceptName/*)"/>
      
      <sch:let name="hasConceptName" 
        value="$conceptName != ''"/>
      
      <sch:assert test="$hasConceptName"
        diagnostics="rule.mex.mex.mandatoryconceptname-failure-en 
                     rule.mex.mex.mandatoryconceptname-failure-fr"/>
      
      <sch:report test="$hasConceptName"
        diagnostics="rule.mex.mex.mandatoryconceptname-success-en 
                     rule.mex.mex.mandatoryconceptname-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  <!-- 
    Rule: MD_ExtendedElementInformation
    Ref: {if dataType = codelist, enumeration, or codelistElement then name is
        not used}
    Comment: No test. Should we set the element invalid if name is set ? TODO-QUESTION
  -->
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 15, Figure 10 Maintenance information classes
  -->
    
    <!-- 
    Rule: MD_MaintenanceInformation
    Ref: {count(maintenanceAndUpdateFrequency + 
                userDefinedMaintenanceFrequency) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mmi-updatefrequency-failure-en"
            xml:lang="en">
            The maintenance information does not define update frequency.</sch:diagnostic>
        <sch:diagnostic id="rule.mmi-updatefrequency-failure-fr"
            xml:lang="fr">
            L'information sur la maintenance ne définit pas de fréquence de mise à jour.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mmi-updatefrequency-success-en"
            xml:lang="en">
            The update frequency is "<sch:value-of select="$maintenanceAndUpdateFrequency"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mmi-updatefrequency-success-fr"
            xml:lang="fr">
            La fréquence de mise à jour est "<sch:value-of select="$maintenanceAndUpdateFrequency"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mmi-updatefrequency-user-success-en"
            xml:lang="en">
            The user defined update frequency is 
            "<sch:value-of select="normalize-space($userDefinedMaintenanceFrequency)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mmi-updatefrequency-user-success-fr"
            xml:lang="fr">
            La fréquence de mise à jour définie par l'utilisateur est 
            "<sch:value-of select="normalize-space($userDefinedMaintenanceFrequency)"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mmi-updatefrequency">
        <sch:title xml:lang="en">Maintenance information MUST
            specified an update frequency</sch:title>
        <sch:title xml:lang="fr">L'information sur la maintenance
            DOIT définir une fréquence de mise à jour</sch:title>
        
        <sch:rule context="//mmi:MD_MaintenanceInformation">
            
            <sch:let name="userDefinedMaintenanceFrequency" 
                value="mmi:userDefinedMaintenanceFrequency/
                gco:TM_PeriodDuration[normalize-space(.) != '']"/>
            
            <sch:let name="maintenanceAndUpdateFrequency" 
                value="mmi:maintenanceAndUpdateFrequency/
                mmi:MD_MaintenanceFrequencyCode/@codeListValue[normalize-space(.) != '']"/>
            
            <sch:let name="hasCodeOrUserFreq" 
                value="count($maintenanceAndUpdateFrequency) + 
                count($userDefinedMaintenanceFrequency) > 0"/>
            
            <sch:assert test="$hasCodeOrUserFreq"
                diagnostics="rule.mmi-updatefrequency-failure-en 
                rule.mmi-updatefrequency-failure-fr"/>
            
            <sch:report test="count($userDefinedMaintenanceFrequency)"
                diagnostics="rule.mmi-updatefrequency-user-success-en 
                rule.mmi-updatefrequency-user-success-fr"/>
            
            <sch:report test="count($maintenanceAndUpdateFrequency)"
                diagnostics="rule.mmi-updatefrequency-success-en 
                rule.mmi-updatefrequency-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 18, Figure 13 Content information classes
  -->
    
    
    
    <!-- 
    Rule: MD_FeatureCatalogueDescription
    Ref: {if FeatureCatalogue not included with resource and
          MD_FeatureCatalogue not provided then
            featureCatalogueCitation > 0}
    Comment: No test because feature catalogue with resource can't be asserted (TODO-QUESTION)
    -->
    
    
    
    <!-- 
    Rule: MD_SampleDimension
    Ref: {if count(maxValue + minValue + meanValue) > 0 then units is
          mandatory}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mrc.sampledimension-failure-en"
            xml:lang="en">The sample dimension does not provide max, min or mean value.</sch:diagnostic>
        <sch:diagnostic id="rule.mrc.sampledimension-failure-fr"
            xml:lang="fr">La dimension ne précise pas de valeur maximum ou minimum ni de moyenne.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mrc.sampledimension-max-success-en"
            xml:lang="en">
            The sample dimension max value is 
            "<sch:value-of select="normalize-space($max)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrc.sampledimension-max-success-fr"
            xml:lang="fr">
            La valeur maximum de la dimension de l'échantillon est
            "<sch:value-of select="normalize-space($max)"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mrc.sampledimension-min-success-en"
            xml:lang="en">
            The sample dimension min value is 
            "<sch:value-of select="normalize-space($min)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrc.sampledimension-min-success-fr"
            xml:lang="fr">
            La valeur minimum de la dimension de l'échantillon est
            "<sch:value-of select="normalize-space($min)"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mrc.sampledimension-mean-success-en"
            xml:lang="en">
            The sample dimension mean value is 
            "<sch:value-of select="normalize-space($mean)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrc.sampledimension-mean-success-fr"
            xml:lang="fr">
            La valeur moyenne de la dimension de l'échantillon est
            "<sch:value-of select="normalize-space($mean)"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mrc.sampledimension">
        <sch:title xml:lang="en">Sample dimension MUST provide a max, 
            a min or a mean value</sch:title>
        <sch:title xml:lang="fr">La dimension de l'échantillon DOIT préciser
            une valeur maximum, une valeur minimum ou une moyenne</sch:title>
        
        <sch:rule context="//mrc:MD_SampleDimension">
            
            <sch:let name="max" 
                value="mrc:maxValue[normalize-space(*) != '']"/>
            <sch:let name="min" 
                value="mrc:minValue[normalize-space(*) != '']"/>
            <sch:let name="mean" 
                value="mrc:meanValue[normalize-space(*) != '']"/>
            
            <sch:let name="hasMaxOrMinOrMean" 
                value="count($max) + count($min) + count($mean) > 0"/>
            
            <sch:assert test="$hasMaxOrMinOrMean"
                diagnostics="rule.mrc.sampledimension-failure-en 
                rule.mrc.sampledimension-failure-fr"/>
            
            <sch:report test="count($max)"
                diagnostics="rule.mrc.sampledimension-max-success-en 
                rule.mrc.sampledimension-max-success-fr"/>
            <sch:report test="count($min)"
                diagnostics="rule.mrc.sampledimension-min-success-en 
                rule.mrc.sampledimension-min-success-fr"/>
            <sch:report test="count($mean)"
                diagnostics="rule.mrc.sampledimension-mean-success-en 
                rule.mrc.sampledimension-mean-success-fr"/>
        </sch:rule>
    </sch:pattern>
    
    
    
    <!-- 
    Rule: MD_Band
    Ref: {if count(boundMax + boundMin) > 0 then boundUnits is mandatory}
    -->
    
    <sch:diagnostics>
        <sch:diagnostic id="rule.mrc.bandunit-failure-en"
            xml:lang="en">The band defined a bound without unit.</sch:diagnostic>
        <sch:diagnostic id="rule.mrc.bandunit-failure-fr"
            xml:lang="fr">La bande définit une borne minimum et/ou maximum
            sans préciser d'unité.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mrc.bandunit-success-en"
            xml:lang="en">
            The band bound [<sch:value-of select="$min"/>-<sch:value-of select="$max"/>] unit is 
            "<sch:value-of select="$units"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrc.bandunit-success-fr"
            xml:lang="fr">
            L'unité de la borne [<sch:value-of select="$min"/>-<sch:value-of select="$max"/>] est 
            "<sch:value-of select="$units"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mrc.bandunit">
        <sch:title xml:lang="en">Band MUST specified bounds units 
            when a bound max or bound min is defined</sch:title>
        <sch:title xml:lang="fr">Une bande DOIT préciser l'unité 
            lorsqu'une borne maximum ou minimum est définie</sch:title>
        
        <sch:rule context="//mrc:MD_Band[
            normalize-space(mrc:boundMax/*) != '' or 
            normalize-space(mrc:boundMin/*) != ''
            ]">
            
            <sch:let name="max" 
                value="normalize-space(mrc:boundMax/*)"/>
            <sch:let name="min" 
                value="normalize-space(mrc:boundMin/*)"/>
            <sch:let name="units" 
                value="normalize-space(mrc:boundUnits[normalize-space(*) != ''])"/>
            
            <sch:let name="hasUnits" 
                value="$units != ''"/>
            
            <sch:assert test="$hasUnits"
                diagnostics="rule.mrc.bandunit-failure-en 
                rule.mrc.bandunit-failure-fr"/>
            
            <sch:report test="$hasUnits"
                diagnostics="rule.mrc.bandunit-success-en 
                rule.mrc.bandunit-success-fr"/>
        </sch:rule>
    </sch:pattern>   
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 20, Figure 15 Distribution information classes
  -->
    
    <!-- 
    Rule: MD_Medium
    Ref: {if density used then count (densityUnits) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mrd.mediumunit-failure-en"
            xml:lang="en">The medium define a density without unit.</sch:diagnostic>
        <sch:diagnostic id="rule.mrd.mediumunit-failure-fr"
            xml:lang="fr">La densité du média est définie sans unité.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mrd.mediumunit-success-en"
            xml:lang="en">
            Medium density is "<sch:value-of select="$density"/>" (unit:  
            "<sch:value-of select="$units"/>").
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrd.mediumunit-success-fr"
            xml:lang="fr">
            La densité du média est "<sch:value-of select="$density"/>" (unité :  
            "<sch:value-of select="$units"/>").
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mrd.mediumunit">
        <sch:title xml:lang="en">Medium having density MUST specified density units</sch:title>
        <sch:title xml:lang="fr">Un média précisant une densité DOIT préciser l'unité</sch:title>
        
        <sch:rule context="//mrd:MD_Medium[mrd:density]">
            
            <sch:let name="density" 
                value="normalize-space(mrd:density/*)"/>
            <sch:let name="units" 
                value="normalize-space(mrd:densityUnits[normalize-space(*) != ''])"/>
            
            <sch:let name="hasUnits" 
                value="$units != ''"/>
            
            <sch:assert test="$hasUnits"
                diagnostics="rule.mrd.mediumunit-failure-en 
                rule.mrd.mediumunit-failure-fr"/>
            
            <sch:report test="$hasUnits"
                diagnostics="rule.mrd.mediumunit-success-en 
                rule.mrd.mediumunit-success-fr"/>
        </sch:rule>
    </sch:pattern> 
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 14, Figure 9 Lineage information classes
  -->
    
    <!-- 
    Rule: LI_Source
    Ref: {count(description + scope) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mrl-describeScope-failure-en"
            xml:lang="en">
            The Source defines neither description nor scope.</sch:diagnostic>
        <sch:diagnostic id="rule.mrl-describeScope-failure-fr"
            xml:lang="fr">
            La Source ne définit ni la description ni la portée.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mrl-describeScope-success-en"
            xml:lang="en">
            The source scope is defined: 
            "<sch:value-of select="normalize-space($scope)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrl-describeScope-success-fr"
            xml:lang="fr">
            La portée source est définie: "<sch:value-of select="normalize-space($scope)"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mrl-describeScope-statement-success-en"
            xml:lang="en">
            The source statement is
            "<sch:value-of select="normalize-space($description)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrl-describeScope-statement-success-fr"
            xml:lang="fr">
            La description de la source est 
            "<sch:value-of select="normalize-space($description)"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mrl-describeScope">
        <sch:title xml:lang="en">Releasability MUST
            specified an addresse or a statement</sch:title>
        <sch:title xml:lang="fr">La possibilité de divulgation 
            DOIT définir un destinataire ou une indication</sch:title>
        
        <sch:rule context="//mrl:LI_Scope">
            
            <sch:let name="scope" 
                value="mrl:scope[normalize-space(.) != '']"/>
            
            <sch:let name="description" 
                value="mrl:description/*[normalize-space(.) != '']"/>
            
            <sch:let name="hasDescriptionOrScope" 
                value="count($scope) + 
                count($description) > 0"/>
            
            <sch:assert test="$hasDescriptionOrScope"
                diagnostics="rule.mrl-describeScope-failure-en 
                rule.mrl-describeScope-failure-fr"/>
            
            <sch:report test="count($scope)"
                diagnostics="rule.mrl-describeScope-success-en 
                rule.mrl-describeScope-success-fr"/>
            
            <sch:report test="count($description)"
                diagnostics="rule.mrl-describeScope-statement-success-en 
                rule.mrl-describeScope-statement-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-2:2019(E) page 11, Figure 4 Lineage extension
  -->
    
    <!-- 
    Rule: LE_Source
    Ref: {count(description + scope) > 0}
    -->
    <sch:diagnostics>
        <sch:diagnostic id="rule.mrlEx-describeScope-failure-en"
            xml:lang="en">
            The Source defines neither description nor scope.</sch:diagnostic>
        <sch:diagnostic id="rule.mrlEx-describeScope-failure-fr"
            xml:lang="fr">
            La Source ne définit ni la description ni la portée.</sch:diagnostic>
        
        <sch:diagnostic id="rule.mrlEx-describeScope-success-en"
            xml:lang="en">
            The source scope is defined: 
            "<sch:value-of select="normalize-space($scope)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrlEx-describeScope-success-fr"
            xml:lang="fr">
            La portée source est définie: "<sch:value-of select="normalize-space($scope)"/>".
        </sch:diagnostic>
        
        <sch:diagnostic id="rule.mrlEx-describeScope-statement-success-en"
            xml:lang="en">
            The source statement is
            "<sch:value-of select="normalize-space($description)"/>".
        </sch:diagnostic>
        <sch:diagnostic id="rule.mrlEx-describeScope-statement-success-fr"
            xml:lang="fr">
            La description de la source est 
            "<sch:value-of select="normalize-space($description)"/>".
        </sch:diagnostic>
    </sch:diagnostics>
    
    <sch:pattern id="rule.mrlEx-describeScope">
        <sch:title xml:lang="en">Releasability MUST
            specified an addresse or a statement</sch:title>
        <sch:title xml:lang="fr">La possibilité de divulgation 
            DOIT définir un destinataire ou une indication</sch:title>
        
        <sch:rule context="//mrl:LE_Source">
            
            <sch:let name="scope" 
                value="mrl:scope[normalize-space(.) != '']"/>
            
            <sch:let name="description" 
                value="mrl:description/*[normalize-space(.) != '']"/>
            
            <sch:let name="hasDescriptionOrScope" 
                value="count($scope) + 
                count($description) > 0"/>
            
            <sch:assert test="$hasDescriptionOrScope"
                diagnostics="rule.mrlEx-describeScope-failure-en 
                rule.mrl-describeScope-failure-fr"/>
            
            <sch:report test="count($scope)"
                diagnostics="rule.mrlEx-describeScope-success-en 
                rule.mrl-describeScope-success-fr"/>
            
            <sch:report test="count($description)"
                diagnostics="rule.mrlEx-describeScope-statement-success-en 
                rule.mrl-describeScope-statement-success-fr"/>
            
        </sch:rule>
    </sch:pattern>
    <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 17, Figure 12 Reference system information classes
  -->
    
    <!-- 
    Rule: MD_ReferenceSystem
    Ref: responsibilities
          Refer to ISO 19111 and ISO19111-2 when coordinate reference
          systeminformation is not given through referenceSystem Identifier
    -->
  <!--
    ISO 19115-3 base requirements for metadata instance documents
    
    See ISO19115-1:2014(E) page 23, Figure 18 Service metadata information classes
  -->
  
  <!-- 
    Rule: SV_ServiceIdentification
    Ref: {count(containsChain + containsOperations) > 0}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.chainoroperations-failure-en"
      xml:lang="en">The service identification does not contain chain or operation.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.chainoroperations-failure-fr"
      xml:lang="fr">L'identification du service ne contient ni chaîne d'opérations, ni opération.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.chainoroperations-success-en"
      xml:lang="en">
      The service identification contains the following 
      number of chains: <sch:value-of select="count($chains)"/>.
      and number of operations: <sch:value-of select="count($operations)"/>.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.chainoroperations-success-fr"
      xml:lang="fr">
      L'identification du service contient 
      le nombre de chaînes d'opérations suivant : <sch:value-of select="count($chains)"/>.
      le nombre d'opérations : <sch:value-of select="count($operations)"/>.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.chainoroperations">
    <sch:title xml:lang="en">Service identification MUST contains chain or operations</sch:title>
    <sch:title xml:lang="fr">L'identification du service DOIT contenir des chaînes d'opérations
      ou des opérations</sch:title>
    
    <sch:rule context="//srv:SV_ServiceIdentification">
      
      <!-- Consider only containsChain or operationsName
      having a name. -->
      <sch:let name="chains" value="srv:containsChain[
        normalize-space(srv:SV_OperationChainMetadata/srv:name) != '']"/>
      <sch:let name="operations" value="srv:containsOperations[
        normalize-space(srv:SV_OperationMetadata/srv:operationName) != '']"/>
      <sch:let name="hasChainOrOperation" 
        value="count($operations) + count($chains) > 0"/>
      
      <sch:assert test="$hasChainOrOperation"
        diagnostics="rule.srv.chainoroperations-failure-en 
                     rule.srv.chainoroperations-failure-fr"/>
      
      <sch:report test="$hasChainOrOperation"
        diagnostics="rule.srv.chainoroperations-success-en 
                     rule.srv.chainoroperations-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  <!-- 
    Rule: SV_ServiceIdentification
    Ref:  {If coupledResource exists then count(coupledResource) > 0}
    Comment: Can't be validated using schematron AFA the existence
    of the related object can't be defined. TODO-QUESTION
    -->
  
  
  <!-- 
    Rule: SV_ServiceIdentification
    Ref: {If coupledResource exists then count(couplingType) > 0}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.coupledresource-failure-en"
      xml:lang="en">The service identification MUST specify coupling type 
      when coupled resource exist</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresource-failure-fr"
      xml:lang="fr">L'identification du service DOIT 
      définir un type de couplage lorsqu'une ressource est couplée.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.coupledresource-success-en"
      xml:lang="en">
      Number of coupled resources: <sch:value-of select="count($coupledResource)"/>.
      Coupling type: "<sch:value-of select="$couplingType"/>".</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresource-success-fr"
      xml:lang="fr">
      Nombre de ressources couplées : <sch:value-of select="count($coupledResource)"/>.
      Type de couplage : "<sch:value-of select="$couplingType"/>".</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.coupledresource">
    <sch:title xml:lang="en">Service identification MUST specify coupling type 
      when coupled resource exist</sch:title>
    <sch:title xml:lang="fr">L'identification du service DOIT 
      définir un type de couplage lorsqu'une ressource est couplée</sch:title>
    
    <sch:rule context="//srv:SV_ServiceIdentification[srv:coupledResource]">
      
      <sch:let name="couplingType" 
               value="srv:couplingType/
                        srv:SV_CouplingType/@codeListValue[. != '']"/>
      <sch:let name="coupledResource" value="srv:coupledResource"/>
      <sch:let name="hasCouplingType" 
        value="count($couplingType) > 0"/>
      
      <sch:assert test="$hasCouplingType"
        diagnostics="rule.srv.coupledresource-failure-en 
                     rule.srv.coupledresource-failure-fr"/>
      
      <sch:report test="$hasCouplingType"
        diagnostics="rule.srv.coupledresource-success-en 
                     rule.srv.coupledresource-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  <!-- 
    Rule: SV_ServiceIdentification
    Ref: {If operatedDataset used then count (operatesOn) = 0}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.operateddataset-failure-en"
      xml:lang="en">The service identification define operatedDataset.
      No operatesOn can be specified.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.operateddataset-failure-fr"
      xml:lang="fr">L'identification du service utilise operatedDataset.
      OperatesOn ne peut être utilisé dans ce cas.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.operateddataset-success-en"
      xml:lang="en">Service identification only use operated dataset.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.operateddataset-success-fr"
      xml:lang="fr">L'identification du service n'utilise que operatedDataset.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.operateddataset">
    <sch:title xml:lang="en">Service identification MUST not use 
      both operatedDataset and operatesOn</sch:title>
    <sch:title xml:lang="fr">L'identification du service NE DOIT PAS 
      utiliser en même temps operatedDataset et operatesOn</sch:title>
    
    <sch:rule context="//srv:SV_ServiceIdentification[srv:operatedDataset]">
      
      <sch:let name="operatesOn" value="srv:operatesOn"/>
      <sch:let name="hasOperatesOn" 
        value="count($operatesOn) > 0"/>
      
      <sch:assert test="not($hasOperatesOn)"
        diagnostics="rule.srv.operateddataset-failure-en 
                     rule.srv.operateddataset-failure-fr"/>
      
      <sch:report test="not($hasOperatesOn)"
        diagnostics="rule.srv.operateddataset-success-en 
                     rule.srv.operateddataset-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  <!-- 
    Rule: SV_ServiceIdentification
    Ref: {If operatesOn used count(operatedDataset) = 0}
    -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.operatesononly-failure-en"
      xml:lang="en">The service identification define operatesOn.
      No operatedDataset can be specified.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.operatesononly-failure-fr"
      xml:lang="fr">L'identification du service utilise operatesOn.
      OperatedDataset ne peut être utilisé dans ce cas.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.operatesononly-success-en"
      xml:lang="en">The service identification only use operates on.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.operatesononly-success-fr"
      xml:lang="fr">L'identification du service n'utilise que 
      des éléments de type operatesOn.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.operatesononly">
    <sch:title xml:lang="en">Service identification MUST not use 
      both operatesOn and operatedDataset</sch:title>
    <sch:title xml:lang="fr">L'identification du service NE DOIT PAS 
      utiliser en même temps operatesOn et operatedDataset</sch:title>
    
    <sch:rule context="//srv:SV_ServiceIdentification[srv:operatesOn]">
      
      <sch:let name="operatedDataset" value="srv:operatedDataset"/>
      
      <sch:let name="hasOperatedDataset" 
        value="count($operatedDataset) > 0"/>
      
      <sch:assert test="not($hasOperatedDataset)"
        diagnostics="rule.srv.operatesononly-failure-en 
                     rule.srv.operatesononly-failure-fr"/>
      
      <sch:report test="not($hasOperatedDataset)"
        diagnostics="rule.srv.operatesononly-success-en 
                     rule.srv.operatesononly-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  <!-- 
    Rule: SV_CoupledResource
    Ref: {count(resourceReference + resource) > 0}
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.harresourcereforresource-failure-en"
      xml:lang="en">The coupled resource does not contains a resource 
    nor a resource reference.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.harresourcereforresource-failure-fr"
      xml:lang="fr">La ressource couplée ne contient ni une ressource
    ni une référence à une ressource.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.harresourcereforresource-success-en"
      xml:lang="en">The coupled resource contains a resource or a resource reference.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.harresourcereforresource-success-fr"
      xml:lang="fr">La ressource couplée contient une ressource ou une référence 
      à une ressource.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.harresourcereforresource">
    <sch:title xml:lang="en">Coupled resource MUST contains 
      a resource or a resource reference</sch:title>
    <sch:title xml:lang="fr">Une ressource couplée DOIT
      définir une ressource ou une référence à une ressource</sch:title>
    
    <sch:rule context="//srv:SV_CoupledResource">
      
      <sch:let name="resourceReference" value="srv:resourceReference"/>
      <sch:let name="resource" value="srv:resource"/>
      
      <sch:let name="hasResourceReferenceOrResource" 
        value="count($resourceReference) + count($resource) > 0"/>
      
      <sch:assert test="$hasResourceReferenceOrResource"
        diagnostics="rule.srv.harresourcereforresource-failure-en 
                     rule.srv.harresourcereforresource-failure-fr"/>
      
      <sch:report test="$hasResourceReferenceOrResource"
        diagnostics="rule.srv.harresourcereforresource-success-en 
                     rule.srv.harresourcereforresource-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  
  
  
  
  <!-- 
    Rule: SV_CoupledResource
    Ref: {If resource used then count(resourceReference) = 0}
  -->
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresource-failure-en"
      xml:lang="en">The coupled resource contains both a resource 
      and a resource reference.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresource-failure-fr"
      xml:lang="fr">La ressource couplée utilise à la fois une ressource
      et une référence à une ressource.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.coupledresourceonlyresource-success-en"
      xml:lang="en">The coupled resource contains only resources.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresource-success-fr"
      xml:lang="fr">La ressource couplée contient uniquement des ressources.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.coupledresourceonlyresource">
    <sch:title xml:lang="en">Coupled resource MUST not use
      both resource and resource reference</sch:title>
    <sch:title xml:lang="fr">Une ressource couplée NE DOIT PAS
      utiliser en même temps une ressource et une référence
      à une ressource</sch:title>
    
    <sch:rule context="//srv:SV_CoupledResource[srv:resource]">
      
      <sch:let name="resourceReference" value="srv:resourceReference"/>
      <sch:let name="hasResourceReference" 
        value="count($resourceReference) > 0"/>
      
      <sch:assert test="not($hasResourceReference)"
        diagnostics="rule.srv.coupledresourceonlyresource-failure-en 
                     rule.srv.coupledresourceonlyresource-failure-fr"/>
      
      <sch:report test="not($hasResourceReference)"
        diagnostics="rule.srv.coupledresourceonlyresource-success-en 
                     rule.srv.coupledresourceonlyresource-success-fr"/>
    </sch:rule>
  </sch:pattern>
  
  
  <!-- 
    Rule: SV_CoupledResource
    Ref: {If resourceReference used then count(resource) = 0}
  -->
  
  <sch:diagnostics>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresourceref-failure-en"
      xml:lang="en">The coupled resource contains both a resource 
      and a resource reference.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresourceref-failure-fr"
      xml:lang="fr">La ressource couplée utilise à la fois une ressource
      et une référence à une ressource.</sch:diagnostic>
    
    <sch:diagnostic id="rule.srv.coupledresourceonlyresourceref-success-en"
      xml:lang="en">The coupled resource contains only resource references.</sch:diagnostic>
    <sch:diagnostic id="rule.srv.coupledresourceonlyresourceref-success-fr"
      xml:lang="fr">La ressource couplée contient uniquement des références à des ressources.</sch:diagnostic>
  </sch:diagnostics>
  
  <sch:pattern id="rule.srv.coupledresourceonlyresourceref">
    <sch:title xml:lang="en">Coupled resource MUST not use
      both resource and resource reference</sch:title>
    <sch:title xml:lang="fr">Une ressource couplée NE DOIT PAS
      utiliser en même temps une ressource et une référence
      à une ressource</sch:title>
    
    <sch:rule context="//srv:SV_CoupledResource[srv:resourceReference]">
      
      <sch:let name="resource" value="srv:resource"/>
      <sch:let name="hasResource" 
        value="count($resource) > 0"/>
      
      <sch:assert test="not($hasResource)"
        diagnostics="rule.srv.coupledresourceonlyresourceref-failure-en 
                     rule.srv.coupledresourceonlyresourceref-failure-fr"/>
      
      <sch:report test="not($hasResource)"
        diagnostics="rule.srv.coupledresourceonlyresourceref-success-en 
                     rule.srv.coupledresourceonlyresourceref-success-fr"/>
    </sch:rule>
  </sch:pattern>    
</sch:schema>