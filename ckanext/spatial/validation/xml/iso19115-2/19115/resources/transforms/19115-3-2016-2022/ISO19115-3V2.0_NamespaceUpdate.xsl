<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:dqc="http://standards.iso.org/iso/19157/-2/dqc/1.0"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:fcc="https://schemas.isotc211.org/19110/-/fcc/2.1" 
                xmlns:gfc="https://schemas.isotc211.org/19110/-/gfc/2.1" 
                xmlns:cat="http://standards.iso.org/iso/19115/-3/cat/1.0"
                xmlns:cit="http://standards.iso.org/iso/19115/-3/cit/2.0"
                xmlns:gex="http://standards.iso.org/iso/19115/-3/gex/1.0"
                xmlns:lan="http://standards.iso.org/iso/19115/-3/lan/1.0"
                xmlns:srv="http://standards.iso.org/iso/19115/-3/srv/2.0"
                xmlns:mac="http://standards.iso.org/iso/19115/-3/mac/2.0"
                xmlns:mas="http://standards.iso.org/iso/19115/-3/mas/1.0"
                xmlns:mcc="http://standards.iso.org/iso/19115/-3/mcc/1.0"
                xmlns:mco="http://standards.iso.org/iso/19115/-3/mco/1.0"
                xmlns:mda="http://standards.iso.org/iso/19115/-3/mda/2.0"
                xmlns:mex="http://standards.iso.org/iso/19115/-3/mex/1.0"
                xmlns:mrl="http://standards.iso.org/iso/19115/-3/mrl/2.0"
                xmlns:mmi="http://standards.iso.org/iso/19115/-3/mmi/1.0"
                xmlns:mpc="http://standards.iso.org/iso/19115/-3/mpc/1.0"
                xmlns:mrc="http://standards.iso.org/iso/19115/-3/mrc/2.0"
                xmlns:mrd="http://standards.iso.org/iso/19115/-3/mrd/1.0"
                xmlns:mri="http://standards.iso.org/iso/19115/-3/mri/1.0"
                xmlns:mrs="http://standards.iso.org/iso/19115/-3/mrs/1.0"
                xmlns:msr="http://standards.iso.org/iso/19115/-3/msr/2.0"
                xmlns:mdq="http://standards.iso.org/iso/19157/-2/mdq/1.1"
                xmlns:gco="http://standards.iso.org/iso/19115/-3/gco/1.0"
                xmlns:gcx="http://standards.iso.org/iso/19115/-3/gcx/1.0"
                xmlns:gwm="http://standards.iso.org/iso/19115/-3/gwm/1.0"
                xmlns:mdb="http://standards.iso.org/iso/19115/-3/mdb/2.0"
                xmlns:gml="http://www.opengis.net/gml/3.2"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
                xmlns:mds="http://standards.iso.org/iso/19115/-3/mds/2.0"
                xmlns:mdt="http://standards.iso.org/iso/19115/-3/mdt/2.0"
                exclude-result-prefixes="#all">
  <!--  
                xmlns:mic="http://standards.iso.org/iso/19115/-3/mic/1.0"
                xmlns:mil="http://standards.iso.org/iso/19115/-3/mil/1.0"
                xmlns:mai="http://standards.iso.org/iso/19115/-3/mai/1.0"
                xmlns:gmd="http://www.isotc211.org/2005/gmd"
                xmlns:gcoold="http://www.isotc211.org/2005/gco"
                xmlns:gmi="http://www.isotc211.org/2005/gmi"
                xmlns:gmx="http://www.isotc211.org/2005/gmx"
                xmlns:gsr="http://www.isotc211.org/2005/gsr"
                xmlns:gss="http://www.isotc211.org/2005/gss"
                xmlns:gts="http://www.isotc211.org/2005/gts"
                xmlns:srvold="http://www.isotc211.org/2005/srv"
                xmlns:gml30="http://www.opengis.net/gml"
  -->
  
  <!-- 
  <xsl:import href="utility/create19115-3Namespaces.xsl"/>

   <xsl:import href="utility/dateTime.xsl"/>
  <xsl:import href="utility/multiLingualCharacterStrings.xsl"/>
