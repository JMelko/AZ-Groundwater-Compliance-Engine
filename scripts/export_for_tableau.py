import duckdb

def export_to_csv(output_path):
    print("Connecting to database...")
    con = duckdb.connect()
    
    # We only need the Postgres bridge
    con.execute("INSTALL postgres; LOAD postgres;")
    
    pg_conn_str = "dbname=agce_db user=postgres password=yourpassword host=localhost port=5432"
    con.execute(f"ATTACH '{pg_conn_str}' AS pg_db (TYPE postgres);")

    print("Delegating spatial analysis to PostGIS and exporting to CSV...")
    
    # By wrapping our SQL in postgres_query(), we force the PostGIS engine
    # to do the math using our spatial index. DuckDB just acts as the CSV writer.
    con.execute(f"""
        COPY (
            SELECT * FROM postgres_query('pg_db', '
                SELECT 
                    registry_id, 
                    owner_name, 
                    well_type, 
                    well_depth, 
                    ST_Y(ST_Transform(geom, 4326)) AS latitude,
                    ST_X(ST_Transform(geom, 4326)) AS longitude
                FROM adwr.wells55
                WHERE ST_DWithin(
                    geom, 
                    ST_SetSRID(ST_MakePoint(495000, 3565000), 26912), 
                    8046
                )
            ')
        ) TO '{output_path}' (HEADER, DELIMITER ',');
    """)
    print(f"Success! Portfolio deliverable saved to: {output_path}")

if __name__ == "__main__":
    DESTINATION = 'data/processed/tableau_compliance_data.csv'
    export_to_csv(DESTINATION)