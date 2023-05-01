<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" xml:lang="en">
  <sch:ns prefix="mrl" uri="https://schemas.isotc211.org/19115/-1/mrl/1.3"/>
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
</sch:schema>