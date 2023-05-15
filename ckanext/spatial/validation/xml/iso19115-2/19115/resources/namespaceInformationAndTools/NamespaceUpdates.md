# Namespace Updates
##2019-01-03
Migration of schemas from standards.iso.org/iso to schemas.isotc211.org
The namespace information file (__ISONamespaceInformation.xml__) does not contain standards.iso.org/iso... so it looks like no change is required there. There are <location> elements that were updated by the general migration script to <location>https://schemas.isotc211.org</location>.

Run the makeNamespaceTable.xsl on __ISONamespaceInformation.xml__ to create ../namespaceSummary.html. This is the oxygen transform scenario titled "Write  ISO Namespace Table" with the location of the xsl file adjusted to the schemas.isotc211.org version. 
 

##2018-03-06

## Namespace Table
Five base namespaces have been updated to new versions: ./19115/-3/msr/2.0, ./19115/-3/mrc/2.0, ./19115/-3/mrl/2.0, ./19115/-3/mac/2.0, ./19115/-3/cit/2.0 

### Update the XML file that contains information about the namespaces (__ISONamespaceInformation.xml__):
1. Version 2 of cit, mac, md1, md2, mda, mdb, mds, mdt, mrc, mrl, msr added


### Update the makeNamespaceTable.xsl that produces the HTML table of namespace information. 
1. Include the version numbers in the imported namespaces

## New Versions of Wrapper Namespaces
There are several namespaces that serve as wrappers for groups of namespaces that are used together. These need to be updated to import Version 2 of the appropriate namespaces.

1. Metadata Base (mdb) imports cit. 
2. Metadata for Data and Services (mds) imports mac, mrc, mrl, msr, mdb. In this case metadataDataServices.xsd only imports mds.xsd so no changes required there.
3. Metadata for Data and Services with Geospatial Common Extensions (md1) imports cit, mds.
4. Metadata with Extended Services (md2) imports cit, md1.
5. MetaData Application (mda) imports md2, mdb.
6. Metadata for Data Transfer (mdt) imports mda.

### Version 2.0 Directories
The namespaces with the new versions are:

ISOTC211-XML/XML/standards.iso.org/iso  
find . -type d -name 2.0 -print  
./19115/-3/cit/2.0  
./19115/-3/mac/2.0  
./19115/-3/md1/2.0  
./19115/-3/md2/2.0  
./19115/-3/mda/2.0  
./19115/-3/mdb/2.0  
./19115/-3/mds/2.0  
./19115/-3/mdt/2.0  
./19115/-3/mrc/2.0  
./19115/-3/mrl/2.0  
./19115/-3/msr/2.0  
./19115/-3/srv/2.0  

