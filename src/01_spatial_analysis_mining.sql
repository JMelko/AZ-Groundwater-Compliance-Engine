/*
===============================================================================
Script: 01_spatial_analysis_mining.sql
Purpose: Simulates a spatial proximity analysis for a 3-mile impact zone 
         around a primary extraction well (Arizona Minerals, Registry 227120).
Author: John Melko/@JMelko

DISCLAIMER: This project and its associated data pipelines are constructed 
strictly for educational and portfolio demonstration purposes. The spatial 
analyses, buffer zones, and calculated proximity metrics are simulated. They 
do not represent official regulatory findings, professional engineering reports, 
or the actual hydrological impacts of any specific mining operations.
===============================================================================
*/

-- Step 1: Isolate the anchor well and project it to NAD83 / Arizona Central (EPSG:2868)
WITH AnchorWell AS (
    SELECT 
        registry_id,
        owner_name,
        ST_Transform(geom, 2868) AS proj_geom
    FROM adwr_wells_raw
    WHERE registry_id = '227120'
),

-- Step 2: Create a 3-mile (15,840 ft) impact buffer around the anchor well
ImpactZone AS (
    SELECT 
        registry_id AS anchor_id,
        ST_Buffer(proj_geom, 15840) AS buffer_geom,
        proj_geom AS anchor_geom
    FROM AnchorWell
)

-- Step 3: Find all intersecting wells, calculate exact distance, and return results
SELECT 
    w.registry_id AS impacted_well_id,
    w.owner_name,
    w.well_type,
    w.water_depth,
    ROUND(
        ST_Distance(
            ST_Transform(w.geom, 2868), 
            iz.anchor_geom
        )::numeric, 2
    ) AS distance_to_anchor_ft,
    w.geom 
FROM adwr_wells_raw w
CROSS JOIN ImpactZone iz
WHERE ST_DWithin(
    ST_Transform(w.geom, 2868), 
    iz.anchor_geom, 
    15840
)
AND w.registry_id != '227120'
ORDER BY distance_to_anchor_ft ASC;