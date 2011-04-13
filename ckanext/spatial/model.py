from ckan.model import Session

DEFAULT_SRID = 4258

def setup(srid=4258):

    if not srid:
        srid = DEFAULT_SRID
    srid = str(srid)

    connection = Session.connection()
    connection.execute("""CREATE TABLE package_extent(
                            package_id text PRIMARY KEY
                       );""")

    #connection.execute('ALTER TABLE package_extent OWNER TO ?',user_name);

    connection.execute('SELECT AddGeometryColumn(\'package_extent\',\'the_geom\', %s, \'POLYGON\', 2)',srid)

    Session.commit()
