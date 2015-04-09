-------------------------------------------------------------------
--  WARNING: This is probably NOT the file you are looking for.
--  This file is intended to be used only during tests, you won't
--  get a functional PostGIS database executing it. Please install
--  PostGIS as described in the README.
-------------------------------------------------------------------

-------------------------------------------------------------------
-- GEOMETRY_COLUMNS
-------------------------------------------------------------------
CREATE TABLE geometry_columns (
	f_table_catalog varchar(256) not null,
	f_table_schema varchar(256) not null,
	f_table_name varchar(256) not null,
	f_geometry_column varchar(256) not null,
	coord_dimension integer not null,
	srid integer not null,
	type varchar(30) not null,
	CONSTRAINT geometry_columns_pk primary key (
		f_table_catalog,
		f_table_schema,
		f_table_name,
		f_geometry_column )
) WITH OIDS;

