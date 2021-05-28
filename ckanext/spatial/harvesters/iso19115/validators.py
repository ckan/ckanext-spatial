#####################################################
# VALIDATORS
#####################################################
import os
from pkg_resources import resource_stream
import ckanext.spatial.validation.validation as validation
XsdValidator = validation.XsdValidator
SchematronValidator = validation.SchematronValidator

class ISO19115_Schema(XsdValidator):
    name = 'iso19115-3.2018'
    title = 'ISO19115 XSD Schema'

    @classmethod
    def is_valid(cls, xml):
        xsd_path = 'schemas/standards.iso.org/19115/-3'
        mdb_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                        xsd_path, 'mdb/2.0/mdb.xsd')
        xsd_name = 'Dataset schema 3.2018 (mdb.xsd)'
        is_valid, errors = cls._is_valid(xml, mdb_xsd_filepath, xsd_name)
        if not is_valid:
            # TODO: not sure if we need this one,
            # keeping for backwards compatibility
            errors.insert(0, ('{0} Validation Error'.format(xsd_name), None))
        return is_valid, errors


class ISO19115_2_Schema(XsdValidator):
    name = 'iso19115-2'
    title = 'ISO19115 XSD Schema'

    @classmethod
    def is_valid(cls, xml):
        xsd_path = 'schemas/standards.iso.org/19115/-3'
        mdb_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                        xsd_path, 'mdb/1.0/mdb.xsd')
        xsd_name = 'Dataset schema 2.0 (mdb.xsd)'
        is_valid, errors = cls._is_valid(xml, mdb_xsd_filepath, xsd_name)
        if not is_valid:
            # TODO: not sure if we need this one,
            # keeping for backwards compatibility
            errors.insert(0, ('{0} Validation Error'.format(xsd_name), None))
        return is_valid, errors

class ISO19115_1_Schema(XsdValidator):
    name = 'iso19115-1'
    title = 'ISO19115-3 v1.0 XSD Schema'

    @classmethod
    def is_valid(cls, xml):
        xsd_path = 'schemas/standards.iso.org/19115/-3'
        mdb_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                        xsd_path, 'mds/1.0/mds.xsd')
        xsd_name = 'Dataset schema 1.0 (mdb.xsd)'
        is_valid, errors = cls._is_valid(xml, mdb_xsd_filepath, xsd_name)
        if not is_valid:
            # TODO: not sure if we need this one,
            # keeping for backwards compatibility
            errors.insert(0, ('{0} Validation Error'.format(xsd_name), None))
        return is_valid, errors

class ISO19115_Schematron(SchematronValidator):
    name = 'iso19115schematron'
    title = 'ISO19115 Schematron'

    @classmethod
    def get_schematrons(cls):
        with resource_stream(
                __name__,
                "schemas/standards.iso.org/19115/-3/mdb/2.0/mdb.sch") as schema:

            return [cls.schematron(schema)]
