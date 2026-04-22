import pandas as pd
from sqlalchemy import create_engine

# Keep your actual password here!
DB_URI = "postgresql://postgres:yourpassword@localhost:5432/agce_db"
engine = create_engine(DB_URI)

print("Searching PostGIS for valid Arizona Minerals anchor wells...")

try:
    # ILIKE makes the search case-insensitive, looking for anything containing 'ARIZONA MINERALS'
    query = """
    SELECT registry_id, owner_name, well_type, water_level 
    FROM adwr_wells_raw 
    WHERE owner_name ILIKE '%%ARIZONA MINERALS%%' and registry_id ILIKE '2%%'
    LIMIT 25;
    """
    
    anchor_df = pd.read_sql(query, engine)

    if len(anchor_df) == 0:
        print("\n🚨 No wells found for Arizona Minerals! We may need to search by a different company name (e.g., SOUTH32).")
    else:
        print("\n✅ FOUND VALID ANCHOR WELLS:")
        print(anchor_df)
        print("\nPick one of these registry_ids to use in your extraction script!")
        
except Exception as e:
    print(f"Query failed: {e}")