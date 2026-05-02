# Arizona Groundwater Compliance Engine (AGCE)

**Live Dashboard:** [\[https://public.tableau.com/views/agce/Sheet1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link\]]


## Project Overview
The Arizona Groundwater Compliance Engine (AGCE) is an automated spatial data pipeline designed to streamline environmental regulatory analysis. Traditional environmental consulting workflows often rely on manual geoprocessing in desktop GIS software, which is slow, difficult to reproduce, and creates data silos. 

This project solves that bottleneck by containerizing the spatial math. By leveraging a custom ETL pipeline, the AGCE automatically ingests massive state compliance datasets, translates raw coordinates into indexed PostGIS geometries, and executes high-speed spatial queries (e.g., 5-mile impact radius analysis) natively within the database. The final output is automatically staged for a live, interactive visualization dashboard.

## Architecture & Tech Stack
* **Infrastructure:** Docker, PostgreSQL
* **Spatial Engine:** PostGIS (EPSG: 26912 / UTM Zone 12N)
* **ETL Pipeline:** Python, Pandas, DuckDB
* **Data Visualization:** Tableau Public

## Methodology
1. **Extraction & Cleaning:** `clean_wells.py` uses Pandas to process the raw ADWR Wells55 Registry, standardizing headers to `snake_case` and filtering for valid spatial coordinates.
2. **High-Speed Ingestion:** `load_to_postgis.py` bypasses traditional row-by-row loading. It utilizes DuckDB as an in-memory bridge to infer schema types and blast the cleaned CSV directly into the localized Docker container.
3. **Spatial Transformation:** `make_spatial.py` executes native PostGIS commands to fuse raw UTM coordinates into `Geometry` objects and builds a Generalized Search Tree (`GIST`) index for millisecond rendering.
4. **Optimized Spatial Analysis (Push-Down):** `export_for_tableau.py` performs a live `ST_DWithin` spatial query to identify compliance wells within an exact 5-mile radius of a target coordinate. The script uses DuckDB to push the query down to the PostGIS engine, leveraging the spatial index for extreme performance, before exporting the final localized dataset for visualization.

## How to Run Locally
To reproduce this pipeline on your local machine:

1. **Clone the repository and activate the environment:**
   ```bash
   git clone [https://github.com/YourUsername/AZ-Groundwater-Compliance-Engine.git](https://github.com/YourUsername/AZ-Groundwater-Compliance-Engine.git)
   cd AZ-Groundwater-Compliance-Engine
   python -m venv venv
   source venv/Scripts/activate  # Or source venv/bin/activate on Mac/Linux
   pip install -r requirements.txt

2. **Start the localized database engine:** 
    docker compose up -d

3. **Execute the pipeline**
    ```bash
    python scripts/clean_wells.py
    python scripts/load_to_postgis.py
    python scripts/make_spatial.py
    python scripts/export_for_tableau.py