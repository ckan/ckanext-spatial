# -*- coding: utf-8 -*-

import pytest

import ckanext.harvest.model as harvest_model


@pytest.fixture
def harvest_setup():
    harvest_model.setup()
