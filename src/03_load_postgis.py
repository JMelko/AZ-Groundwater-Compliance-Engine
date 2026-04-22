import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def load_parquet_to_postgis(parquet_path, db_uri, table_name):
    if not os.path.exists(parquet_path):
        logging.error("Clean Parquet file not found. Run DuckDB preprocessing first.")
        return

    logging.info(f"Reading clean data from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    
    # We explicitly tell GeoPandas to use the UTM columns you extracted
    logging.info("Creating spatial geometries from UTM coordinates...")
    gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.utm_x, df.utm_y),
        crs="EPSG:26912" # ADWR standard UTM Zone 12N (NAD83)
    )
    
    logging.info(f"Pushing {len(gdf)} records to PostGIS table: {table_name}...")
    engine = create_engine(db_uri)
    
    # if_exists='replace' ensures idempotency (safe to rerun)
    try:
        gdf.to_postgis(table_name, engine, if_exists='replace', index=False)
        logging.info("Data load complete. Table is ready for spatial SQL.")
    except Exception as e:
        logging.error(f"Database upload failed: {e}")

if __name__ == "__main__":
    PARQUET_FILE = "data/processed/clean_adwr_wells.parquet"
    
    # Standard local Docker PostGIS connection string
    # Verify the password and database name match your Docker configuration
    DB_URI = "postgresql://postgres:yourpassword@localhost:5432/agce_db"
    
    load_parquet_to_postgis(PARQUET_FILE, DB_URI, "adwr_wells_raw")