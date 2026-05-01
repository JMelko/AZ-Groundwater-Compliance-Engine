import duckdb

def create_spatial_geometries():
    print("Connecting to PostGIS engine via DuckDB...")
    con = duckdb.connect()
    con.execute("INSTALL postgres;")
    con.execute("LOAD postgres;")
    
    # Connect to your Docker container
    pg_conn_str = "dbname=agce_db user=postgres password=yourpassword host=localhost port=5432"
    con.execute(f"ATTACH '{pg_conn_str}' AS pg_db (TYPE postgres);")

    print("Executing PostGIS Spatial Transformation...")
    
    # We must use CALL postgres_execute() to pass native PostgreSQL commands 
    # directly to the container so DuckDB doesn't try to parse them.

    # 1. Enable the PostGIS extension
    con.execute("CALL postgres_execute('pg_db', 'CREATE EXTENSION IF NOT EXISTS postgis;');")
    
    # 2. Add a new Geometry column (Point, EPSG: 26912 for AZ UTM Zone 12N)
    # Notice we drop 'pg_db.' from the table name because this command runs natively inside Postgres
    con.execute("CALL postgres_execute('pg_db', 'ALTER TABLE adwr.wells55 ADD COLUMN IF NOT EXISTS geom geometry(Point, 26912);');")

    # 3. Populate the geometry column using the X and Y coordinates
    print("Fusing X and Y coordinates into spatial objects...")
    con.execute("""
        CALL postgres_execute('pg_db', '
            UPDATE adwr.wells55 
            SET geom = ST_SetSRID(ST_MakePoint(utm_x_meters, utm_y_meters), 26912)
            WHERE utm_x_meters IS NOT NULL AND utm_y_meters IS NOT NULL;
        ');
    """)

    # 4. Create a Spatial Index
    print("Building spatial index for fast QGIS rendering...")
    con.execute("""
        CALL postgres_execute('pg_db', '
            CREATE INDEX IF NOT EXISTS idx_wells55_geom 
            ON adwr.wells55 USING GIST (geom);
        ');
    """)

    print("Success! Your well data is now a fully functional spatial layer.")

if __name__ == "__main__":
    create_spatial_geometries()