## Creating the Namespace Summary
The namespace summary is an html file (standards.iso.org/iso/19115/-3/resources/namespaceSummary.html. It contains information from the standards.iso.org/iso/19115/-3/resources/namespaceInformationAndTools/ISONamespaceInformation.xml file converted to html using standards.iso.org/iso/19115/-3/resources/namespaceInformationAndTools/makdNamespaceTable.xsl. This xsl has several input parameters:  

__Parameter schemaRootDirectory__:  
This is the root of the schema directories.  
Example: /Users/tedhabermann/GitRepositories/ISOTC211-XML/XML/standards.iso.org/iso 

__Parameter standard__:  
This is a space delimited list of the schemaStandardNumbers to be included in the output.  
Namespaces whose schemaStandardNumber is in this list will be included in the output.  
Example: 19115-3 19157-2 19110 19111 19135

__Parameter workingVersionDate__:  
This is the date associated with a working version of the schema. It is in the format /YYYY-MM-DD. 
NOTE THE SLASH INCLUDED BEFORE THE DATE
Example: /2014-12-25

The output of this transform is written into standards.iso.org/iso/19115/-3/resources//namespaceSummary.html which is the summary of all namespaces.  

## Codelist files
The transform ISOTC211-XML/XML/standards.iso.org/iso/19115/resources/transforms/CT_CodelistCatalougue2HTML.xsl is used to create html versions of the codelist.xml files in each nemespace directory. This should be done before the index.html files are created so that the codelist.xml and codelist.html files will be included in the index files.

## Sample XML files
Sample XML files are created for each namespace inorder to illustrate new capabilities and correct namespaces and schema locations. This should be done before the index.html files are created so that the sample files will be included in the index files.

## index.html files
Run the xsl ISOTC211-XML/XML/standards.iso.org/iso/19115/resources/namespaceInformationAndTools/writeHTMLFiles.xsl on ISONamespaceInformation.xml to create index.html files in all of the namespace directories. The names of the files that are written are in writeHTMLFilesLog.html.

## Zip files
The script XML/MaintenanceTools/makeAllZipFiles.sh creates all of the zip files in the repository. The names of the files are written into zipFileList.txt. This script should be run last so that all of the zip files are up-to-date.

## Instance Document
The current instance document header is:

```
<mdb:MD_Metadata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
   xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:mcc="http://standards.iso.org/iso/19115/-3/mcc/1.0" 
   xmlns:mmi="http://standards.iso.org/iso/19115/-3/mmi/1.0" xmlns:cat="http://standards.iso.org/iso/19115/-3/cat/1.0"
   xmlns:lan="http://standards.iso.org/iso/19115/-3/lan/1.0" xmlns:gco="http://standards.iso.org/iso/19115/-3/gco/1.0" 
   xmlns:mco="http://standards.iso.org/iso/19115/-3/mco/1.0" xmlns:gex="http://standards.iso.org/iso/19115/-3/gex/1.0" 
   xmlns:gcx="http://standards.iso.org/iso/19115/-3/gcx/1.0" xmlns:mas="http://standards.iso.org/iso/19115/-3/mas/1.0" 
   xmlns:mrd="http://standards.iso.org/iso/19115/-3/mrd/1.0" xmlns:mrc="http://standards.iso.org/iso/19115/-3/mrc/2.0" 
   xmlns:mex="http://standards.iso.org/iso/19115/-3/mex/1.0" xmlns:mpc="http://standards.iso.org/iso/19115/-3/mpc/1.0" 
   xmlns:mri="http://standards.iso.org/iso/19115/-3/mri/1.0" xmlns:mda="http://standards.iso.org/iso/19115/-3/mda/1.0" 
   xmlns:mrs="http://standards.iso.org/iso/19115/-3/mrs/1.0" xmlns:srv="http://standards.iso.org/iso/19115/-3/srv/2.0" 
   xmlns:mdq="http://standards.iso.org/iso/19157/-2/mdq/1.0" xmlns:xlink="http://www.w3.org/1999/xlink" 
   xmlns:msr="http://standards.iso.org/iso/19115/-3/msr/2.0" xmlns:cit="http://standards.iso.org/iso/19115/-3/cit/2.0"  
   xmlns:mdb="http://standards.iso.org/iso/19115/-3/mdb/2.0"
   xmlns:mdt="http://standards.iso.org/iso/19115/-3/mdt/2.0" xmlns:mds="http://standards.iso.org/iso/19115/-3/mds/2.0" 
   xmlns:mac="http://standards.iso.org/iso/19115/-3/mac/2.0" xmlns:mrl="http://standards.iso.org/iso/19115/-3/mrl/2.0"
   xsi:schemaLocation="http://standards.iso.org/iso/19115/-3/mdb/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mdt/2.0/mdt.xsd 
   http://standards.iso.org/iso/19115/-3/mac/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mac/2.0/mac.xsd
   http://standards.iso.org/iso/19115/-3/mdb/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mdb/2.0/mdb.xsd
   http://standards.iso.org/iso/19115/-3/mrl/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mrl/2.0/mrl.xsd
   http://standards.iso.org/iso/19115/-3/mdt/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mdt/2.0/mdt.xsd
   http://standards.iso.org/iso/19115/-3/mrc/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/mrc/2.0/mrc.xsd
   http://standards.iso.org/iso/19115/-3/msr/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/msr/2.0/msr.xsd
   http://standards.iso.org/iso/19115/-3/cit/2.0 ../../../ISOTC211-XML/XML/standards.iso.org/19115/-3/cit/2.0/cit.xsd">
```

