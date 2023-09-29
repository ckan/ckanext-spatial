<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
    <sch:ns prefix="mdb" uri="https://schemas.isotc211.org/19115/-1/mdb/1.3"/>
    <sch:ns prefix="mri" uri="https://schemas.isotc211.org/19115/-1/mri/1.3"/>
    <sch:ns prefix="cit" uri="https://schemas.isotc211.org/19115/-1/cit/1.3"/>
    <sch:ns prefix="gex" uri="https://schemas.isotc211.org/19115/-1/gex/1.3"/>
    <sch:ns prefix="srv" uri="https://schemas.isotc211.org/19115/-1/srv/1.3"/>
    <sch:ns prefix="mcc" uri="https://schemas.isotc211.org/19115/-1/mcc/1.3"/>
    <sch:ns prefix="lan" uri="https://schemas.isotc211.org/19115/-1/lan/1.3"/>
    <sch:ns prefix="gco" uri="https://schemas.isotc211.org/19103/-/gco/1.2"/>
    <sch:ns prefix="gcx" uri="https://schemas.isotc211.org/19103/-/gcx/1.2"/>
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
    
</sch:schema>