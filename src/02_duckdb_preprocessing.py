import duckdb
import logging
import os

# Set up logging to track our pipeline's progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def process_adwr_data(raw_csv_path, output_parquet_path):
    if not os.path.exists(raw_csv_path):
        logging.error(f"Cannot find {raw_csv_path}. Please check your data folder.")
        return

    logging.info(f"Connecting to DuckDB and querying {raw_csv_path}...")
    
    con = duckdb.connect(database=':memory:')
    
    # We use DuckDB to read the CSV directly from the hard drive.
    # We filter out any wells missing Latitude/Longitude, as they will break PostGIS.
    query = f"""
        COPY (
            SELECT 
                "Registry ID" AS registry_id,
                "Owner Name" AS owner_name,
                "Well Type" AS well_type,
                TRY_CAST("Well Depth" AS INTEGER) AS well_depth,
                TRY_CAST("Water Level" AS INTEGER) AS water_level,
                "County" AS county,
                TRY_CAST("UTM X Meters" AS DOUBLE) AS utm_x,
                TRY_CAST("UTM Y Meters" AS DOUBLE) AS utm_y
            FROM read_csv_auto('{raw_csv_path}', sample_size=-1, ignore_errors=true)
            WHERE "UTM X Meters" IS NOT NULL 
              AND "UTM Y Meters" IS NOT NULL
        ) TO '{output_parquet_path}' (FORMAT PARQUET);
    """
    
    try:
        con.execute(query)
        logging.info(f"Successfully processed and exported to {output_parquet_path}")
    except Exception as e:
        logging.error(f"DuckDB encountered an error: {e}")

if __name__ == "__main__":
    RAW_DATA = "data/raw/adwr_wells.csv"
    PROCESSED_DATA = "data/processed/clean_adwr_wells.parquet"
    
    process_adwr_data(RAW_DATA, PROCESSED_DATA)