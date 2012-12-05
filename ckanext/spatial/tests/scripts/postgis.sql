-------------------------------------------------------------------
--  WARNING: This is probably NOT the file you are looking for.
--  This file is intended to be used only during tests, you won't
--  get a functional PostGIS database executing it. Please install
--  PostGIS as described in the README.
-------------------------------------------------------------------

-------------------------------------------------------------------
-- SPATIAL_REF_SYS
-------------------------------------------------------------------
CREATE TABLE spatial_ref_sys (
	 srid integer not null primary key,
	 auth_name varchar(256),
	 auth_srid integer,
	 srtext varchar(2048),
	 proj4text varchar(2048)
);

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

---
--- EPSG 4326 : WGS 84
---
INSERT INTO "spatial_ref_sys" ("srid","auth_name","auth_srid","srtext","proj4text") VALUES (4326,'EPSG',4326,'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ');

