# -*- coding: utf-8 -*-

import pytest
import os
import re
from sqlalchemy import Table

from ckan.model import Session, meta
from ckanext.spatial.geoalchemy_common import postgis_version
from ckanext.spatial.model.package_extent import setup as spatial_db_setup
from ckanext.harvest.model import setup as harvest_model_setup
import ckanext.harvest.model as harvest_model


def _execute_script(script_path):

    conn = Session.connection()
    script = open(script_path, "r").read()
    for cmd in script.split(";"):
        cmd = re.sub(r"--(.*)|[\n\t]", "", cmd)
        if len(cmd):
            conn.execute(cmd)

    Session.commit()


def _create_postgis_extension():
    Session.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Session.commit()


def create_postgis_tables():
    _create_postgis_extension()
    scripts_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "scripts"
    )
    if postgis_version()[:1] == "1":
        _execute_script(os.path.join(scripts_path, "spatial_ref_sys.sql"))
        _execute_script(os.path.join(scripts_path, "geometry_columns.sql"))
    else:
        _execute_script(os.path.join(scripts_path, "spatial_ref_sys.sql"))


@pytest.fixture
def clean_postgis():
    Session.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
    Session.commit()


@pytest.fixture
def spatial_clean_db(reset_db):
    reset_db()

    # This will create the PostGIS tables (geometry_columns and
    # spatial_ref_sys) which were deleted when rebuilding the database
    table = Table("spatial_ref_sys", meta.metadata)
    if not table.exists():
        create_postgis_tables()

        # When running the tests with the --reset-db option for some
        # reason the metadata holds a reference to the `package_extent`
        # table after being deleted, causing an InvalidRequestError
        # exception when trying to recreate it further on
        if "package_extent" in meta.metadata.tables:
            meta.metadata.remove(meta.metadata.tables["package_extent"])

    spatial_db_setup()

    # Setup the harvest tables
    harvest_model_setup()


@pytest.fixture
def harvest_setup():
    harvest_model.setup()


@pytest.fixture
def spatial_setup():
    # This will create the PostGIS tables (geometry_columns and
    # spatial_ref_sys) which were deleted when rebuilding the database
    table = Table("spatial_ref_sys", meta.metadata)
    if not table.exists():
        create_postgis_tables()

    # When running the tests with the --reset-db option for some
    # reason the metadata holds a reference to the `package_extent`
    # table after being deleted, causing an InvalidRequestError
    # exception when trying to recreate it further on
    if "package_extent" in meta.metadata.tables:
        meta.metadata.remove(meta.metadata.tables["package_extent"])
        Session.execute("DROP INDEX IF EXISTS idx_package_extent_the_geom")
        Session.commit()

    spatial_db_setup()
