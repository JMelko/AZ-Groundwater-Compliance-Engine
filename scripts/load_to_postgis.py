import duckdb

def load_data_to_postgres(csv_path):
    print("Starting DuckDB engine...")
    # Connect to an in-memory DuckDB instance
    con = duckdb.connect()

    print("Installing and loading Postgres extension...")
    # DuckDB needs this extension to talk directly to your Docker container
    con.execute("INSTALL postgres;")
    con.execute("LOAD postgres;")

    print("Attaching PostgreSQL database...")
    # This connection string matches your docker-compose.yml credentials
    pg_conn_str = "dbname=agce_db user=postgres password=yourpassword host=localhost port=5432"
    
    # Attach the database and name it 'pg_db'
    con.execute(f"ATTACH '{pg_conn_str}' AS pg_db (TYPE postgres);")

    print(f"Reading {csv_path} and loading into PostgreSQL...")
    
    # 1. Create a dedicated schema for state data to keep things organized
    con.execute("CREATE SCHEMA IF NOT EXISTS pg_db.adwr;")
    
    # 2. Drop the table if it already exists (useful if you run this script multiple times)
    con.execute("DROP TABLE IF EXISTS pg_db.adwr.wells55;")

    # 3. Read the CSV and instantly create/populate the Postgres table
    # read_csv_auto tells DuckDB to automatically guess the data types (integers, floats, text)
    con.execute(f"""
        CREATE TABLE pg_db.adwr.wells55 AS 
        SELECT * FROM read_csv_auto('{csv_path}');
    """)

    print("Success! Data successfully added into PostgreSQL.")

if __name__ == "__main__":
    # Point this to the clean file we generated in the last step
    PROCESSED_DATA = 'data/processed/clean_wells55.csv'
    
    try:
        load_data_to_postgres(PROCESSED_DATA)
    except Exception as e:
        print(f"An error occurred: {e}")