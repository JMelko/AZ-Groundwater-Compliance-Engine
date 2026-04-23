import pandas as pd
import os

def clean_adwr_wells(input_path, output_path):
    print(f"Loading raw data from: {input_path}...")
    
    # 1. Read the raw CSV file
    # Using low_memory=False because ADWR files have mixed data types in columns
    try:
        df = pd.read_csv(input_path, low_memory=False)
    except FileNotFoundError:
        print("Error: Could not find the raw CSV. Check the filename and path.")
        return

    # 2. Define the exact columns we care about for compliance and spatial mapping
    # Note: Verify these exact header names match your downloaded CSV
    columns_to_keep = [
        'Registry ID', 
        'Well Type', 
        'Well Depth', 
        'Water Level', 
        'UTM X Meters', 
        'UTM Y Meters', 
        'Owner Name'
    ]

    # Verify columns exist before filtering to avoid script crashes
    missing_cols = [col for col in columns_to_keep if col not in df.columns]
    if missing_cols:
         print(f"Warning: The following columns are missing in the raw data: {missing_cols}")
         print("Available columns are:", df.columns.tolist()[:10], "... check exact spelling.")
         return

    # Filter the dataframe to only our desired columns
    df = df[columns_to_keep]

    # 3. Data Cleaning & Transformation
    print("Cleaning data...")
    
    # Standardize column headers to snake_case for SQL database compatibility
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Drop any rows where we don't have spatial coordinates (UTM X or UTM Y)
    # A well we can't map is a well we can't run spatial compliance on.
    df = df.dropna(subset=['utm_x_meters', 'utm_y_meters'])

    # Standardize Owner Names (uppercase, strip trailing/leading spaces)
    # This prevents "PHELPS DODGE" and "phelps dodge  " from being treated as different entities
    df['owner_name'] = df['owner_name'].str.upper().str.strip()

    # 4. Save the cleaned data
    print(f"Saving cleaned dataset to: {output_path}...")
    df.to_csv(output_path, index=False)
    
    print(f"Success! Reduced dataset to {len(df)} mappable wells.")

if __name__ == "__main__":
    # Define relative paths (assuming script is run from the project root)
    RAW_DATA = 'data/raw/adwr_wells.csv' 
    PROCESSED_DATA = 'data/processed/clean_wells55.csv'
    
    clean_adwr_wells(RAW_DATA, PROCESSED_DATA)