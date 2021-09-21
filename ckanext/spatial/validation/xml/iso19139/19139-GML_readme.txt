For the sake of convenience, GML 3.2 XML schemas (version 19136 DIS - 2005 november) are (temporarily) provided with the 19139 set of schemas. The following changes were applied to the GML schemas to enable locale referencing:

-1- "referenceSystems.xsd" :

a)replace
   <import namespace="http://www.isotc211.org/schemas/2005/gmd" schemaLocation="../iso19139/gmd/gmd.xsd"/>
with
   <import namespace="http://www.isotc211.org/2005/gmd" schemaLocation="../gmd/gmd.xsd"/>

b) replace
   xmlns:gmd="http://www.isotc211.org/schemas/2005/gmd"
with
   xmlns:gmd="http://www.isotc211.org/2005/gmd"



-2- "coordinateOperations.xsd" :

a) replace
   <import namespace="http://www.isotc211.org/schemas/2005/gmd" schemaLocation="../iso19139/gmd/gmd.xsd"/>
with
   <import namespace="http://www.isotc211.org/2005/gmd" schemaLocation="../gmd/gmd.xsd"/>

b) replace
   xmlns:gmd="http://www.isotc211.org/schemas/2005/gmd"
with
   xmlns:gmd="http://www.isotc211.org/2005/gmd"