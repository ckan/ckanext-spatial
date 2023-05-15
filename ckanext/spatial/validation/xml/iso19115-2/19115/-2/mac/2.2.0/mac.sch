<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
    <sch:ns prefix="mac" uri="http://standards.iso.org/iso/19115/-2/mac/2.2"/>
    <sch:ns prefix="cit" uri="http://standards.iso.org/iso/19115/-1/cit/1.3"/>
    <sch:ns prefix="mri" uri="http://standards.iso.org/iso/19115/-1/mri/1.3"/>
    <sch:ns prefix="srv" uri="http://standards.iso.org/iso/19115/-1/srv/1.3"/>
    <sch:ns prefix="mdb" uri="http://standards.iso.org/iso/19115/-1/mdb/1.3"/>
    <sch:ns prefix="mcc" uri="http://standards.iso.org/iso/19115/-1/mcc/1.3"/>
    <sch:ns prefix="lan" uri="http://standards.iso.org/iso/19115/-1/lan/1.3"/>
    <sch:ns prefix="gco" uri="http://standards.iso.org/iso/19103/-/gco/1.2"/>
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
</sch:schema>
    