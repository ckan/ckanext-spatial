#!/bin/sh -e

nosetests --ckan --nologcapture --with-pylons=subdir/test.ini ckanext/spatial