-->
  <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
    <xd:desc>
      <xd:p>
        <xd:b>Created on:</xd:b>November 11, 2020 </xd:p>
      <xd:p>Translates from ISO 19115-3 V.1.0 for ISO 19115-1 and ISO 19115-2 to ISO 19115-1 V.1.3 and ISO 19115 V.2.1 and ISO 19103 v.1.1</xd:p>
      <xd:p>
        <xd:b>Version November 20, 2020</xd:b>
        <xd:ul>
          <xd:li>Converged the 19115-3 transform into 19115-1 and ISO 19115-2 namespace URIs</xd:li>
        </xd:ul>
      </xd:p>
      <xd:p><xd:b>Author 1:</xd:b>BARLOW Melanie - melanie.barlow@ardc.edu.au</xd:p>
      <xd:p><xd:b>Responsibility:</xd:b>BLEYS Evert - ejbleys@gmail.com</xd:p>
    </xd:desc>
  </xd:doc>

  <xsl:output method="xml" version="1.1" indent="yes" omit-xml-declaration="no" undeclare-prefixes="yes"/>

  <xsl:strip-space elements="*"/>

  <xsl:variable name="stylesheetVersion" select="'0.1'"/>
  
  <xsl:template match="/">
    <xsl:variable name="allOutputXML" as="node()*">
     <xsl:copy>
       <xsl:apply-templates select="node()|@*"/>
     </xsl:copy>
    </xsl:variable>
    <xsl:for-each select="$allOutputXML">
      <xsl:copy-of select="."/>
    </xsl:for-each>
  </xsl:template>
  
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="mdb:MD_Metadata">
      <xsl:element name="mdb:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mdb/1.3" >
         <xsl:namespace name="cit" select="'https://schemas.isotc211.org/19115/-1/cit/1.3'"/>
        <xsl:namespace name="gex" select="'https://schemas.isotc211.org/19115/-1/gex/1.3'"/>
        <xsl:namespace name="lan" select="'https://schemas.isotc211.org/19115/-1/lan/1.3'"/>
        <xsl:namespace name="mas" select="'https://schemas.isotc211.org/19115/-1/mas/1.3'"/>
        <xsl:namespace name="mcc" select="'https://schemas.isotc211.org/19115/-1/mcc/1.3'"/>
        <xsl:namespace name="mco" select="'https://schemas.isotc211.org/19115/-1/mco/1.3'"/>
        <xsl:namespace name="mda" select="'https://schemas.isotc211.org/19115/-1/mda/1.3'"/>
        <xsl:namespace name="mdb" select="'https://schemas.isotc211.org/19115/-1/mdb/1.3'"/>
        <xsl:namespace name="mex" select="'https://schemas.isotc211.org/19115/-1/mex/1.3'"/>
        <xsl:namespace name="mmi" select="'https://schemas.isotc211.org/19115/-1/mmi/1.3'"/>
        <xsl:namespace name="mpc" select="'https://schemas.isotc211.org/19115/-1/mpc/1.3'"/>
        <xsl:namespace name="mrc" select="'https://schemas.isotc211.org/19115/-1/mrc/1.3'"/>
        <xsl:namespace name="mrd" select="'https://schemas.isotc211.org/19115/-1/mrd/1.3'"/>
        <xsl:namespace name="mri" select="'https://schemas.isotc211.org/19115/-1/mri/1.3'"/>
        <xsl:namespace name="mrl" select="'https://schemas.isotc211.org/19115/-1/mrl/1.3'"/>
        <xsl:namespace name="mrs" select="'https://schemas.isotc211.org/19115/-1/mrs/1.3'"/>
        <xsl:namespace name="msr" select="'https://schemas.isotc211.org/19115/-1/msr/1.3'"/>
        <xsl:namespace name="srv" select="'https://schemas.isotc211.org/19115/-1/srv/1.3'"/>
        <xsl:namespace name="mac" select="'https://schemas.isotc211.org/19115/-2/mac/2.2'"/>
        <xsl:namespace name="gco" select="'https://schemas.isotc211.org/19103/-/gco/1.2'"/>
        <xsl:namespace name="gcx" select="'https://schemas.isotc211.org/19103/-/gcx/1.2'"/>
        <xsl:namespace name="gfc" select="'https://schemas.isotc211.org/19110/-/gfc/2.2'"/>
        <xsl:namespace name="fcc" select="'https://schemas.isotc211.org/19110/-/fcc/2.2'"/>
        <xsl:namespace name="gwm" select="'https://schemas.isotc211.org/19136/-/gwm/1.1'"/>
        <xsl:namespace name="gml" select="'https://www.opengis.net/gml/3.2'"/>
        <xsl:namespace name="cat" select="'https://schemas.isotc211.org/19139/-/cat/1.2'"/>
        <xsl:namespace name="mdq" select="'https://schemas.isotc211.org/19157/-/mdq/1.2'"/>
        <xsl:namespace name="xsi" select="'http://www.w3.org/2001/XMLSchema-instance'"/>
        <xsl:namespace name="xlink" select="'http://www.w3.org/1999/xlink'"/>
        <!--
          <xsl:attribute name="xsi:schemaLocation" select="'
          https://schemas.isotc211.org/19115/-1/cit/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/cit/1.3.0/cit.xsd
          https://schemas.isotc211.org/19115/-1/gex/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/gex/1.3.0/gex.xsd
          https://schemas.isotc211.org/19115/-1/lan/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/lan/1.3.0/lan.xsd
          https://schemas.isotc211.org/19115/-1/mas/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mas/1.3.0/mas.xsd
          https://schemas.isotc211.org/19115/-1/mcc/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mcc/1.3.0/mcc.xsd
          https://schemas.isotc211.org/19115/-1/mco/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mco/1.3.0/mco.xsd
          https://schemas.isotc211.org/19115/-1/mda/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mda/1.3.0/mda.xsd
          https://schemas.isotc211.org/19115/-1/mdb/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mdb/1.3.0/mdb.xsd
          https://schemas.isotc211.org/19115/-1/mex/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mex/1.3.0/mex.xsd
          https://schemas.isotc211.org/19115/-1/mmi/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mmi/1.3.0/mmi.xsd
          https://schemas.isotc211.org/19115/-1/mpc/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mpc/1.3.0/mpc.xsd
          https://schemas.isotc211.org/19115/-1/mrc/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mrc/1.3.0/mrc.xsd
          https://schemas.isotc211.org/19115/-1/mrd/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mrd/1.3.0/mrd.xsd
          https://schemas.isotc211.org/19115/-1/mri/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mri/1.3.0/mri.xsd
          https://schemas.isotc211.org/19115/-1/mrl/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mrl/1.3.0/mrl.xsd
          https://schemas.isotc211.org/19115/-1/mrs/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/mrs/1.3.0/mrs.xsd
          https://schemas.isotc211.org/19115/-1/msr/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/msr/1.3.0/msr.xsd
          https://schemas.isotc211.org/19115/-1/srv/1.3 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-1/srv/1.3.0/srv.xsd
          https://schemas.isotc211.org/19115/-2/mac/2.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19115/-2/mac/2.2.0/mac.xsd
          https://schemas.isotc211.org/19139/-/cat/1.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19139/-/cit/1.2.0/cat.xsd
          https://schemas.isotc211.org/19103/-/gco/1.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19103/-/gco/1.2.0/gco.xsd
          https://schemas.isotc211.org/19103/-/gcx/1.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19103/-/gcx/1.1.0/gcx.xsd
          https://schemas.isotc211.org/19110/-/gfc/2.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19110/-/gfc/2.2.0/gfc.xsd
          https://schemas.isotc211.org/19110/-/fcc/2.2 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19110/-/fcc/2.2.0/fcc.xsd
          https://schemas.isotc211.org/19157/-2/mdq/1.1 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19157/-3/mdq/1.1.0/mdq.xsd
          https://schemas.isotc211.org/19136/-/gwm/1.1 https://raw.githubusercontent.com/ISO-TC211/XML/master/schemas.isotc211.org/19115Restructure/19136/-/gwm/1.1.0/gwm.xsd
          http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd 
          http://www.w3.org/1999/xlink http://www.w3.org/1999/xlink.xsd'"/>
        -->
        
        <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="cat:*">
    <xsl:element name="cat:{local-name()}" namespace="https://schemas.isotc211.org/19115/-3/cat/1.0" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="cit:*">
    <xsl:element name="cit:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/cit/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="fcc:*">
    <xsl:element name="fcc:{local-name()}" namespace="https://schemas.isotc211.org/19110/-/fcc/1.0" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="gex:*">
    <xsl:element name="gex:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/gex/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="gfc:*">
    <xsl:element name="gfc:{local-name()}" namespace="https://schemas.isotc211.org/19110/-/gfc/1.0" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="gcx:*">
    <xsl:element name="gcx:{local-name()}" namespace="https://schemas.isotc211.org/19136/-/gcx/1.1" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="gco:*">
    <xsl:element name="gco:{local-name()}" namespace="https://schemas.isotc211.org/19103/-/gco/1.2" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="gml:*">
    <xsl:element name="gml:{local-name()}" namespace="http://www.opengis.net/gml/3.2" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="lan:*">
    <xsl:element name="lan:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/lan/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mac:*">
    <xsl:element name="mac:{local-name()}" namespace="https://schemas.isotc211.org/19115/-2/mac/2.2" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <!-- xmlns:mai="http://standards.iso.org/iso/19115/-3/mai/1.0" -->
  
  <!--    xmlns:mic="http://standards.iso.org/iso/19115/-3/mic/1.0"-->
  
  <!--  xmlns:mil="http://standards.iso.org/iso/19115/-3/mil/1.0" -->
  
  <xsl:template match="mas:*">
    <xsl:element name="mas:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mas/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mcc:*">
    <xsl:element name="mcc:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mcc/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <!--   xmlns:mds="http://standards.iso.org/iso/19115/-3/mds/1.0" -->
  
  <xsl:template match="mco:*">
    <xsl:element name="mco:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mco/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mda:*">
    <xsl:element name="mda:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mda/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mdb:*[not(local-name() ='MD_Metadata')]">
    <xsl:element name="mdb:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mdb/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mdq:*">
    <xsl:element name="mdq:{local-name()}" namespace="https://schemas.isotc211.org/19157/-2/mdq/1.1" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <!--xmlns:mdt="http://standards.iso.org/iso/19115/-3/mdt/1.0"-->
  
  <xsl:template match="mdt:*">
    <xsl:element name="mdq:{local-name()}" namespace="https://schemas.isotc211.org/19157/-2/mdq/1.1" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mex:*">
    <xsl:element name="mex:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mex/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mmi:*">
    <xsl:element name="mmi:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mmi/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mpc:*">
    <xsl:element name="mpc:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mpc/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mrc:*">
    <xsl:element name="mrc:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mrc/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mrd:*">
    <xsl:element name="mrd:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mrd/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mri:*">
    <xsl:element name="mri:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mri/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mrl:*">
    <xsl:element name="mrl:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mrl/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="mrs:*">
    <xsl:element name="mrs:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/mrs/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="srv:*">
    <xsl:element name="srv:{local-name()}" namespace="https://schemas.isotc211.org/19115/-1/srv/1.3" >
      <xsl:apply-templates select="node()|@*"/>
    </xsl:element>
  </xsl:template>
  
  
</xsl:stylesheet>