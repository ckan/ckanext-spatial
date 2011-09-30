These are custom builds of the OpenLayers Javascript mapping library,
slimmed down to only contain the features we need.

The files *.cfg contain the build profile used to build OpenLayers.
In order to add more functionality, new classes must be added in the
build profile, and then run the build command from the OpenLayers
distribution:

1. Download OpenLayers source code from http://openlayers.org

2. Modify the cfg file

3. Go to build/ and execute::

    python build.py {path-to-ckan.cfg} {output-file}
    
These builds have been obtained using the Closure Compiler. Please refer
to the build/README.txt on the OpenLayers Source Code for more details.

    python build.py -c closure {path-to-ckan.cfg} {output-file}


The theme used for the OpenLayers controls is the "dark" theme made available
by Development Seed under the BSD License:

https://github.com/developmentseed/openlayers_themes/blob/master/LICENSE.txt

The default map marker is derived from an icon available at The Noun Project:

http://thenounproject.com/
