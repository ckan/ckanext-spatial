import os
from pkg_resources import resource_stream, resource_filename
from ckanext.spatial.model import GeminiDocument

from lxml import etree

log = __import__("logging").getLogger(__name__)

class BaseValidator(object):
    '''Base class for a validator.'''
    name = None
    title = None

    @classmethod
    def is_valid(cls, xml):
        '''
        Runs the validation on the supplied XML etree.
        Returns tuple:
          (is_valid, error_message_list)
        '''
        raise NotImplementedError

class XsdValidator(BaseValidator):
    '''Base class for validators that use an XSD schema.'''

    @classmethod
    def _is_valid(cls, xml, xsd_filepath, xsd_name):
        '''Returns whether or not an XML file is valid according to
        an XSD.

        Params:
          xml - etree of the XML to be validated
          xsd_filepath - full path to the XSD file
          xsd_name - string describing the XSD

        Returns:
          (is_valid_boolean, list_of_error_message_strings)
        '''
        xsd = etree.parse(xsd_filepath)
        schema = etree.XMLSchema(xsd)
        # With libxml2 versions before 2.9, this fails with this error:
        #    gmx_schema = etree.XMLSchema(gmx_xsd)
        #  File "xmlschema.pxi", line 103, in lxml.etree.XMLSchema.__init__ (src/lxml/lxml.etree.c:116069)
        # XMLSchemaParseError: local list type: A type, derived by list or union, must have the simple ur-type definition as base type, not '{http://www.opengis.net/gml/3.2}doubleList'., line 118
        try:
            schema.assertValid(xml)
        except AssertionError, e:
            msg = '%s Schema Error: %s' % (xsd_name, e.args)
            return False, [msg]
        except etree.DocumentInvalid, e:
            msg = '%s Validation Error: %s' % (xsd_name, e.args)
            return False, [msg]
        return True, []


class ISO19139Schema(XsdValidator):
    name = 'iso19139'
    title = 'ISO19139 XSD Schema'

    @classmethod
    def is_valid(cls, xml):
        xsd_path = 'xml/iso19139'
        gmx_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                            xsd_path, 'gmx/gmx.xsd')
        is_valid, errors = cls._is_valid(xml, gmx_xsd_filepath, 'Dataset schema (gmx.xsd)')
        return is_valid, errors

class ISO19139EdenSchema(XsdValidator):
    name = 'iso19139eden'
    title = 'ISO19139 XSD Schema (EDEN)'

    @classmethod
    def is_valid(cls, xml):
        xsd_path = 'xml/iso19139eden'

        metadata_type = cls.get_record_type(xml)

        if metadata_type in ('dataset', 'series'):
            gmx_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                            xsd_path, 'gmx/gmx.xsd')
            is_valid, errors = cls._is_valid(xml, gmx_xsd_filepath, 'Dataset schema (gmx.xsd)')
        elif metadata_type == 'service':
            gmx_and_srv_xsd_filepath = os.path.join(os.path.dirname(__file__),
                                                    xsd_path, 'gmx_and_srv.xsd')
            is_valid, errors = cls._is_valid(xml, gmx_and_srv_xsd_filepath, 'Service schemas (gmx.xsd & srv.xsd)')
        else:
            is_valid = False
            errors = ['Metadata type not recognised "%s" - cannot choose an ISO19139 validator.' %
                      metadata_type]
        if is_valid:
            return True, []

        return False, errors

    @classmethod
    def get_record_type(cls, xml):
        '''
        For a given ISO19139 record, returns the "type"
        e.g. "dataset", "series", "service"

        xml - etree of the ISO19139 XML record
        '''
        gemini = GeminiDocument(xml_tree=xml)
        return gemini.read_value('resource-type')

