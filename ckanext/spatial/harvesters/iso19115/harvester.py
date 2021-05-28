import re
import six
from six.moves.urllib.parse import urlparse, urlunparse, urlencode

import logging
from lxml import etree

from ckan import model
from ckan import plugins as p
from ckantoolkit import config

from ckan.lib.navl.validators import not_empty
from ckan import logic

from ckan.plugins.core import SingletonPlugin, implements

from ckanext.harvest.interfaces import IHarvester
from ckanext.harvest.model import HarvestObject

from ckanext.spatial.harvesters.csw import CSWHarvester
from ckanext.spatial.interfaces import ISpatialHarvester

from ckanext.spatial.harvesters.iso19115.model import ISO19115Document

class ISO19115Harvester(CSWHarvester, SingletonPlugin):
    '''
    A Harvester for CSW servers
    '''
    implements(IHarvester)

    # def __init__(self):
        #_csw = CSWHarvester()
        # super(SpatialHarvester, self).__init__()

# IHarvester

    # From parent
    def info(self):
        '''
        Harvesting implementations must provide this method, which will return
        a dictionary containing different descriptors of the harvester. The
        returned dictionary should contain:

        * name: machine-readable name. This will be the value stored in the
            database, and the one used by ckanext-harvest to call the appropiate
            harvester.
        * title: human-readable name. This will appear in the form's select box
            in the WUI.
        * description: a small description of what the harvester does. This
            will appear on the form as a guidance to the user.

        A complete example may be::

            {
                'name': 'csw',
                'title': 'CSW Server',
                'description': 'A server that implements OGC's Catalog Service
                                for the Web (CSW) standard'
            }

        :returns: A dictionary with the harvester descriptors
        '''
        return {
            'name': 'iso19115_csw_harvester',
            'title': 'ISO19115 CSW based',
            'description': 'A server that implements OGC\'s Catalog Service for the Web (CSW) standard'
            }

    # From parent CSWHarvester
    # From parent SpatialHarvester
    # def validate_config(self, config):
        # '''

        # [optional]

        # Harvesters can provide this method to validate the configuration
        # entered in the form. It should return a single string, which will be
        # stored in the database.  Exceptions raised will be shown in the form's
        # error messages.

        # :param harvest_object_id: Config string coming from the form
        # :returns: A string with the validated configuration options
        # '''
        # # Delegate
        # return self._csw.validate_config(config)

    # From parent CSWHarvester
    # def get_original_url(self, harvest_object_id):
        # '''
        # [optional]

        # This optional but very recommended method allows harvesters to return
        # the URL to the original remote document, given a Harvest Object id.
        # Note that getting the harvest object you have access to its guid as
        # well as the object source, which has the URL.
        # This URL will be used on error reports to help publishers link to the
        # original document that has the errors. If this method is not provided
        # or no URL is returned, only a link to the local copy of the remote
        # document will be shown.

        # Examples:
        #     * For a CKAN record: http://{ckan-instance}/api/rest/{guid}
        #     * For a WAF record: http://{waf-root}/{file-name}
        #     * For a CSW record: http://{csw-server}/?Request=GetElementById&Id={guid}&...

        # :param harvest_object_id: HarvestObject id
        # :returns: A string with the URL to the original document
        # '''
        # # Delegate
        # return self._csw.get_original_url(harvest_object_id)

        # obj = model.Session.query(HarvestObject).\
        #                     filter(HarvestObject.id==harvest_object_id).\
        #                     first()
        # if not obj:
        #     return None

        # return obj.source.url

    # overriding waiting for merge #258
    # From parent CSWHarvester
    # def gather_stage(self, harvest_job):
        # '''
        # The gather stage will receive a HarvestJob object and will be
        # responsible for:
        #     - gathering all the necessary objects to fetch on a later.
        #       stage (e.g. for a CSW server, perform a GetRecords request)
        #     - creating the necessary HarvestObjects in the database, specifying
        #       the guid and a reference to its job. The HarvestObjects need a
        #       reference date with the last modified date for the resource, this
        #       may need to be set in a different stage depending on the type of
        #       source.
        #     - creating and storing any suitable HarvestGatherErrors that may
        #       occur.
        #     - returning a list with all the ids of the created HarvestObjects.
        #     - to abort the harvest, create a HarvestGatherError and raise an
        #       exception. Any created HarvestObjects will be deleted.

        # :param harvest_job: HarvestJob object
        # :returns: A list of HarvestObject ids
        # '''

        # #TODO ########################################################################
        # # be sure to reload config
        # self._set_source_config(harvest_job.source.config)
        # #########################################################################

        # return self._csw.gather_stage(harvest_job)
        
    # overriding waiting for merge #258
    # From parent CSWHarvester
    def fetch_stage(self,harvest_object):
        '''
        The fetch stage will receive a HarvestObject object and will be
        responsible for:
            - getting the contents of the remote object (e.g. for a CSW server,
              perform a GetRecordById request).
            - saving the content in the provided HarvestObject.
            - creating and storing any suitable HarvestObjectErrors that may
              occur.
            - returning True if everything is ok (ie the object should now be
              imported), "unchanged" if the object didn't need harvesting after
              all (ie no error, but don't continue to import stage) or False if
              there were errors.

        :param harvest_object: HarvestObject object
        :returns: True if successful, 'unchanged' if nothing to import after
                  all, False if not successful
        '''

        # Check harvest object status
        status = self._get_object_extra(harvest_object, 'status')

        if status == 'delete':
            # No need to fetch anything, just pass to the import stage
            return True

        log = logging.getLogger(__name__ + '.CSW.fetch')
        log.debug('CswHarvester fetch_stage for object: %s', harvest_object.id)

        url = harvest_object.source.url
        try:
            self._setup_csw_client(url)
        except Exception as e:
            self._save_object_error('Error contacting the CSW server: %s' % e,
                                    harvest_object)
            return False
        #TODO ########################################################################
        # load config
        self._set_source_config(harvest_object.source.config)
        # get output_schema from config
        namespace = self.source_config.get('output_schema',self.output_schema())
        identifier = harvest_object.guid
        try:
            record = self.csw.getrecordbyid([identifier], outputschema=namespace)
        except Exception as e:
            self._save_object_error('Error getting the CSW record with GUID %s' % identifier, harvest_object)
            return False
        ##########################################################################

        if record is None:
            self._save_object_error('Empty record for GUID %s' % identifier,
                                    harvest_object)
            return False

        try:
            # Save the fetch contents in the HarvestObject
            # Contents come from csw_client already declared and encoded as utf-8
            # Remove original XML declaration
            content = re.sub('<\?xml(.*)\?>', '', record['xml'])

            harvest_object.content = content.strip()
            harvest_object.save()
        except Exception as e:
            self._save_object_error('Error saving the harvest object for GUID %s [%r]' % \
                                    (identifier, e), harvest_object)
            return False

        log.debug('XML content saved (len %s)', len(record['xml']))
        return True

    # From parent SpatialHarvester
    def import_stage(self, harvest_object):
        '''
        The import stage will receive a HarvestObject object and will be
        responsible for:
            - performing any necessary action with the fetched object (e.g.
              create, update or delete a CKAN package).
              Note: if this stage creates or updates a package, a reference
              to the package should be added to the HarvestObject.
            - setting the HarvestObject.package (if there is one)
            - setting the HarvestObject.current for this harvest:
               - True if successfully created/updated
               - False if successfully deleted
            - setting HarvestObject.current to False for previous harvest
              objects of this harvest source if the action was successful.
            - creating and storing any suitable HarvestObjectErrors that may
              occur.
            - creating the HarvestObject - Package relation (if necessary)
            - returning True if the action was done, "unchanged" if the object
              didn't need harvesting after all or False if there were errors.

        NB You can run this stage repeatedly using 'paster harvest import'.

        :param harvest_object: HarvestObject object
        :returns: True if the action was done, "unchanged" if the object didn't
                  need harvesting after all or False if there were errors.
        '''

        log = logging.getLogger(__name__ + '.import')
        log.debug('Import stage for harvest object: %s', harvest_object.id)

        # check arguments
        if not harvest_object:
            log.error('No harvest object received')
            return False
        elif harvest_object.content is None:
            self._save_object_error('Empty content for object {0}'.format(harvest_object.id), harvest_object, 'Import')
            return False


        # read configuration
        self._set_source_config(harvest_object.source.config)

        # prepare context
        context = {
            'model': model,
            'session': model.Session,
            'user': self._get_user_name(),
            # Tunnelled to pass to spatial_plugin
            'config': dict(self.source_config)
        }

        # Flag previous object as not current anymore
        # Get the last harvested object (if any)
        previous_object = model.Session.query(HarvestObject) \
                            .filter(HarvestObject.guid==harvest_object.guid) \
                            .filter(HarvestObject.current==True) \
                            .first()
        if previous_object and not self.force_import:
            previous_object.current = False
            previous_object.add()

        ##############################################

        # evaluate the new status
        if self.force_import:
            status = 'change'
        else:
            status = self._get_object_extra(harvest_object, 'status')

        if status == 'delete':
            return self._delete(context, harvest_object)

        ###################
        # TODO guess the 'right' ISpatialHarvester
        
        # Validate ISO document
        is_valid, _status, _plugin, _validator = self._validate(harvest_object)
        if not is_valid:
            # If validation errors were found, import will stop unless
            # harvester validation flag says otherwise
            # TODO better policy, based on cumulated _status
            #  a boolean can't express too much,
            #  we should be able to ask
            if not self.source_config.get('continue_on_validation_errors') \
                    and \
                    not p.toolkit.asbool(config.get('ckanext.spatial.harvest.continue_on_validation_errors', False)):
                return False
        # Build the package dict    
        package_dict = None
        if not _plugin:
            # if not spatial_plugins:
            log.error('unable to guess the format using validator, '+\
                'fallback to default iso19139 implementation')

            csw_harvester = p.get_plugin('csw_harvester')
            
            # fallback to default parent implementation
                # TODO rise a ticket: unable to extend CSWHarvester
                # super.get_package_dict(iso_values, harvest_object)
                # overlaps but not implements ISpatialHarvester method
                # harvester.get_package_dict(context, {
                #     'package_dict': package_dict,
                #     'iso_values': parsed_values,
                #     'xml_tree': parsed_values.xml_tree,
                #     'harvest_object': harvest_object,
                # })

            if csw_harvester:
                # Parse ISO document
                try:
                    from ckanext.spatial.model import ISODocument
                    iso_parser = ISODocument(harvest_object.content)
                    parsed_values = iso_parser.read_values()
                except Exception as e:
                    self._save_object_error('Error parsing ISO document for object {0}: {1}'.format(harvest_object.id, six.text_type(e)),
                                            harvest_object, 'Import')
                    return False

                package_dict = csw_harvester.get_package_dict(parsed_values, harvest_object)
        else:
            # a plugin has been found and used to parse
            # let's use that implementation to provide a package

            # Parse ISO document
            # TODO use _status and policy to understand which parser to use
            # this may require an interface method from ISpatialHarvester
            try:
                parser = ISO19115Document(harvest_object.content)
                parsed_values = parser.read_values()
            except Exception as e:
                self._save_object_error('Error parsing ISO document for object {0}: {1}'.format(harvest_object.id, six.text_type(e)),
                                        harvest_object, 'Import')
                return False
            
            package_dict = _plugin.get_package_dict(context, {
                'package_dict': package_dict,
                'iso_values': parsed_values,
                # TODO ticket
                # should be passed by base parser.read_values()
                # but it's not there...
                'xml_tree': parsed_values.get('xml_tree',etree.fromstring(harvest_object.content)),
                'harvest_object': harvest_object,
            })

        if not package_dict:
            log.error('No package dict returned, aborting import for object {0}'.format(harvest_object.id))
            return False
        

        ###################

        # Update GUID with the one on the document
        iso_guid = parsed_values.get('guid')
        self._set_guid(harvest_object, iso_guid)
        
        # Get document modified date
        metadata_date = parsed_values.get('metadata-date')
        if metadata_date:
            import dateutil
            try:
                harvest_object.metadata_modified_date = dateutil.parser.parse(metadata_date, ignoretz=True)
            except ValueError:
                self._save_object_error('Could not extract reference date for object {0} ({1})'
                            .format(harvest_object.id, parsed_values['metadata-date']), harvest_object, 'Import')
                return False
        else:
            import datetime
            #TODO log warn!
            harvest_object.metadata_modified_date = datetime.datetime.today()

        
        # TODO doublecheck when to .add()
        # Flag this object as the current one
        harvest_object.current = True
        harvest_object.add()
        ###################

        # The default package schema does not like Upper case tags
        tag_schema = logic.schema.default_tags_schema()
        tag_schema['name'] = [not_empty, six.text_type]
        package_schema = logic.schema.default_create_package_schema()
        package_schema['tags'] = tag_schema
        context['schema'] = package_schema

        try:
            if status == 'new':
                self._new(context, log, harvest_object, package_schema, package_dict)

            elif status == 'change':
                # Check if the modified date is more recent
                if not self.force_import \
                        and previous_object and \
                        harvest_object.metadata_modified_date <= previous_object.metadata_modified_date:
                    
                    # Assign the previous job id to the new object to
                    # avoid losing history
                    harvest_object.harvest_job_id = previous_object.job.id
                    harvest_object.add()
                    # Delete the previous object to avoid cluttering the object table
                    previous_object.delete()

                    self._change(context, log, harvest_object, package_schema, package_dict)
                else:
                    
                    package_dict['id'] = harvest_object.package_id

                    package_id = p.toolkit.get_action('package_update')(context, package_dict)
                    log.info('Updated package %s with guid %s', package_id, harvest_object.guid)

        except p.toolkit.ValidationError as e:
            self._save_object_error('Validation Error: %s' % six.text_type(e.error_summary), harvest_object, 'Import')
            return False 

        model.Session.commit()

        return True

    
    def _set_guid(self, harvest_object, iso_guid):
        import uuid
        import hashlib
        if iso_guid and harvest_object.guid != iso_guid:
            # First make sure there already aren't current objects
            # with the same guid
            existing_object = model.Session.query(HarvestObject.id) \
                            .filter(HarvestObject.guid==iso_guid) \
                            .filter(HarvestObject.current==True) \
                            .first()
            if existing_object:
                self._save_object_error('Object {0} already has this guid {1}'.format(existing_object.id, iso_guid),
                        harvest_object, 'Import')
                return False

            harvest_object.guid = iso_guid
            harvest_object.add()

        # Generate GUID if not present (i.e. it's a manual import)
        if not harvest_object.guid:
            m = hashlib.md5()
            m.update(harvest_object.content.encode('utf8', 'ignore'))
            harvest_object.guid = m.hexdigest()
            harvest_object.add() #????

    def _validate(self, harvest_object):
        '''
            :returns: [True|False] status plugin_name
            if True some validator has passed (first win)
             in that case also the plugin is passed
             (True, status[plugin_name]['errors'], plugin, validator)
            if False the plugin name is false and a report 
             can be located under:
             status[plugin_name]['errors']
        '''
        # Add any custom validators from extensions
        is_valid = False
        status = {}
        for plugin in p.PluginImplementations(ISpatialHarvester):
            
            # TODO priority / preferences / order (let's define harvester options to use into get_validators())?
            for validator in plugin.get_validators():
                # TODO this assume document as xml, we can do better... (using csw outputformat)
                _errors=[]
                try:
                    # TODO
                    # report:
                    #   File "/srv/app/src_extensions/ckanext-spatial/ckanext/spatial/harvesters/base.py", line 827, in _validate_document
                    #     valid, profile, errors = validator.is_valid(xml)
                    #     ValueError: need more than 2 values to unpack
                    # is_valid, _profile, _errors = self._validate_document(harvest_object.content, harvest_object, validator)
                    # is_valid interface is also specifying an different tuple:
                    # class XsdValidator(BaseValidator):
                    # '''Base class for validators that use an XSD schema.'''
                    # @classmethod
                    # def _is_valid(cls, xml, xsd_filepath, xsd_name):                
                    # Returns:
                    #   (is_valid, [(error_message_string, error_line_number)])
                    # which instead (as is currently used) should be:
                    #   (is_valid, [(error_line_number, error_message_string)])

                    # if csw outputformat application/xml
                    
                    document_string = re.sub('<\?xml(.*)\?>', '', harvest_object.content)
                    try:
                        _xml = etree.fromstring(document_string)
                    except etree.XMLSyntaxError as e:
                        self._save_object_error('Could not parse XML file: {0}'.format(six.text_type(e)), harvest_object, 'Import')
                        return False, None, []

                    is_valid, _errors = validator.is_valid(_xml)
                except Exception as e:
                    is_valid = False
                    _errors.insert(0, ('{0} Validation Error'.format(str(e)), e))

                plugin_name = plugin.name# or plugin.__class__.__name__

                # accumulate errors by (profile and plugin)
                status.update({plugin_name:{'status':is_valid, 'validator':validator.name, 'errors':_errors}})
                
                # The first win, order policy matter!
                if is_valid:
                    return is_valid, status, plugin, validator
                    
                # continue iterating to guess the right profile

        return is_valid, status, None, None

    def _delete(self, log, context, harvest_object):
        # Delete package
        context.update({
            'ignore_auth': True,
        })
        p.toolkit.get_action('package_delete')(context, {'id': harvest_object.package_id})
        log.info('Deleted package {0} with guid {1}'.format(harvest_object.package_id, harvest_object.guid))
        return True

    def _change(self, context, log, harvest_object, package_schema, package_dict):


        # Reindex the corresponding package to update the reference to the
        # harvest object
        if ((config.get('ckanext.spatial.harvest.reindex_unchanged', True) != 'False'
            or self.source_config.get('reindex_unchanged') != 'False')
            and harvest_object.package_id):
            context.update({'validate': False, 'ignore_auth': True})
            try:
                package_dict = logic.get_action('package_show')(context,
                    {'id': harvest_object.package_id})
            except p.toolkit.ObjectNotFound:
                # TODO LOG?!?!
                pass
            else:
                for extra in package_dict.get('extras', []):
                    if extra['key'] == 'harvest_object_id':
                        extra['value'] = harvest_object.id
                if package_dict:
                    from ckan.lib.search.index import PackageSearchIndex
                    PackageSearchIndex().index_package(package_dict)

        log.info('Document with GUID %s unchanged, skipping...' % (harvest_object.guid))
        
    def _new(self, context, log, harvest_object, package_schema, package_dict):

        # We need to explicitly provide a package ID, otherwise ckanext-spatial
        # won't be be able to link the extent to the package.
        import uuid
        package_dict['id'] = six.text_type(uuid.uuid4())
        package_schema['id'] = [six.text_type]

        # Save reference to the package on the object
        harvest_object.package_id = package_dict['id']
        harvest_object.add()
        # Defer constraints and flush so the dataset can be indexed with
        # the harvest object id (on the after_show hook from the harvester
        # plugin)
        model.Session.execute('SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED')
        model.Session.flush()
        
        package_id = p.toolkit.get_action('package_create')(context, package_dict)
        log.info('Created new package %s with guid %s', package_id, harvest_object.guid)
    

