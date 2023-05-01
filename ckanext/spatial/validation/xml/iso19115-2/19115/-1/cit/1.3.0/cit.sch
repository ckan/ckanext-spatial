<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
    <sch:ns prefix="cit" uri="https://schemas.isotc211.org/19115/-1/cit/1.3"/>
    <sch:ns prefix="mri" uri="https://schemas.isotc211.org/19115/-1/mri/1.3"/>
    <sch:ns prefix="srv" uri="https://schemas.isotc211.org/19115/-1/srv/1.3"/>
    <sch:ns prefix="mdb" uri="https://schemas.isotc211.org/19115/-1/mdb/1.3"/>
    <sch:ns prefix="mcc" uri="https://schemas.isotc211.org/19115/-1/mcc/1.3"/>
    <sch:ns prefix="lan" uri="https://schemas.isotc211.org/19115/-1/lan/1.3"/>
    <sch:ns prefix="gco" uri="https://schemas.isotc211.org/19103/-/gco/1.2"/>
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
    
</sch:schema>