class SchematronValidator(BaseValidator):
    '''Base class for a validator that uses Schematron.'''
    has_init = False

    @classmethod
    def get_schematrons(cls):
        '''Subclasses should override this method to implement
        their validation.'''
        raise NotImplementedError

    @classmethod
    def is_valid(cls, xml):
        if not hasattr(cls, 'schematrons'):
            log.info('Compiling schematron "%s"', cls.title)
            cls.schematrons = cls.get_schematrons()
        for schematron in cls.schematrons:
            result = schematron(xml)
            errors = []
            for element in result.findall("{http://purl.oclc.org/dsdl/svrl}failed-assert"):
                errors.append(element)
            if len(errors) > 0:
                messages_already_reported = set()
                error_details = []
                for error in errors:
                    message, details = cls.extract_error_details(error)
                    if not message in messages_already_reported:
                        error_details.append(details)
                        messages_already_reported.add(message)
                return False, error_details
        return True, []

    @classmethod
    def extract_error_details(cls, failed_assert_element):
        '''Given the XML Element describing a schematron test failure,
        this method extracts the strings describing the failure and returns
        them.

        Returns:
           (error_message, fuller_error_details)
        '''
        assert_ = failed_assert_element.get('test')
        location = failed_assert_element.get('location')
        message_element = failed_assert_element.find("{http://purl.oclc.org/dsdl/svrl}text")
        message = message_element.text.strip()
        failed_assert_element
        return message, 'Error Message: "%s"  Error Location: "%s"  Error Assert: "%s"' % (message, location, assert_)

    @classmethod
    def schematron(cls, schema):
        transforms = [
            "validation/xml/schematron/iso_dsdl_include.xsl",
            "validation/xml/schematron/iso_abstract_expand.xsl",
            "validation/xml/schematron/iso_svrl_for_xslt1.xsl",
            ]
        if isinstance(schema, file):
            compiled = etree.parse(schema)
        else:
            compiled = schema
        for filename in transforms:
            with resource_stream("ckanext.spatial", filename) as stream:
                xform_xml = etree.parse(stream)
                xform = etree.XSLT(xform_xml)
                compiled = xform(compiled)
        return etree.XSLT(compiled)


class ConstraintsSchematron(SchematronValidator):
    name = 'constraints'
    title = 'ISO19139 Table A.1 Constraints Schematron 1.3'

    @classmethod
    def get_schematrons(cls):
        with resource_stream("ckanext.spatial",
                             "validation/xml/medin/ISOTS19139A1Constraints_v1.3.sch") as schema:
            return [cls.schematron(schema)]


class Gemini2Schematron(SchematronValidator):
    name = 'gemini2'
    title = 'GEMINI 2.1 Schematron 1.2'

    @classmethod
    def get_schematrons(cls):
        with resource_stream("ckanext.spatial",
                             "validation/xml/gemini2/gemini2-schematron-20110906-v1.2.sch") as schema:
            return [cls.schematron(schema)]

all_validators = (ISO19139Schema,
                  ISO19139EdenSchema,
                  ConstraintsSchematron,
                  Gemini2Schematron)


class Validators(object):
    '''
    Validates XML against one or more profiles (i.e. validators).
    '''
    def __init__(self, profiles=["iso19139", "constraints", "gemini2"]):
        self.profiles = profiles

    def isvalid(self, xml):
        '''For backward compatibility'''
        return self.is_valid(xml)

    def is_valid(self, xml):
        if not hasattr(self, 'validators'):
            self.validators = {} # name: class
            for validator_class in all_validators:
                self.validators[validator_class.name] = validator_class
        for name in self.profiles:
            validator = self.validators[name]
            is_valid, error_message_list = validator.is_valid(xml)
            if not is_valid:
                error_message_list.insert(0, 'Validating against "%s" profile failed' % validator.title)
                log.info('%r', error_message_list)
                return False, error_message_list
            log.info('Validated against "%s"', validator.title)
        log.info('Validation passed')
        return True, []

if __name__ == '__main__':
    from sys import argv
    import logging
    from pprint import pprint
    logging.basicConfig()

    if len(argv) == 3:
        profiles = argv[2].split(',')
    else:
        profiles = ["iso19139", "constraints", "gemini2"]
    v = Validators(profiles)
    result = v.is_valid(etree.parse(open(argv[1])))
    pprint(result)
