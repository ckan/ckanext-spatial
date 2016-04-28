#!/bin/bash
set -e

echo "This is travis-build.bash..."

echo "Installing the packages that CKAN requires..."
sudo apt-get update -qq
sudo apt-get install postgresql-9.1 solr-jetty libcommons-fileupload-java:amd64=1.2.2-1

echo "Installing PostGIS..."
if [ $POSTGISVERSION == '1' ]
then
    sudo apt-get install postgresql-9.1-postgis=1.5.3-2
fi
# PostGIS 2.1 already installed on Travis

echo "Patching lxml..."
wget ftp://xmlsoft.org/libxml2/libxml2-2.9.0.tar.gz
tar zxf libxml2-2.9.0.tar.gz
cd libxml2-2.9.0/
./configure --quiet --libdir=/usr/lib/x86_64-linux-gnu
make --silent
sudo make --silent install
xmllint --version
cd -

echo "Installing CKAN and its Python dependencies..."
git clone https://github.com/ckan/ckan
cd ckan
if [ $CKANVERSION != 'master' ]
then
    git checkout release-v$CKANVERSION-latest
fi
python setup.py develop
pip install -r requirements.txt --allow-all-external
pip install -r dev-requirements.txt --allow-all-external
cd -

echo "Setting up Solr..."
# solr is multicore for tests on ckan master now, but it's easier to run tests
# on Travis single-core still.
# see https://github.com/ckan/ckan/issues/2972
sed -i -e 's/solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/' ckan/test-core.ini
printf "NO_START=0\nJETTY_HOST=127.0.0.1\nJETTY_PORT=8983\nJAVA_HOME=$JAVA_HOME" | sudo tee /etc/default/jetty
sudo cp ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
sudo service jetty restart

echo "Creating the PostgreSQL user and database..."
sudo -u postgres psql -c "CREATE USER ckan_default WITH PASSWORD 'pass';"
sudo -u postgres psql -c 'CREATE DATABASE ckan_test WITH OWNER ckan_default;'

echo "Setting up PostGIS on the database..."
if [ $POSTGISVERSION == '1' ]
then
    sudo -u postgres psql -d ckan_test -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
    sudo -u postgres psql -d ckan_test -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
    sudo -u postgres psql -d ckan_test -c 'ALTER TABLE geometry_columns OWNER TO ckan_default;'
    sudo -u postgres psql -d ckan_test -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan_default;'
elif [ $POSTGISVERSION == '2' ]
then
    sudo -u postgres psql -d ckan_test -c 'CREATE EXTENSION postgis;'
    sudo -u postgres psql -d ckan_test -c 'ALTER VIEW geometry_columns OWNER TO ckan_default;'
    sudo -u postgres psql -d ckan_test -c 'ALTER TABLE spatial_ref_sys OWNER TO ckan_default;'
fi

echo "Install other libraries required..."
sudo apt-get install python-dev libxml2-dev libxslt1-dev libgeos-c1

echo "Initialising the database..."
cd ckan
paster db init -c test-core.ini
cd -

echo "Installing ckanext-harvest and its requirements..."
git clone https://github.com/ckan/ckanext-harvest
cd ckanext-harvest
python setup.py develop
pip install -r pip-requirements.txt --allow-all-external

paster harvester initdb -c ../ckan/test-core.ini
cd -

echo "Installing ckanext-spatial and its requirements..."
pip install -r pip-requirements.txt --allow-all-external
python setup.py develop


echo "Moving test.ini into a subdir..."
mkdir subdir
mv test.ini subdir

paster spatial initdb -c subdir/test.ini

echo "travis-build.bash is done."
