#!/bin/sh -e

pytest --ckan-ini=subdir/test.ini ckanext/spatial/tests
