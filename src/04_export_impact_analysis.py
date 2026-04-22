import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def export_tableau_data(db_uri, output_csv_path):
    logging.info("Connecting to PostGIS database...")
    engine = create_engine(db_uri)

    # The exact spatial SQL we tested in QGIS, customized for Tableau export
    query = """
    WITH AnchorWell AS (
        SELECT registry_id, owner_name, ST_Transform(geometry, 2868) AS proj_geom
        FROM adwr_wells_raw
        WHERE registry_id = '227120'
    ),
    ImpactZone AS (
        SELECT registry_id AS anchor_id, ST_Buffer(proj_geom, 15840) AS buffer_geom, proj_geom AS anchor_geom
        FROM AnchorWell
    )
    SELECT 
        w.registry_id AS impacted_well_id,
        w.owner_name,
        w.well_type,
        w.water_level,  -- Updated to match your DuckDB fix!
        ROUND(ST_Distance(ST_Transform(w.geometry, 2868), iz.anchor_geom)::numeric, 2) AS distance_to_anchor_ft,
        ST_Y(ST_Transform(w.geometry, 4326)) AS latitude,
        ST_X(ST_Transform(w.geometry, 4326)) AS longitude
    FROM adwr_wells_raw w
    CROSS JOIN ImpactZone iz
    WHERE ST_DWithin(ST_Transform(w.geometry, 2868), iz.anchor_geom, 15840)
    AND w.registry_id != '227120'
    ORDER BY distance_to_anchor_ft ASC;
    """

    try:
        logging.info("Executing 3-mile spatial buffer analysis for Arizona Minerals...")
        # Pandas pushes the SQL to the database and reads the result natively
        df = pd.read_sql(query, engine)
        logging.info(f"Analysis complete. Found {len(df)} impacted wells in the 3-mile zone.")
        
        # Save to a flat file for Tableau
        df.to_csv(output_csv_path, index=False)
        logging.info(f"Data exported successfully to: {output_csv_path}")
        
    except Exception as e:
        logging.error(f"Extraction failed: {e}")

if __name__ == "__main__":
    # Standard local Docker PostGIS connection string
    DB_URI = "postgresql://postgres:yourpassword@localhost:5432/agce_db"
    OUTPUT_CSV = "data/processed/impacted_wells_arizona_minerals.csv"
    
    export_tableau_data(DB_URI, OUTPUT_CSV)