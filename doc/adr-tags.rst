==============================================
Architectural Decision Record for tags schema
==============================================

Summary
#######

Allow the default CKAN tag schema to be used rather than the loose spatial schema when a CKAN config setting is set.

Problem
#######

It appears that in the schema for tags was eased for gemini sources which means if there are tags ingested into the database there is a chance that some of them would not meet the default CKAN tag schema. 

This causes an issue when a user attempts to add a resource to a resource which has an invalid tag, as this would cause an internal server error as there is an tag which doesn't meet the default CKAN tag schema and it doesn't attempt to validate against the loose tag schema. So an attempt to add a resource to a dataset which is linked to invalid tag fails.

As the spatial tag schema is very loose, only needing the tag to be in unicode, there is a whole range of tags attached to datasets including tags which are cut off, newlines in tags or invalid encodings and tags with other symbols.

Statistics
##########

Running a script on the 17/6/20 to extract the number of affected datasets with invalid tags on the data.gov.uk CKAN database reveals that there are 0.23% tags in the system which would be invalid under the default CKAN tag schema affecting 5.1% datasets that have tags or 1.27% of all datasets. 

The most impacted tag is 

    Area management/restriction/regulation zones and r

affecting 1.77% datasets with tags or 0.44% of all datasets.

Proposal
########

Rather than attempting to fix the internal server in CKAN I am proposing to default to the default CKAN tag schema. This will be done in a number of steps

- Add a config setting which will allow CKAN administrators to use the default tag schema and ensure that tag validation errors are visible to users in their harvest logs so that they can correct tags at the harvest source. The config setting will also make it easier to merge upstream as it won't impact other CKAN stacks.

- Existing invalid tags with datasets using the tags will be exported to a file in case the tags need to be restored.

- Invalid tags will be removed from the database thereby allowing adding of new resources to datasets which previously had invalid tags attached.

Other proposals
###############

1. Rather than setting the tag schema to the CKAN default tag schema we could find the source of the Internal error and fix it and continue to ignore tags which do not conform to the CKAN default tag schema. 

- This may need some time to fix as it may be difficult to work out which extension is raising the error which may mean also fixing those and there may be other consequences from fixing the internal server error.

2. Update the code to validate against the loose spatial schema. Whilst this is an option it would mean substantial rewrite of parts of the CKAN core code, spatial, harvest and datagovuk extension code. As there are only 0.23% invalid tags affecting around 1.27% datasets the effort to fix this would be disproportionate to the benefits.

Impact
######

The impact of this will be that invalid tags will be removed so the display of tags will be clearer and no longer available to users on CKAN publishing website to select when filtering search results.

For publishers there will be a number of additional harvest errors to warn them of tags being invalid when previously all tags which only met the criteria of being unicode were allowed through, the datasets will still be published through to data.gov.uk despite the warnings.
