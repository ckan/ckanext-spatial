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


def _create_postgis_extension():
    Session.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    Session.commit()


def create_postgis_tables():
    _create_postgis_extension()


@pytest.fixture
def clean_postgis():
    Session.execute("DROP TABLE IF EXISTS package_extent")
    Session.execute("DROP EXTENSION IF EXISTS postgis CASCADE")
    Session.commit()

@pytest.fixture
def harvest_setup():
    harvest_model.setup()


@pytest.fixture
def spatial_setup():
    create_postgis_tables()
    spatial_db_setup()
