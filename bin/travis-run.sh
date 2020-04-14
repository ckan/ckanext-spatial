#!/bin/sh -e

if [ $CKANVERSION == 'master' ]
then
    pytest --ckan-ini=subdir/test.ini ckanext/spatial/tests
else
    nosetests --ckan --nologcapture --with-pylons=subdir/test.ini ckanext/spatial/tests/nose
fi
