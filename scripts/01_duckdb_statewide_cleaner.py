import duckdb
import pandas as pd
import time
import os

print("🚀 Starting Hybrid ETL Pipeline...")
start_time = time.time()

# 1. Bulletproof Pathing
script_dir = os.path.dirname(os.path.abspath(__file__))
raw_file = os.path.join(script_dir, '..', 'data', 'raw', 'adwr_wells.csv')
processed_file = os.path.join(script_dir, '..', 'data', 'processed', 'clean_statewide_wells.csv')

raw_file = os.path.normpath(raw_file).replace('\\', '/')
processed_file = os.path.normpath(processed_file).replace('\\', '/')

if not os.path.exists(raw_file):
    print(f"❌ Error: Could not find the file at {raw_file}")
    exit()

print("🐼 Step 1: Pandas Ingestion (Forgiving Parser)...")
# We use Pandas to safely read the messy Government CSV. 
# dtype=str forces it to read everything as text first, preventing mixed-type crashes.
df = pd.read_csv(raw_file, low_memory=False, dtype=str)

print("🦆 Step 2: DuckDB SQL Processing...")
con = duckdb.connect(database=':memory:')

# Notice the FROM clause! We are telling DuckDB to run SQL directly on the Pandas 'df' variable.
query = f"""
COPY (
    SELECT
        "Registry ID" AS registry_id,
        "Owner Name" AS owner_name,
        "Well Type" AS well_type,
        "Well Depth" AS well_depth,
        "Water Level" AS water_level,
        "UTM X Meters" AS utm_x,
        "UTM Y Meters" AS utm_y
    FROM df 
    WHERE "UTM X Meters" IS NOT NULL
      AND "UTM Y Meters" IS NOT NULL
      AND "UTM X Meters" != '0'
      AND "UTM Y Meters" != '0'
      AND "UTM X Meters" != ''
) TO '{processed_file}' (HEADER, DELIMITER ',');
"""

try:
    con.execute(query)
    end_time = time.time()
    print(f"✅ Success! Hybrid pipeline processed the state-wide dataset in {round(end_time - start_time, 2)} seconds!")
    print(f"✅ Clean file exported to: {processed_file}")
except Exception as e:
    print(f"❌ Pipeline failed with error:\n{e}")