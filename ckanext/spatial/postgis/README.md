PostGIS is no longer required, extents are not stored in a table with a geometry column
anymore by default. This modules are kept here for backwards compatibility only, and will
be removed in future versions.

Users that need to keep storing dataset extents in PostGIS for some reason can re-enable
this behaviour by setting the `ckan.spatial.use_postgis=True` configuration option.
Again, this feature will be dropped in future versions.
